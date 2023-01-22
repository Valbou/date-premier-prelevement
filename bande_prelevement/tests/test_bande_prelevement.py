import calendar
import datetime
import unittest

from bande_prelevement import BandePrelevement, TypeBande


class TestBandePrelevement(unittest.TestCase):
    """Classe de tests pour les bandes de prélèvement des organisations"""

    bascule = datetime.date(year=2018, month=12, day=27)  # Jour de la bascule

    def setUp(self):
        self.bande = BandePrelevement(
            type_bande=TypeBande.FIXE, taille_bande=27, jour_prelevement=5
        )

    def _bande(self):
        debut = datetime.date(year=self.bascule.year, month=self.bascule.month, day=1)
        fin = datetime.date(
            year=self.bascule.year,
            month=self.bascule.month,
            day=calendar.monthrange(year=self.bascule.year, month=self.bascule.month)[
                1
            ],
        )
        jour = debut

        # Test du mois entier
        while debut <= jour <= fin:
            with self.subTest(jour):
                # Prélèvement le mois prochain
                if jour < self.bascule:
                    self.assertEqual(
                        self.bande.date_prochain_prelevement(jour),
                        datetime.date(year=2019, month=1, day=5),
                    )
                # Prélèvement le mois suivant
                else:
                    self.assertEqual(
                        self.bande.date_prochain_prelevement(jour),
                        datetime.date(year=2019, month=2, day=5),
                    )
            jour = jour + datetime.timedelta(days=1)

    def test_date_prochain_prelevement_jour_ouvrables(self):
        self.bande._type_bande = TypeBande.OUVRABLES
        self.bande.taille_bande = 8
        self._bande()

    def test_date_prochain_prelevement_jour_ouvres(self):
        self.bande._type_bande = TypeBande.OUVRES
        self.bande.taille_bande = 7
        self._bande()

    def test_date_prochain_prelevement_jour_calendaires(self):
        self.bande._type_bande = TypeBande.CALENDAIRES
        self.bande.taille_bande = 9
        self._bande()

    def test_date_prochain_prelevement_jour_francs(self):
        self.bande._type_bande = TypeBande.FRANCS
        self.bande.taille_bande = 9
        self._bande()

    def test_date_prochain_prelevement_jour_fixe(self):
        self.bande._type_bande = TypeBande.FIXE
        self.bande.taille_bande = 27
        self._bande()

    def test_depassement_annee(self):
        jour = datetime.date(year=2022, month=12, day=1)
        annee, mois = self.bande._depassement_annee(jour)
        self.assertEqual(annee, 2023)
        self.assertEqual(mois, 1)

    def test_depassement_annee_fin_mois(self):
        jour = datetime.date(year=2022, month=12, day=31)
        annee, mois = self.bande._depassement_annee(jour)
        self.assertEqual(annee, 2023)
        self.assertEqual(mois, 1)

    def test_sans_depassement_annee(self):
        jour = datetime.date(year=2023, month=1, day=1)
        annee, mois = self.bande._depassement_annee(jour)
        self.assertEqual(annee, 2023)
        self.assertEqual(mois, 2)

    def test_calcul_date_prelevement_a_venir(self):
        aujourdhui = datetime.date(year=2018, month=12, day=4)
        self.assertEqual(
            self.bande._calcul_date_prelevement(aujourdhui),
            datetime.date(year=2018, month=12, day=5)
        )

    def test_calcul_date_prelevement_passee(self):
        aujourdhui = datetime.date(year=2018, month=12, day=6)
        self.assertEqual(
            self.bande._calcul_date_prelevement(aujourdhui),
            datetime.date(year=2019, month=1, day=5)
        )

    def test_calcul_date_prelevement_actuelle(self):
        aujourdhui = datetime.date(year=2018, month=12, day=5)
        self.assertEqual(
            self.bande._calcul_date_prelevement(aujourdhui),
            datetime.date(year=2018, month=12, day=5)
        )

    def test_repousse_date_prelevement(self):
        date_prelevement = datetime.date(year=2022, month=12, day=5)
        nouvelle_date = self.bande._repousse_date_prelevement(date_prelevement)
        self.assertEqual(
            nouvelle_date,
            datetime.date(year=2023, month=1, day=5)
        )
