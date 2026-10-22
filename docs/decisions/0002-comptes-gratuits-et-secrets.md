# 0002 — Comptes gratuits autorisés, créés par le pilote

Date : 2026-10-22 · Statut : acceptée

## Contexte
Plusieurs sources et outils exigent un compte gratuit : Copernicus CDS (ERA5-Land, CERRA), Copernicus Data Space (satellite), portail API Météo-France (AROME-PI, PE-AROME, temps réel), Hugging Face, Kaggle ([roadmap](../roadmap.md), risques). La règle de SP0 était : aucun compte sans accord du pilote.

## Décision
Tous les comptes gratuits sont autorisés. **Seul le pilote les crée**, au moment où un besoin nommé apparaît, à la demande de Claude. Les jetons et identifiants vont dans les secrets GitHub ou dans un fichier local ignoré par Git (`.env`, `secrets/`), jamais dans le dépôt. Aucun moyen de paiement n'est enregistré (zéro euro).

## Conséquences
- Les fiches dont le test d'accès s'est arrêté sur `compte gratuit requis` sont reprises une fois le compte créé.
- Les sources écartées faute de compte (AROME-PI, PE-AROME métropole) sont à reconsidérer en SP1.
- `.gitignore` exclut `.env` et `secrets/`.
