from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from credits.models import CreditLedger
from credits.services import append_entry, available_credits
from listings.views import listing_covers_dates, listing_has_accepted_overlap
from safety.services import users_are_blocked

from .models import StayRequest


def validate_dates_and_nights(check_in, check_out, guests_count) -> int:
    nights = (check_out - check_in).days
    if nights < 1:
        raise ValidationError({"check_out": "Stay must be at least one night"})
    if guests_count < 1:
        raise ValidationError({"guests_count": "Must include at least one guest"})
    return nights * guests_count


def create_stay_request(*, guest, listing, check_in, check_out, guests_count, message=""):
    if listing.host_id == guest.id:
        raise ValidationError("You cannot request your own listing")
    if users_are_blocked(guest, listing.host):
        raise ValidationError("You cannot request this listing")
    if not listing.is_active:
        raise ValidationError("This listing is not available")
    if guests_count > listing.max_guests:
        raise ValidationError({"guests_count": "Exceeds listing guest limit"})
    guest_nights = validate_dates_and_nights(check_in, check_out, guests_count)
    if not listing_covers_dates(listing, check_in, check_out):
        raise ValidationError("Listing is not available for these dates")
    if listing_has_accepted_overlap(listing, check_in, check_out):
        raise ValidationError("These dates are already booked")
    if available_credits(guest) < guest_nights:
        raise ValidationError("Insufficient credits for this stay")
    return StayRequest.objects.create(
        guest=guest,
        listing=listing,
        check_in=check_in,
        check_out=check_out,
        guests_count=guests_count,
        message=message,
        status=StayRequest.Status.PENDING,
    )


def _locked_request(pk) -> StayRequest:
    return StayRequest.objects.select_for_update().select_related("listing", "guest").get(pk=pk)


def accept_stay_request(stay: StayRequest, actor):
    with transaction.atomic():
        stay = _locked_request(stay.pk)
        if stay.listing.host_id != actor.id:
            raise PermissionDenied("Only the host can accept this request")
        if stay.status != StayRequest.Status.PENDING:
            raise ValidationError("Only pending requests can be accepted")
        if listing_has_accepted_overlap(stay.listing, stay.check_in, stay.check_out):
            raise ValidationError("Overlapping accepted stay exists for this listing")
        if available_credits(stay.guest) < stay.guest_nights:
            raise ValidationError("Guest does not have enough credits")
        stay.status = StayRequest.Status.ACCEPTED
        stay.save(update_fields=["status", "updated_at"])
        return stay


def decline_stay_request(stay: StayRequest, actor):
    with transaction.atomic():
        stay = _locked_request(stay.pk)
        if stay.listing.host_id != actor.id:
            raise PermissionDenied("Only the host can decline this request")
        if stay.status != StayRequest.Status.PENDING:
            raise ValidationError("Only pending requests can be declined")
        stay.status = StayRequest.Status.DECLINED
        stay.save(update_fields=["status", "updated_at"])
        return stay


def cancel_stay_request(stay: StayRequest, actor):
    with transaction.atomic():
        stay = _locked_request(stay.pk)
        is_host = stay.listing.host_id == actor.id
        is_guest = stay.guest_id == actor.id
        if not (is_host or is_guest):
            raise PermissionDenied("Only participants can cancel this request")
        if stay.status not in {StayRequest.Status.PENDING, StayRequest.Status.ACCEPTED}:
            raise ValidationError("This request can no longer be cancelled")
        stay.status = StayRequest.Status.CANCELLED
        stay.save(update_fields=["status", "updated_at"])
        return stay


def complete_stay_request(stay: StayRequest, actor):
    with transaction.atomic():
        stay = _locked_request(stay.pk)
        is_host = stay.listing.host_id == actor.id
        is_guest = stay.guest_id == actor.id
        if not (is_host or is_guest):
            raise PermissionDenied("Only participants can complete this stay")
        if stay.status != StayRequest.Status.ACCEPTED:
            raise ValidationError("Only accepted stays can be completed")
        if CreditLedger.objects.filter(
            stay_request=stay, reason=CreditLedger.Reason.STAYED
        ).exists():
            raise ValidationError("Credits for this stay were already settled")
        nights = stay.guest_nights
        append_entry(
            user=stay.guest,
            amount=-nights,
            reason=CreditLedger.Reason.STAYED,
            stay_request=stay,
        )
        append_entry(
            user=stay.listing.host,
            amount=nights,
            reason=CreditLedger.Reason.HOSTED_STAY,
            stay_request=stay,
        )
        stay.status = StayRequest.Status.COMPLETED
        stay.save(update_fields=["status", "updated_at"])
        return stay
