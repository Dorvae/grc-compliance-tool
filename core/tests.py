from django.test import TestCase

from .models import Controle, Domaine, Evaluation, Risque


class TauxConformiteTests(TestCase):
    def setUp(self):
        self.domaine = Domaine.objects.create(nom="Technologique", referentiel="ISO27001")

    def _eval(self, code, statut):
        c = Controle.objects.create(code=code, libelle=code, domaine=self.domaine)
        Evaluation.objects.create(controle=c, statut=statut)

    def test_sans_evaluation_retourne_none(self):
        self.assertIsNone(self.domaine.taux_conformite())

    def test_ponderation(self):
        self._eval("A", "conforme")      # 1
        self._eval("B", "partiel")       # 0.5
        self._eval("C", "non_conforme")  # 0
        self.assertEqual(self.domaine.taux_conformite(), 50.0)

    def test_non_applicable_exclu(self):
        self._eval("A", "conforme")
        self._eval("B", "na")
        self.assertEqual(self.domaine.taux_conformite(), 100.0)

    def test_seulement_na_retourne_none(self):
        self._eval("A", "na")
        self.assertIsNone(self.domaine.taux_conformite())


class NiveauRisqueTests(TestCase):
    def test_seuils(self):
        cas = [(5, 3, "Critique"), (3, 5, "Critique"), (3, 4, "Élevé"),
               (3, 3, "Élevé"), (2, 2, "Moyen"), (1, 3, "Faible"), (1, 1, "Faible")]
        for p, i, attendu in cas:
            with self.subTest(p=p, i=i):
                self.assertEqual(Risque(nom="r", probabilite=p, impact=i).niveau_residuel(), attendu)


class VuesTests(TestCase):
    def test_pages_repondent(self):
        for url in ["/", "/dashboard/", "/evaluations/ajouter/", "/risques/ajouter/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_ajout_risque_redirige_vers_dashboard(self):
        d = Domaine.objects.create(nom="D", referentiel="ISO27001")
        c = Controle.objects.create(code="A.8.5", libelle="Auth", domaine=d)
        r = self.client.post("/risques/ajouter/", {"nom": "Test", "probabilite": 3,
                                                   "impact": 5, "controles": [c.pk]})
        self.assertRedirects(r, "/dashboard/")
        self.assertEqual(Risque.objects.get().niveau_residuel(), "Critique")

    def test_dashboard_reproduit_les_taux_documentes(self):
        from django.core.management import call_command
        from io import StringIO
        call_command("seed_demo", stdout=StringIO())
        attendu = {"Organisationnel": 25.0, "Personnes": 50.0, "Physique": 50.0,
                   "Technologique": 0.0, "DNSSI": 25.0}
        for d in Domaine.objects.all():
            self.assertEqual(d.taux_conformite(), attendu[d.nom])
