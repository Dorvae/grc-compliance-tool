from django.db import models  # type: ignore[import]

class Domaine(models.Model):
    nom = models.CharField(max_length=100)
    referentiel = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nom} ({self.referentiel})"

    def taux_conformite(self):
        points = {"conforme": 1, "partiel": 0.5, "non_conforme": 0}
        evaluations = Evaluation.objects.filter(
            controle__domaine=self
        ).exclude(statut="na")
        

        if not evaluations.exists():
            return None

        total_points = sum(points[e.statut] for e in evaluations)
        return round((total_points / evaluations.count()) * 100, 1)

class Controle(models.Model):
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    domaine = models.ForeignKey(Domaine, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.libelle}"

class Evaluation(models.Model):
    STATUTS = [
        ("conforme", "Conforme"),
        ("partiel", "Partiellement conforme"),
        ("non_conforme", "Non conforme"),
        ("na", "Non applicable"),
    ]
    controle = models.ForeignKey(Controle, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUTS)
    date_evaluation = models.DateField(auto_now_add=True)
    commentaire = models.TextField(blank=True)

class Risque(models.Model):
    nom = models.CharField(max_length=255)
    probabilite = models.IntegerField()
    impact = models.IntegerField()
    controles = models.ManyToManyField(Controle)

    def niveau_residuel(self):
        score = self.probabilite * self.impact
        if score >= 15: return "Critique"
        elif score >= 9: return "Élevé"
        elif score >= 4: return "Moyen"
        return "Faible"