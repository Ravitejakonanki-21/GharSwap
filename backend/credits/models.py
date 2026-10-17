from django.conf import settings
from django.db import models


class CreditLedger(models.Model):
    class Reason(models.TextChoices):
        HOSTED_STAY = "hosted_stay", "Hosted stay"
        STAYED = "stayed", "Stayed"
        SIGNUP_BONUS = "signup_bonus", "Signup bonus"
        ADJUSTMENT = "adjustment", "Adjustment"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credit_entries",
    )
    amount = models.IntegerField(help_text="Positive credits in, negative credits out")
    reason = models.CharField(max_length=32, choices=Reason.choices)
    stay_request = models.ForeignKey(
        "stays.StayRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"{self.user} {sign}{self.amount} ({self.reason})"
