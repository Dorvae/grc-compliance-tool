from django import forms
from .models import Evaluation, Risque

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ["controle", "statut", "commentaire"]

class RisqueForm(forms.ModelForm):
    class Meta:
        model = Risque
        fields = ["nom", "probabilite", "impact", "controles"]