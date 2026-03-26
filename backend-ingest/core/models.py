"""Modelos no gestionados: tablas creadas en Supabase / SQL."""

from django.db import models


class Policy(models.Model):
    id = models.BigIntegerField(primary_key=True)
    batch_id = models.UUIDField(null=True, blank=True)
    policy_id = models.TextField()
    cohort_year = models.IntegerField()
    issue_age = models.IntegerField()
    annual_premium = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "policies"
        verbose_name = "Póliza"
        verbose_name_plural = "Pólizas"

    def __str__(self) -> str:
        return self.policy_id


class PolicyClaim(models.Model):
    id = models.BigIntegerField(primary_key=True)
    batch_id = models.UUIDField(null=True, blank=True)
    claim_id = models.TextField()
    policy_id = models.TextField()
    loss_date = models.DateField()
    reported_amount_bs = models.DecimalField(max_digits=14, decimal_places=2)
    paid_amount_bs = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "policy_claims"
        verbose_name = "Siniestro"
        verbose_name_plural = "Siniestros"

    def __str__(self) -> str:
        return self.claim_id
