# Date de Premier Prelevement
Calcul de la date de premier prélèvement, selon une bande de prélèvement exprimée en jours légaux (ouvrés, ouvrables, calendaires, etc...) ou fixes.

La bande de prélèvement correspond au délai minimum nécessaire à la mise en place d'un prélèvement automatique. (Variable selon les process et les banques)

Cet outil est utilisé dans la collecte de dons notamment.
Il permet, à partir d'une contrainte de date de prélèvement (ex: prélèvement le 5 du mois), de savoir si en souscrivant aujourd'hui, il sera possible de prélever dès le mois prochain. A défaut, le premier prélèvement aura lieu le même jour le mois suivant (ex: le 5 du mois suivant).
Il permet ainsi de proposer une deuxième date de prélèvement si la première ne passe pas et que l'on souhaite démarrer les prélèvements au plus tôt (ex: prélèvement le 5 ou le 15 du mois).

## Usage

Vous souhaitez prélever uniquement les 5 de chaque mois, et votre banque impose un délai de traitement de 7 jours ouvrés.
En fonction de la date du jour, vous pourrez informer votre client de la prochaine date de prélèvement.

```python
from datetime import date

from bande_prelevement import BandePrelevement, TypeBande

aujourdhui = date.today()
bande = BandePrelevement(
    type_bande=TypeBande.OUVRES, taille_bande=7, jour_prelevement=5
)
date_prelevement: date = bande.date_prochain_prelevement(aujourdhui)
```
