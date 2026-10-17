from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from credits.models import CreditLedger
from credits.services import append_entry
from listings.models import Availability, Listing

User = get_user_model()

DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    help = "Create demo users and listings in Goa and Pondicherry"

    def handle(self, *args, **options):
        anita = self._user(
            "anita.goa@gharswap.demo",
            display_name="Anita D'Souza",
            city="Goa",
            bio="I host a cottage two lanes back from Calangute. Quiet mornings, strong coffee.",
            languages=["English", "Konkani", "Hindi"],
        )
        ravi = self._user(
            "ravi.pondy@gharswap.demo",
            display_name="Ravi Menon",
            city="Pondicherry",
            bio="White Town studio with a bicycle and a French-quarter bakery habit.",
            languages=["English", "Tamil", "French"],
        )
        meera = self._user(
            "meera.guest@gharswap.demo",
            display_name="Meera Shah",
            city="Mumbai",
            bio="Looking to swap a few weekends on the coast.",
            languages=["English", "Hindi", "Gujarati"],
        )
        for user in (anita, ravi, meera):
            if not CreditLedger.objects.filter(
                user=user, reason=CreditLedger.Reason.ADJUSTMENT
            ).exists():
                append_entry(
                    user=user,
                    amount=6,
                    reason=CreditLedger.Reason.ADJUSTMENT,
                )

        goa = self._listing(
            anita,
            title="Calangute cottage with a mango tree",
            description="One bedroom, a shaded verandah, and the beach a 12-minute walk away. "
            "Best for two. Exact street address is shared only after a stay is accepted.",
            city="Goa",
            address_area="Calangute",
            max_guests=2,
            house_rules="No parties. Shoes off at the door. Quiet after 10pm.",
            start=date(2026, 11, 1),
            end=date(2026, 12, 15),
        )
        anjuna = self._listing(
            anita,
            title="Anjuna room near the flea market",
            description="A bright single room in a shared house. Scooter parking, outdoor shower.",
            city="Goa",
            address_area="Anjuna",
            max_guests=1,
            house_rules="Shared kitchen. Bring a lock for the cupboard.",
            start=date(2026, 11, 10),
            end=date(2027, 1, 31),
        )
        pondy = self._listing(
            ravi,
            title="White Town studio above a courtyard",
            description="High ceilings, a writing desk, and the promenade a short walk downhill.",
            city="Pondicherry",
            address_area="White Town",
            max_guests=2,
            house_rules="No smoking indoors. Bicycle is free to use.",
            start=date(2026, 11, 1),
            end=date(2026, 12, 31),
        )
        auro = self._listing(
            ravi,
            title="Auroville-edge room with a garden",
            description="Simple room opening onto a small garden. Good for one guest who likes early walks.",
            city="Pondicherry",
            address_area="Auroville Road",
            max_guests=1,
            house_rules="Vegetarian kitchen. Please refill drinking water.",
            start=date(2026, 12, 1),
            end=date(2027, 2, 28),
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"  Goa host:     {anita.email} / {DEMO_PASSWORD} (listing {goa.id}, {anjuna.id})")
        self.stdout.write(f"  Pondy host:   {ravi.email} / {DEMO_PASSWORD} (listing {pondy.id}, {auro.id})")
        self.stdout.write(f"  Traveler:     {meera.email} / {DEMO_PASSWORD}")

    def _user(self, email, *, display_name, city, bio, languages):
        user, created = User.objects.get_or_create(
            email=email, defaults={"phone": "9990000000"}
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        profile = user.profile
        profile.display_name = display_name
        profile.city = city
        profile.bio = bio
        profile.languages = languages
        profile.save()
        return user

    def _listing(self, host, **kwargs):
        start = kwargs.pop("start")
        end = kwargs.pop("end")
        listing, _ = Listing.objects.get_or_create(
            host=host, title=kwargs["title"], defaults=kwargs
        )
        Availability.objects.get_or_create(
            listing=listing, start_date=start, end_date=end
        )
        return listing
