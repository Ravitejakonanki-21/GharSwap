from django.contrib import admin

from .models import Block, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reported_user", "reason", "status", "created_at")
    list_filter = ("status",)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked_user", "created_at")
