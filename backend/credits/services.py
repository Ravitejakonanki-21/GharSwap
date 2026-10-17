from django.conf import settings
from django.db.models import Sum

from .models import CreditLedger


def ledger_balance(user) -> int:
    total = CreditLedger.objects.filter(user=user).aggregate(total=Sum("amount"))["total"]
    return int(total or 0)


def reserved_credits(user) -> int:
    from stays.models import StayRequest

    requests = StayRequest.objects.filter(
        guest=user, status=StayRequest.Status.ACCEPTED
    ).only("check_in", "check_out", "guests_count")
    return sum(item.guest_nights for item in requests)


def available_credits(user) -> int:
    return ledger_balance(user) - reserved_credits(user)


def grant_signup_bonus(user) -> CreditLedger | None:
    if CreditLedger.objects.filter(user=user, reason=CreditLedger.Reason.SIGNUP_BONUS).exists():
        return None
    return CreditLedger.objects.create(
        user=user,
        amount=settings.SIGNUP_BONUS_CREDITS,
        reason=CreditLedger.Reason.SIGNUP_BONUS,
    )


def append_entry(*, user, amount: int, reason: str, stay_request=None) -> CreditLedger:
    if amount == 0:
        raise ValueError("Ledger amount cannot be zero")
    return CreditLedger.objects.create(
        user=user,
        amount=amount,
        reason=reason,
        stay_request=stay_request,
    )
