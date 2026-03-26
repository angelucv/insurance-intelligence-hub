from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from core.models import Policy, PolicyClaim


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "policy_id",
        "cohort_year",
        "issue_age",
        "premium_display",
        "status",
        "created_at",
    )
    list_filter = ("cohort_year", "status")
    search_fields = ("policy_id", "status")
    ordering = ("-created_at",)
    list_per_page = 50
    show_full_result_count = True
    empty_value_display = "—"

    @admin.display(description="Prima anual (Bs.)", ordering="annual_premium")
    def premium_display(self, obj: Policy) -> str:
        return f"{obj.annual_premium:,.2f}"

    def has_add_permission(self, request):  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ANN001
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ANN001
        return False


@admin.register(PolicyClaim)
class PolicyClaimAdmin(admin.ModelAdmin):
    list_display = (
        "claim_id",
        "policy_id",
        "loss_date",
        "reported_display",
        "paid_display",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        ("loss_date", DateFieldListFilter),
    )
    search_fields = ("claim_id", "policy_id", "status")
    ordering = ("-created_at",)
    list_per_page = 50
    show_full_result_count = True
    date_hierarchy = "loss_date"
    empty_value_display = "—"

    @admin.display(description="Reportado (Bs.)", ordering="reported_amount_bs")
    def reported_display(self, obj: PolicyClaim) -> str:
        return f"{obj.reported_amount_bs:,.2f}"

    @admin.display(description="Pagado (Bs.)", ordering="paid_amount_bs")
    def paid_display(self, obj: PolicyClaim) -> str:
        return f"{obj.paid_amount_bs:,.2f}"

    def has_add_permission(self, request):  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ANN001
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ANN001
        return False
