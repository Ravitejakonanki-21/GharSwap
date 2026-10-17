from django.contrib import admin

from .models import CreditLedger


@admin.register(CreditLedger)
class CreditLedgerAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "reason", "stay_request", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__email",)
    readonly_fields = ("user", "amount", "reason", "stay_request", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
