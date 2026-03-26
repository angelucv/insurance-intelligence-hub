from django import forms


class PolicyFileForm(forms.Form):
    file = forms.FileField(
        label="Archivo",
        help_text=(
            "CSV o Excel con columnas: policy_id, cohort_year, issue_age, annual_premium, status "
            "(active | lapsed). Opcional: issue_date (YYYY-MM-DD). Los datos se validan con hub-contracts "
            "y alimentan los KPI del API de cómputo y el portal Reflex."
        ),
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "class": "iihub-file-input",
            }
        ),
    )


class ClaimFileForm(forms.Form):
    file = forms.FileField(
        label="Archivo",
        help_text=(
            "Columnas obligatorias: claim_id, policy_id, loss_date, status. "
            "Opcionales: reported_amount_bs, paid_amount_bs. "
            "Cada policy_id debe existir ya en pólizas cargadas."
        ),
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "class": "iihub-file-input",
            }
        ),
    )
