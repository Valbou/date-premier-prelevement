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
        i = 0

        # Test du mois entier
        while debut <= jour <= fin:
            with self.subTest(i=i):
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
            i += 1
            jour = jour + datetime.timedelta(days=1)

    def test_date_prochain_prelevement_jour_ouvrables(self):
        self.bande.type_bande = TypeBande.OUVRABLES
        self.bande.taille_bande = 8
        self._bande()

    def test_date_prochain_prelevement_jour_ouvres(self):
        self.bande.type_bande = TypeBande.OUVRES
        self.bande.taille_bande = 7
        self._bande()

    def test_date_prochain_prelevement_jour_calendaires(self):
        self.bande.type_bande = TypeBande.CALENDAIRES
        self.bande.taille_bande = 9
        self._bande()

    def test_date_prochain_prelevement_jour_francs(self):
        self.bande.type_bande = TypeBande.FRANCS
        self.bande.taille_bande = 9
        self._bande()

    def test_date_prochain_prelevement_jour_fixe(self):
        self.bande.type_bande = TypeBande.FIXE
        self.bande.taille_bande = 27
        self._bande()
