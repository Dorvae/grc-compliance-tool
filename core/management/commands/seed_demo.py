"""Load the AtlasPay demo dataset.

Recreates the 5 domains, 8 controls, 8 evaluations and 3 risks shown in the
project screenshots. Statuses and risk-to-control links are taken from the original project
database (assessments of 27-28 July 2026); the dashboard reproduces the
documented compliance rates (25 / 50 / 50 / 0 / 25 %).

Usage:  python manage.py seed_demo [--reset]
"""
from django.core.management.base import BaseCommand

from core.models import Controle, Domaine, Evaluation, Risque

DOMAINES = [
    ("Organisationnel", "ISO27001"),
    ("Personnes", "ISO27001"),
    ("Physique", "ISO27001"),
    ("Technologique", "ISO27001"),
    ("DNSSI", "DNSSI"),
]

# (code, libellé, domaine, statut d'évaluation)
CONTROLES = [
    ("A.5.9", "Inventaire des actifs", "Organisationnel", "partiel"),
    ("A.5.19", "Sécurité relations fournisseurs", "Organisationnel", "non_conforme"),
    ("A.6.3", "Sensibilisation et formation", "Personnes", "partiel"),
    ("A.7.1", "Périmètres de sécurité physique", "Physique", "partiel"),
    ("A.8.5", "Authentification sécurisée", "Technologique", "non_conforme"),
    ("A.8.24", "Utilisation de la cryptographie", "Technologique", "non_conforme"),
    ("RSSI", "Organisation de la sécurité (séparation DSI/RSSI)", "DNSSI", "partiel"),
    ("SOUV", "Souveraineté / hébergement des données", "DNSSI", "non_conforme"),
]

# (nom, probabilité, impact, codes des contrôles liés)
RISQUES = [
    ("Fraude via API mal sécurisée", 3, 5, ["A.8.5"]),
    ("Ransomware sur les serveurs on-premise", 3, 5, ["A.7.1", "A.8.24"]),
    ("Fuite de données clients", 3, 4, ["A.5.19"]),
]


class Command(BaseCommand):
    help = "Charge le jeu de données de démonstration AtlasPay."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Supprime les données existantes avant le chargement.")

    def handle(self, *args, **options):
        if options["reset"]:
            Risque.objects.all().delete()
            Domaine.objects.all().delete()  # cascade: contrôles + évaluations

        domaines = {}
        for nom, ref in DOMAINES:
            domaines[nom], _ = Domaine.objects.get_or_create(nom=nom, referentiel=ref)

        controles = {}
        for code, libelle, dom, statut in CONTROLES:
            c, created = Controle.objects.get_or_create(
                code=code, defaults={"libelle": libelle, "domaine": domaines[dom]}
            )
            controles[code] = c
            if created or not Evaluation.objects.filter(controle=c).exists():
                Evaluation.objects.create(controle=c, statut=statut)

        for nom, p, i, codes in RISQUES:
            r, _ = Risque.objects.get_or_create(nom=nom, defaults={"probabilite": p, "impact": i})
            r.controles.set(controles[c] for c in codes)

        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))
        for d in Domaine.objects.all():
            self.stdout.write(f"  {d.nom:<16} {d.taux_conformite()} %")
