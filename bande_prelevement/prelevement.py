#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
from enum import Enum
from typing import Optional


class TypeBande(Enum):
    OUVRABLES = "Jours ouvrables"  # Lundi au Samedi
    OUVRES = "Jours ouvrés"  # Lundi au Vendredi
    CALENDAIRES = "Jours calendaires"  # Lundi au Dimanche
    FRANCS = "Jours francs"  # 24h (jours partiels non comptabilisés - dimanche et jours fériés impliquant un report)
    FIXE = "Jours fixes"  # A date du jour dans le mois (par ex: le 27 de chaque mois)


class BandePrelevement:
    """Manipule les bandes de prélèvement"""

    type_bande: TypeBande = TypeBande.OUVRABLES
    taille_bande: int = 0  # en jours
    jour_prelevement: int = 5  # numéro du jour du mois
    aujourdhui = None

    def __init__(self, type_bande: TypeBande, taille_bande: int, jour_prelevement: int):
        self.type_bande: TypeBande = type_bande
        self.taille_bande: int = taille_bande
        self.jour_prelevement: int = jour_prelevement
        self.aujourdhui = None

    def _depassement_annee(self, local_date: datetime.date):
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
            self.date_prelevement = datetime.date(
                year=annee, month=mois, day=self.jour_prelevement
            )
        else:
            self.date_prelevement = datetime.date(
                year=self.aujourdhui.year,
                month=self.aujourdhui.month,
                day=self.jour_prelevement,
            )

    def _repousse_date_prelevement(self):
        """Détermine la date de prélèvement suivante possible"""
        annee, mois = self._depassement_annee(self.date_prelevement)
        self.date_prelevement = datetime.date(
            year=annee, month=mois, day=self.date_prelevement.day
        )

    def _convert_jours_calendaires(self, ecart: int, jours_semaine: int):
        """Convertion des jours ouvrables en jours calandaires"""
        semaines_cal = ecart // 7
        semaines_bande = self.taille_bande // jours_semaine
        jours_bande = self.taille_bande % jours_semaine
        bande_cal = semaines_bande * 7 + jours_bande

        # Il reste plus de semaines calendaires que la bande ne contient de semaines en jours ouvrables
        if (semaines_cal < semaines_bande) or (ecart <= bande_cal):
            self._repousse_date_prelevement()

    def _calcul_bande(self):
        """Contrôle si l'on est dans la bande ou pas"""
        self._calcul_date_prelevement()
        ecart = self.date_prelevement - self.aujourdhui
        if (
            self.type_bande != TypeBande.FIXE and ecart.days <= self.taille_bande
        ):  # gestion des cas évidents + jours calendaires et francs
            self._repousse_date_prelevement()
        elif (
            self.type_bande == TypeBande.FIXE
            and self.aujourdhui.day >= self.taille_bande
        ):  # gestion des jours fixes
            self._repousse_date_prelevement()
        elif (
            self.type_bande == TypeBande.FIXE
            and self.aujourdhui.day <= self.taille_bande
            and self.aujourdhui.month == self.date_prelevement.month
        ):  # gestion des jours fixes
            self._repousse_date_prelevement()
        elif self.type_bande == TypeBande.OUVRABLES:  # jours ouvrables
            self._convert_jours_calendaires(ecart.days, 6)
        elif self.type_bande == TypeBande.OUVRES:  # jours ouvrés
            self._convert_jours_calendaires(ecart.days, 5)

    def date_prochain_prelevement(self, aujourdhui: Optional[datetime.date] = None):
        """Retourne la date du prochain prélèvement selon la date du jour"""
        self.aujourdhui = aujourdhui or datetime.date.today()
        self._calcul_bande()
        return self.date_prelevement
