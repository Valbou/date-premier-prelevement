#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

TYPE_JOURS = (
    (1, 'Jours ouvrables'), # Lundi au Samedi
    (2, 'Jours ouvrés'), # Lundi au Vendredi
    (3, 'Jours calendaires'), # Lundi au Dimanche
    (4, 'Jours francs'), # 24h glissantes
    (5, 'Jours fixe'), # A date du jour dans le mois (par ex: le 27 pour MSF)
)

class BandePrelevement:
    type_bande = 0
    taille_bande = 0
    jour_prelevement = 5
    aujourdhui = None

    """Manipule les bandes de prélèvement"""
    def __init__(self, type_bande, taille_bande, jour_prelevement):
        self.type_bande = type_bande
        self.taille_bande = taille_bande
        self.jour_prelevement = jour_prelevement
        self.aujourdhui = None
        print('Aujourdh\'hui:', self.aujourdhui)

    def _depassement_annee(self, local_date):
        if local_date.month + 1 <= 12:
            mois = local_date.month + 1
            annee = local_date.year
        else:
            mois = 1
            annee = local_date.year + 1
        return annee, mois

    def _calcul_date_prelevement(self):
        """Détermine la prochaine date de prélèvement possible"""
        if self.jour_prelevement < self.aujourdhui.day:
            annee, mois = self._depassement_annee(self.aujourdhui)
            self.date_prelevement = datetime.date(year=annee, month=mois, day=self.jour_prelevement)
        else:
            self.date_prelevement = datetime.date(year=self.aujourdhui.year, month=self.aujourdhui.month, day=self.jour_prelevement)
        print('Date prélèvement', self.date_prelevement)

    def _repousse_date_prelevement(self):
        """Détermine la date de prélèvement suivante possible"""
        annee, mois = self._depassement_annee(self.date_prelevement)
        self.date_prelevement = datetime.date(year=annee, month=mois, day=self.date_prelevement.day)
        print('Date prélèvement repoussée', self.date_prelevement)

    def _convert_jours_calendaires(self, ecart, jours_semaine):
        """Convertion des jours ouvrables en jours calandaires"""
        semaines_cal = ecart // 7
        semaines_bande = self.taille_bande // jours_semaine
        jours_bande = self.taille_bande % jours_semaine
        bande_cal = semaines_bande * 7 + jours_bande

        if semaines_cal > semaines_bande:  # Il reste plus de semaines calendaires que la bande ne contient de semaines en jours ouvrables
            print("{} semaines restantes > {} semaines de {} jours".format(semaines_cal, semaines_bande, jours_semaine))
            return True
        elif semaines_cal < semaines_bande:
            print("{} semaines restantes < {} semaines de {} jours".format(semaines_cal, semaines_bande, jours_semaine))
            self._repousse_date_prelevement()
        elif ecart <= bande_cal:
            print('Ecart :', ecart, '- Bande en jours cal:', bande_cal)
            self._repousse_date_prelevement()

    def _calcul_bande(self):
        """Contrôle si l'on est dans la bande ou pas"""
        self._calcul_date_prelevement()
        ecart = self.date_prelevement - self.aujourdhui
        if self.type_bande != 5 and ecart.days <= self.taille_bande:  # gestion des cas évidents + jours calendaires et francs
            print('Jours restants :', ecart.days, '< taille bande :', self.taille_bande)
            self._repousse_date_prelevement()
        elif self.type_bande == 5 and self.aujourdhui.day >= self.taille_bande:  # gestion des jours fixes
            print('Jours fixes 1')
            self._repousse_date_prelevement()
        elif self.type_bande == 5 and self.aujourdhui.day <= self.taille_bande and self.aujourdhui.month == self.date_prelevement.month:  # gestion des jours fixes
            print('Jours fixes 2')
            self._repousse_date_prelevement()
        elif self.type_bande == 1:  # jours ouvrables
            print('Jours ouvrables')
            self._convert_jours_calendaires(ecart.days, 6)
        elif self.type_bande == 2:  # jours ouvrés
            print('Jours ouvrés')
            self._convert_jours_calendaires(ecart.days, 5)

    def date_prochain_prelevement(self, aujourdhui=datetime.date.today()):
        """Retourne la date du prochain prélèvement selon la date du jour"""
        print('--- Calcul de la Bande ---')
        self.aujourdhui = aujourdhui
        self._calcul_bande()
        return self.date_prelevement


import unittest
import calendar


class TestBandePrelevement(unittest.TestCase):
    """Classe de tests pour les bandes de prélèvement des organisations"""
    bascule = datetime.date(year=2018, month=12, day=27)  # Jour de la bascule

    def setUp(self):
        self.bande = BandePrelevement(type_bande=5, taille_bande=27, jour_prelevement=5)

    def _bande(self):
        debut = datetime.date(year=self.bascule.year, month=self.bascule.month, day=1)
        fin = datetime.date(year=self.bascule.year, month=self.bascule.month, day=calendar.monthrange(year=self.bascule.year, month=self.bascule.month)[1])
        jour = debut
        i=0

        # Test du mois entier
        while debut <= jour <= fin:
            print(str(jour))
            with self.subTest(i=i):
                # Prélèvement le mois prochain
                if jour < self.bascule:
                    self.assertEqual(self.bande.date_prochain_prelevement(jour), datetime.date(year=2019, month=1, day=5))
                # Prélèvement le mois suivant
                else:
                    self.assertEqual(self.bande.date_prochain_prelevement(jour), datetime.date(year=2019, month=2, day=5))
            i+=1
            jour = jour + datetime.timedelta(days=1)

    def test_date_prochain_prelevement_jour_ouvrables(self):
        self.bande.type_bande = 1
        self.bande.taille_bande = 8
        self._bande()

    def test_date_prochain_prelevement_jour_ouvres(self):
        self.bande.type_bande = 2
        self.bande.taille_bande = 7
        self._bande()

    def test_date_prochain_prelevement_jour_calendaires(self):
        self.bande.type_bande = 3
        self.bande.taille_bande = 9
        self._bande()

    def test_date_prochain_prelevement_jour_francs(self):
        self.bande.type_bande = 4
        self.bande.taille_bande = 9
        self._bande()

    def test_date_prochain_prelevement_jour_fixe(self):
        self.bande.type_bande = 5
        self.bande.taille_bande = 27
        self._bande()


if __name__ == '__main__':
    unittest.main()

    import os
    os.system('pause')
