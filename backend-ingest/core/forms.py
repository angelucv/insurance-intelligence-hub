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
