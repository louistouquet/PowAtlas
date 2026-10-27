# Suivi de la collecte : alertes, contrôles, corrections

Procédure du 2026-10-25, pour le pilote et pour toute session Claude. Le but est d'avoir 100 % des unités complètes, ou chaque manque expliqué. Le fonctionnement est décrit dans le [cadrage SP1](../specs/2026-10-22-sp1-archive-design.md) et les [décisions 0005](../decisions/0005-collecte-hybride-actions-et-pc.md) et [0006](../decisions/0006-rattrapage-sur-le-pc-automatique.md).

## 1. D'où viennent les alertes

| Alerte | Où | Ce qu'elle signale |
|---|---|---|
| **Bilan de santé** au début de chaque session Claude ([`scripts/health.py`](../../scripts/health.py), lancé par [`scripts/session-start.sh`](../../scripts/session-start.sh)) | contexte de la session | runs `collect` en échec sur 48 h ; dernier run réussi il y a plus de 2 h ; unités des 3 derniers jours pas complètes ; issues `collecte` ouvertes |
| **Rappels du pilote** ([`rappels.toml`](rappels.toml), lus par [`scripts/reminders.py`](../../scripts/reminders.py)) | contexte de la session | dernier `sync` connu à plus de 20 jours ; jetons et version d'API à renouveler ; actions attendues du pilote |
| **Issue `collecte`** et e-mail de GitHub | dépôt, boîte du pilote | unités perdues pour de bon après le dernier déclenchement d'une tâche ; 45 jours sans commit |
| **E-mail de cron-job.org** | boîte du pilote | déclencheur horaire en échec (jeton expiré : 401) |
| **Journal du PC** (`data\pc-daily.log`) et `powatlas progress` | PC du pilote | `sync` en erreur ou artefacts de plus de 48 h ; avancement du rattrapage et runs abandonnés (`given up`, avec la raison) |

Le PC n'est pas visible depuis une session Claude : le pilote colle ses sorties.

## 2. Contrôles du pilote (une fois par semaine suffit)

Dans PowerShell, une ligne à la fois :

```powershell
cd D:\Codage\PowAtlas
Get-ScheduledTaskInfo -TaskName "PowAtlas sync"
.venv\Scripts\powatlas progress --data data
```

- `LastRunTime` donne le dernier passage de la tâche (le jour même si le PC a été allumé). `LastTaskResult` 0 veut dire « sans erreur » ; 267011 veut dire « pas encore lancée ».
- `progress` affiche une barre par source. `given up` liste les runs abandonnés et la raison : coller la sortie dans une session.
- En cas de doute : `Get-Content data\pc-daily.log -Tail 20`.

## 3. Que faire, cas par cas (session Claude)

- **Run `collect` en échec** : lire les journaux du job (outils GitHub). La ligne `note:` de l'unité donne la cause. Le run n'échoue que s'il y a une perte définitive ou plus de 45 jours d'inactivité.
- **Unité `missing` ou `partial`** : vérifier si le producteur répond (même requête depuis la session) et lire la fiche de la source.
  - **Panne chez le producteur** : rien à corriger dans le code. La rattraper dans sa fenêtre (tableau ci-dessous), puis noter le manque daté dans la fiche et dans `STATUS.md`.
  - **Changement chez le producteur** (format, grille, adresse) : corriger l'adaptateur (TDD, PR), puis relancer avec `workflow_dispatch` (`task=auto`) tant que la fenêtre le permet.
- **Dernier run réussi il y a plus de 2 h** :
  1. regarder l'historique de cron-job.org avec le pilote (jeton, § 4 de [`declenchement-externe.md`](declenchement-externe.md)) ;
  2. regarder si le workflow a été désactivé (onglet *Actions*) ;
  3. lancer `workflow_dispatch` à la main en attendant.
