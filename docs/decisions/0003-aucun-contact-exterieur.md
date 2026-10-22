# 0003 — Aucun contact extérieur

Date : 2026-10-22 · Statut : acceptée

## Contexte
R0.3 laissait deux questions à poser aux producteurs : le sens du champ `campo_neve` d'Arpa Piemonte et celui des codes `perssfrai` du réseau nivo-météo de Météo-France.

## Décision
Claude ne contacte ni producteur, ni support, ni auteur. Les questions se tranchent par recherche documentaire et par l'analyse des données publiques ; ce qui reste incertain est marqué [hypothèse].

## Conséquences
- Fait le 2026-10-22 : `campo_neve = S` = champ de neige à relevé manuel (preuve élevée) ; `perssfrai` `-99` / `-50` = relevé du matin / de l'après-midi d'après les données, sans définition du producteur ([`arpa-piemonte`](../sources/arpa-piemonte.md), [`reseau-nivo-meteo`](../sources/reseau-nivo-meteo.md)).
- Certaines incertitudes resteront ouvertes ; elles sont déclarées dans les fiches et dans les scores.
