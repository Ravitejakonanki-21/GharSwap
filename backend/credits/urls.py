from django.urls import path

from .views import CreditBalanceView, CreditLedgerView

urlpatterns = [
    path("credits/", CreditBalanceView.as_view(), name="credit-balance"),
    path("credits/ledger/", CreditLedgerView.as_view(), name="credit-ledger"),
]
