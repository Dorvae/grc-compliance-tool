from django.shortcuts import render, redirect
from .models import Domaine, Risque
from .forms import EvaluationForm, RisqueForm

def home(request):
    return render(request, "home.html")

def dashboard(request):
    domaines = Domaine.objects.all()
    risques = Risque.objects.all()
    return render(request, "dashboard.html", {"domaines": domaines, "risques": risques})

def ajouter_evaluation(request):
    if request.method == "POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/")
    else:
        form = EvaluationForm()
    return render(request, "evaluation_form.html", {"form": form})

def ajouter_risque(request):
    if request.method == "POST":
        form = RisqueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/dashboard/")
    else:
        form = RisqueForm()
    return render(request, "risque_form.html", {"form": form})