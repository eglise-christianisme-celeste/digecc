"""Tests de la correction des noms des sites particuliers.

Fichier isolé (``tests_sites_particuliers.py``) pour ne pas entrer en
conflit avec une éventuelle suite de tests existante. Exécution :

    python manage.py test recensement.tests_sites_particuliers
"""

from django.test import SimpleTestCase, TestCase

from recensement.models import District, Province, Region, Village, Zone

from ..sites_particuliers import (
    CORRECTIONS_SITES_PARTICULIERS,
    corriger_nom_site,
    normaliser,
)


class NormalisationTests(SimpleTestCase):
    """Tests unitaires purs, sans base de données."""

    def test_normalisation_insensible_accents_casse_ponctuation(self):
        self.assertEqual(normaliser("Site d'Agonguè"), normaliser("SITE D'AGONGUÈ"))
        self.assertEqual(normaliser("  Tchakou  "), normaliser("Tchakou"))
        self.assertEqual(normaliser("SITE DE TCHAKOU"), normaliser("Site de Tchakou"))

    def test_ancien_nom_harmonise(self):
        self.assertEqual(
            corriger_nom_site("Site de Nativité de Sèmè Plage"),
            "Site de la Nativité de Sèmè-Plage",
        )
        self.assertEqual(corriger_nom_site("SITE CÉLESTE D'IMÈKO"), "Cité Céleste d'Imèko")

    def test_nom_deja_harmonise_reste_inchange(self):
        self.assertEqual(corriger_nom_site("Site de Tchakou"), "Site de Tchakou")

    def test_nom_non_reconnu_reste_inchange(self):
        self.assertEqual(corriger_nom_site("Un nom inconnu"), "Un nom inconnu")

    def test_couverture_des_six_noms_du_classeur(self):
        bruts = [
            "Site de Nativité de Sèmè Plage",
            "Site d'Agonguè",
            "Site de Tchakou",
            "Site Céleste d'Imèko",
            "Site de Ketu",
            "Site de Makoko",
        ]
        for brut in bruts:
            self.assertIn(corriger_nom_site(brut), CORRECTIONS_SITES_PARTICULIERS.values(), f"« {brut} » non reconnu")


class CommandeCorrectionTests(TestCase):
    """Test d'intégration de la commande ``corriger_sites_particuliers``."""

    def setUp(self):
        self.region = Region.objects.create(nom="Porto-Novo", ordre=1, code="R01")
        self.province = Province.objects.create(nom="Mère", region=self.region, code="P01")
        self.district = District.objects.create(nom="des Sites particuliers", province=self.province, code="D01")
        self.zone_benin = Zone.objects.create(nom="Bénin", district=self.district, code="Z001")
        self.zone_nigeria = Zone.objects.create(nom="Nigéria", district=self.district, code="Z002")

    def test_commande_corrige_les_noms_bruts(self):
        from django.core.management import call_command

        Village.objects.create(zone=self.zone_benin, nom="Site de Nativité de Sèmè Plage")
        Village.objects.create(zone=self.zone_nigeria, nom="Site Céleste d'Imèko")

        call_command("corriger_sites_particuliers")

        self.assertTrue(Village.objects.filter(zone=self.zone_benin, nom="Site de la Nativité de Sèmè-Plage").exists())
        self.assertTrue(Village.objects.filter(zone=self.zone_nigeria, nom="Cité Céleste d'Imèko").exists())

    def test_commande_idempotente(self):
        from django.core.management import call_command

        Village.objects.create(zone=self.zone_benin, nom="Site Céleste d'Imèko")
        call_command("corriger_sites_particuliers")
        call_command("corriger_sites_particuliers")  # deuxième exécution : ne doit rien casser

        self.assertEqual(Village.objects.filter(zone=self.zone_benin, nom="Cité Céleste d'Imèko").count(), 1)

    def test_commande_ne_touche_pas_les_villages_hors_district(self):
        from django.core.management import call_command

        autre_district = District.objects.create(nom="Dangbo", province=self.province, code="D02")
        autre_zone = Zone.objects.create(nom="Zone Dangbo", district=autre_district, code="Z003")
        Village.objects.create(zone=autre_zone, nom="Site Céleste d'Imèko")

        call_command("corriger_sites_particuliers")

        self.assertTrue(Village.objects.filter(zone=autre_zone, nom="Site Céleste d'Imèko").exists())

    def test_commande_dry_run_n_ecrit_rien(self):
        from django.core.management import call_command

        Village.objects.create(zone=self.zone_benin, nom="Site Céleste d'Imèko")
        call_command("corriger_sites_particuliers", dry_run=True)

        self.assertTrue(Village.objects.filter(zone=self.zone_benin, nom="Site Céleste d'Imèko").exists())
        self.assertFalse(Village.objects.filter(zone=self.zone_benin, nom="Cité Céleste d'Imèko").exists())
