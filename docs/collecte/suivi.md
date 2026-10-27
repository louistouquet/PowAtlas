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

- **Arpa Piemonte, depuis le 2026-10-24 vers 10 h UTC** : aucune réponse depuis GitHub Actions ni depuis la session Claude. Les unités du 24, du 25 et du 26 sont `missing` ([issue 50](https://github.com/louistouquet/PowAtlas/issues/50) ; les issues 56 et 57, doublons, sont fermées). Les unités d'observations ne sont pas retentées les jours suivants (`window_days = 0`) : l'alerte ne s'efface pas seule.
  - **Constats** [vérifié] :
    - GitHub Actions, 2026-10-24 à 19:52 UTC : `ConnectTimeout` sur `api_realtime/pie_neve` et `pie_anag` (aucune réponse TCP en 60 s, 6 essais) ; mêmes pertes les 25 et 26 ;
    - session Claude, 2026-10-25 à 14:50 UTC puis 2026-10-27 à 07:48 UTC : aucune réponse TLS de `utility` ni de `www`. Le `Connection reset by peer` vient du proxy de la session (`recentRelayFailures` de `$HTTPS_PROXY/__agentproxy/status`), pas d'Arpa ;
    - outil de lecture web, 2026-10-25 à 14:50 UTC : HTTP 503 sans corps sur `www.arpa.piemonte.it`, d'origine non attribuable ;
    - PC du pilote, 2026-10-27 [vérifié par le pilote] : `api_realtime/pie_anag` s'affiche (JSON), et `powatlas collect --unit arpa-piemonte__20261027 --out data\pc-collect` donne `complete`, avec la note `Last-Modified absent for 2 of 2 files`.
  - **Cause** : Arpa filtre les réseaux de centres de données [hypothèse]. Le PC passe le 27, alors que les réseaux de centres de données échouent du 24 au 27 (la session encore le 27, à 07:48 puis vers 08:30 UTC). Une panne du producteur finie avant le 27, avec un échec du proxy de la session ce jour-là, expliquerait aussi ces faits. Arpa ne passant plus par Actions, la question reste ouverte ; elle ne change rien à la collecte.
  - **Couverture de la copie du 27** : la fenêtre du producteur est de 7 jours (le test du 2026-10-21 couvrait du 15 au 21, [fiche](../sources/arpa-piemonte.md)). La copie couvre donc sans doute du 21 au 27, les 24 à 26 compris [hypothèse, à vérifier en lisant les dates de `pie-neve.json` quand la copie sera rangée].
  - **Correction du 2026-10-27** : Arpa est dans la tâche `pc` du catalogue, donc plus collectée par GitHub Actions. La tâche quotidienne du PC la collecte (`collect-pc`) et range dans l'archive les copies faites à la main dans `data\pc-collect` (`store`) ; `powatlas dates --data data --unit arpa-piemonte__AAAAMMJJ` liste les jours que contient chaque fichier d'une unité rangée ([installation](installation-pc.md), § 4). L'alerte `unit not complete` des unités du 24 au 26 s'efface seule après 3 jours (fenêtre du bilan de santé). L'issue 50 se ferme quand la copie du 27 est rangée et ses dates vérifiées.
  - **Repli** : l'API historique `meteoidro` (même hôte) ne servira que si la copie du 27 ne contient pas les 24 à 26. Elle n'est utilisable qu'une fois sa table journalière à jour : au 2026-10-21, son dernier jour était le 2026-06-30, hors saison, et son délai de mise à jour en saison est inconnu. Vérification : `https://utility.arpa.piemonte.it/meteoidro/dati_giornalieri_nivo_latest_date/fetch_latest/` (chemin à confirmer sur `/schema/`).
