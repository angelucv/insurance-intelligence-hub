from django import forms


class PolicyFileForm(forms.Form):
    file = forms.FileField(
        label="Archivo",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        ),
    )


class ClaimFileForm(forms.Form):
    file = forms.FileField(
        label="Archivo",
        help_text="Columnas: claim_id, policy_id, loss_date, status; opcional reported_amount_bs, paid_amount_bs.",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        ),
    )