- **Run abandonné du rattrapage (`given up`)** : la raison vient de `progress`. Corriger la cause si elle est chez nous ; exemple : la grille IFS de 1439 colonnes des 2024-02-01 et 02 ([PR 52](https://github.com/louistouquet/PowAtlas/pull/52)). Le pilote relance ensuite, quand la tâche ne tourne pas : `backfill --source <source> --data data --to <date> --retry-given-up`.
- **Pas de nouvelles du PC depuis 20 jours** : demander au pilote les contrôles du § 2. Les artefacts disparaissent au bout de 30 jours.
- **Toujours** : fermer l'issue `collecte` quand la cause est traitée, en notant ce qui est rattrapé et ce qui reste perdu ; mettre à jour `rappels.toml`, `STATUS.md` et `NEXT.md`.

## 4. Combien de temps une unité manquée reste rattrapable

D'après `window_days` du [catalogue](../../src/powatlas/catalogue.toml) et les fiches, lus le 2026-10-25 :

| Source | Rattrapable sur GitHub | Ensuite |
|---|---|---|
| ICON-D2, ICON-EU | le jour même (run conservé 24 h chez DWD) | perdu |
| AROME 0,025°, ARPEGE 0,1° | 7 jours | perdu |
| IFS 0,25°, AIFS | 2 jours (portail) | copie AWS sur des années : rattrapage manuel par le PC (`backfill --source <source> --data data --from <date> --to <date>`), car le rattrapage automatique s'arrête au 2026-04-30 |
| GFS 0,25° (PC seulement) | sans objet : rattrapage automatique par la tâche du PC | copie AWS sur des années |
| SLF | chaque copie couvre 7 jours | perdu au-delà de 7 jours |
| Arpa Piemonte (PC seulement depuis le 2026-10-27) | sans objet : collectée chaque jour par la tâche du PC (`collect-pc`) ; chaque copie couvre 7 jours | API historique `meteoidro` (journalière, depuis 1983), une fois la table à jour (`fetch_latest`) ; délai de mise à jour en saison inconnu |
| Météo-France nivo-météo et base quotidienne | fichiers cumulés de l'année ou de la saison | perdu seulement pour les corrections ultérieures |

## 5. Constats en cours

- **Arpa Piemonte : réglé le 2026-10-27** ([issue 50](https://github.com/louistouquet/PowAtlas/issues/50), fermée). Depuis le 2026-10-24, Arpa ne répond ni à GitHub Actions ni à la session Claude, mais répond au PC du pilote [vérifié]. Cause supposée : filtrage des réseaux de centres de données ; une panne du producteur finie avant le 27, doublée d'un échec du proxy de la session, l'expliquerait aussi [hypothèse]. Arpa est dans la tâche `pc` du catalogue ([PR 59](https://github.com/louistouquet/PowAtlas/pull/59)) : la tâche quotidienne du PC la collecte (`collect-pc`) et range les copies faites à la main (`store`). La copie du 2026-10-27 à 07:54 UTC, rangée, contient les jours du 2026-10-20 au 2026-10-26 (80 stations par jour, `powatlas dates`) [vérifié par le pilote, sortie collée dans la session du 2026-10-27 et citée dans l'issue 50] : les unités `missing` du 24 au 26 sont rattrapées, rien n'est perdu. Chaque copie couvrant 7 jours, un PC éteint 6 jours de suite au plus ne perd rien ; au-delà, l'API historique `meteoidro` pourrait boucher les trous (prévu en SP2) [hypothèse] : elle est journalière (`hn`, `hs`), et sa table s'arrêtait au 2026-06-30 le 2026-10-21, délai de mise à jour en saison inconnu.
- **Rattrapage IFS, runs `missing` en série** (journal du PC du 2026-10-27, runs vus du 2025-02-26 au 2026-01-25 : `FormatChange: step 3: mx2t3 decoded as max_2t at 180 min`) : du 2025-02-26 au plus tard au 2026-02-01 au moins, les extrêmes de température (`mx2t3`, `mn2t3`, `mx2t6`, `mn2t6`) portent les tables GRIB2 34, qu'ecCodes 2.50 lit `max_2t` et `min_2t` [vérifié, 2026-10-27] ([fiche](../sources/ecmwf-open-data.md#limites)). Corrigé le 2026-10-27 ([PR 60](https://github.com/louistouquet/PowAtlas/pull/60)) : les deux noms sont acceptés si la nature et la durée correspondent. La tâche du PC reprend ces runs tant qu'ils ont moins de 3 tentatives ; le nombre de passages déjà faits est inconnu, d'où un `backfill --source ifs-0p25 --data data --retry-given-up --max-hours 3` lancé une fois à la main pour remettre les compteurs à zéro. Ces échecs expliquent sans doute l'avance lente de l'IFS (207/452 au 2026-10-27) [hypothèse].
