#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
from enum import Enum
from typing import Optional, Tuple


class TypeBande(Enum):
    OUVRABLES = "Jours ouvrables"  # Lundi au Samedi
    OUVRES = "Jours ouvrés"  # Lundi au Vendredi
    CALENDAIRES = "Jours calendaires"  # Lundi au Dimanche
    FRANCS = "Jours francs"  # 24h (jours partiels non comptabilisés - dimanche et jours fériés impliquant un report)
    FIXE = "Jours fixes"  # A date du jour dans le mois (par ex: le 27 de chaque mois)


class BandePrelevement:
    """Manipule les bandes de prélèvement"""

    _type_bande: TypeBande = TypeBande.OUVRABLES
    taille_bande: int = 0  # en jours
    jour_prelevement: int = 5  # numéro du jour du mois
    aujourdhui = None

    def __init__(self, type_bande: TypeBande, taille_bande: int, jour_prelevement: int):
        self._type_bande: TypeBande = type_bande
        self.taille_bande: int = taille_bande
        self.jour_prelevement: int = jour_prelevement
        self.aujourdhui = None

    def _depassement_annee(self, local_date: datetime.date) -> Tuple[int, int]:
        if local_date.month + 1 <= 12:
            mois = local_date.month + 1
            annee = local_date.year
        else:
            mois = 1
            annee = local_date.year + 1
        return annee, mois

    def _calcul_date_prelevement(self, aujourdhui: datetime.date) -> datetime.date:
        """Détermine la prochaine date de prélèvement possible"""
        if self.jour_prelevement < aujourdhui.day:
            annee, mois = self._depassement_annee(aujourdhui)
            date_prelevement = datetime.date(
                year=annee, month=mois, day=self.jour_prelevement
            )
        else:
            date_prelevement = datetime.date(
                year=aujourdhui.year,
                month=aujourdhui.month,
                day=self.jour_prelevement,
            )
        return date_prelevement

    def _repousse_date_prelevement(
        self, date_prelevement: datetime.date
    ) -> datetime.date:
        """Détermine la date de prélèvement suivante possible"""
        annee, mois = self._depassement_annee(date_prelevement)
        return datetime.date(year=annee, month=mois, day=date_prelevement.day)

    def _convert_jours_calendaires(
        self, date_prelevement: datetime.date, ecart: int, jours_semaine: int
    ) -> datetime.date:
        """Convertion des jours ouvrables en jours calandaires"""
        semaines_cal = ecart // 7
        semaines_bande = self.taille_bande // jours_semaine
        jours_bande = self.taille_bande % jours_semaine
        bande_cal = semaines_bande * 7 + jours_bande

        # Il reste plus de semaines calendaires que la bande ne contient de semaines en jours ouvrables
        if (semaines_cal < semaines_bande) or (ecart <= bande_cal):
            date_prelevement = self._repousse_date_prelevement(date_prelevement)
        return date_prelevement

    def _calcul_bande(self, aujourdhui: datetime.date) -> datetime.date:
        """Contrôle si l'on est dans la bande ou pas"""
        date_prelevement = self._calcul_date_prelevement(aujourdhui)
        ecart = date_prelevement - aujourdhui
        if (
            self._type_bande != TypeBande.FIXE and ecart.days <= self.taille_bande
        ):  # gestion des cas évidents + jours calendaires et francs
            date_prelevement = self._repousse_date_prelevement(date_prelevement)
        elif (
            self._type_bande == TypeBande.FIXE
            and aujourdhui.day >= self.taille_bande
        ):  # gestion des jours fixes
            date_prelevement = self._repousse_date_prelevement(date_prelevement)
        elif (
            self._type_bande == TypeBande.FIXE
            and aujourdhui.day <= self.taille_bande
            and aujourdhui.month == date_prelevement.month
        ):  # gestion des jours fixes
            date_prelevement = self._repousse_date_prelevement(date_prelevement)
        elif self._type_bande == TypeBande.OUVRABLES:  # jours ouvrables
            date_prelevement = self._convert_jours_calendaires(
                date_prelevement, ecart.days, 6
            )
        elif self._type_bande == TypeBande.OUVRES:  # jours ouvrés
            date_prelevement = self._convert_jours_calendaires(
                date_prelevement, ecart.days, 5
            )

        return date_prelevement

    def date_prochain_prelevement(
        self, aujourdhui: Optional[datetime.date] = None
    ) -> datetime.date:
        """Retourne la date du prochain prélèvement selon la date du jour"""
        self.aujourdhui = aujourdhui or datetime.date.today()
        return self._calcul_bande(aujourdhui)
