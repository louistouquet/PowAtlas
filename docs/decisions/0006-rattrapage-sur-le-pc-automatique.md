# 0006 — Rattrapage historique sur le PC, automatique et sans partiels dus au serveur

Date : 2026-10-23 · Statut : acceptée (le pilote a délégué le choix : « prends les meilleures décisions », 2026-10-23)

## Contexte
Le premier rattrapage AIFS, lancé à la main sur le PC du pilote, fait environ 47 s par run, contre 20 s attendues d'après l'essai court. Le bucket AWS d'ECMWF ralentit un débit soutenu (HTTP 503 `SlowDown`), et des runs restent partiels. Le pilote demande :
- s'il faut un cloud qui télécharge 24 h sur 24 ;
- comment éviter les partiels ;
- si couper le PC casse quelque chose ;
- une seule direction, notée.

## Options étudiées
- **Cloud gratuit, téléchargement 24 h sur 24.**
  - *GitHub Actions* : la [décision 0005](0005-collecte-hybride-actions-et-pc.md) y a écarté les gros volumes d'AWS (doute sur les conditions d'utilisation pour environ 185 Go). Les artefacts ne durent que 30 jours, et le serveur qui ralentit resterait le même.
  - *Machines virtuelles gratuites* (offres « toujours gratuites » des grands clouds) : elles demandent en général une carte bancaire à l'inscription [hypothèse, non vérifiée le 2026-10-23]. C'est un risque pour la règle du zéro euro, et le pilote devrait créer un compte de plus.
  - Dans tous les cas, le goulot est le serveur, pas la disponibilité du PC.
- **PC du pilote** (décision 0005). Le rattrapage n'est pas pressé : les copies AWS d'ECMWF et de NOAA gardent des années d'historique ([fiche ECMWF](../sources/ecmwf-open-data.md), [fiche GFS](../sources/gfs.md)). Un PC éteint met donc le rattrapage en pause, sans rien perdre. Seule la collecte quotidienne est urgente, et elle tourne déjà sur Actions, 24 h sur 24.

## Décision
**Pas de cloud pour le rattrapage : il reste sur le PC, entièrement automatique.**
- **Tâche planifiée quotidienne** ([`scripts/pc-daily.ps1`](../../scripts/pc-daily.ps1), [guide](../collecte/installation-pc.md), § 4). Au premier allumage de la journée, elle attend le réseau, lance `sync`, puis fait une heure de rattrapage par source (AIFS, IFS, GFS). Ensuite, elle tient GFS à jour. Le pilote n'a plus rien à lancer.
- **Ralentissements du serveur absorbés au lieu de produire des partiels** :
  - après un 503, le rythme ralentit de lui-même jusqu'à 10 s entre requêtes, puis réaccélère à chaque succès ;
  - le rattrapage réessaie chaque requête jusqu'à 10 fois, soit environ 20 minutes ;
  - un run resté partiel seulement parce que le serveur a refusé est repris au passage suivant, sans compter comme une tentative (10 passages au plus).
  - Les seuls partiels qui restent sont donc des données réellement absentes chez le producteur. Ils sont notés dans le manifeste.
- **Couper le PC à tout moment ne casse rien.** Chaque fichier est écrit à part, puis renommé d'un coup ; un run interrompu est refait au passage suivant. Les runs complets sont sautés, donc rien n'est fait en double. La tâche ne lance pas de rattrapage si un autre `powatlas` tourne déjà.

## Conséquences
- Durée : environ 3 h pour l'AIFS et environ 30 h pour l'IFS au débit soutenu mesuré ; GFS reste à mesurer. Cela fait quelques semaines de passages quotidiens d'une heure par source, sans action du pilote. Lancer une source à la main reste possible pour aller plus vite ([guide](../collecte/installation-pc.md), § 5).
- À revoir si le PC reste éteint plus de 20 jours (les artefacts de la collecte quotidienne durent 30 jours ; un rappel s'affiche à chaque session) ou si AWS retire l'historique.
