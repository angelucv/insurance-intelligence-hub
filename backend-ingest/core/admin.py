from django.contrib import admin

from core.models import Policy


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "policy_id",
        "cohort_year",
        "issue_age",
        "annual_premium",
        "status",
        "created_at",
    )
    list_filter = ("cohort_year", "status")
    search_fields = ("policy_id",)
    ordering = ("-created_at",)

    def has_add_permission(self, request):  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ANN001
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ANN001
        return False
