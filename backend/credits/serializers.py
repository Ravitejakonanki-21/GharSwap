from rest_framework import serializers

from credits.services import available_credits, ledger_balance, reserved_credits

from .models import CreditLedger


class CreditLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditLedger
        fields = ("id", "amount", "reason", "stay_request", "created_at")
        read_only_fields = fields


class CreditBalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField()
    reserved = serializers.IntegerField()
    available = serializers.IntegerField()

    @classmethod
    def from_user(cls, user):
        data = {
            "balance": ledger_balance(user),
            "reserved": reserved_credits(user),
            "available": available_credits(user),
        }
        serializer = cls(data)
        return serializer.data
