from django import forms


class PolicyFileForm(forms.Form):
    file = forms.FileField(label="Archivo CSV o Excel")
