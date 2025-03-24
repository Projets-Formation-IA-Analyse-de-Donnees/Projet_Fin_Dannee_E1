from django import forms

class CSVUploadForm(forms.Form):
    fichier = forms.FileField(label="Fichier CSV")