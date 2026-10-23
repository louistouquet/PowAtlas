# Installation de la collecte sur le PC du pilote

Guide du 2026-10-22 pour `D:\Codage\PowAtlas` (Windows). Il met en place le rapatriement quotidien des artefacts de GitHub Actions vers l'archive de référence `D:\Codage\PowAtlas\data\` ([décision 0005](../decisions/0005-collecte-hybride-actions-et-pc.md), [cadrage SP1](../specs/2026-10-22-sp1-archive-design.md)). La collecte elle-même tourne sur GitHub Actions : ce guide n'est pas nécessaire pour qu'elle démarre, mais l'archive n'existe sur le PC qu'une fois `sync` lancé, et les artefacts disparaissent au bout de 30 jours.

Le déclenchement horaire de la collecte par cron-job.org est décrit à part : [`declenchement-externe.md`](declenchement-externe.md).

## 1. Logiciels

1. Installer **Python 3.12 ou plus récent** pour Windows (python.org, cocher « Add python.exe to PATH ») et **Git pour Windows**. Le PC du pilote a Python 3.14 : l'installation et les tests sont vérifiés sous Windows avec Python 3.14 à chaque PR (job CI `windows`, depuis le 2026-10-23). Sous Windows, la bibliothèque ecCodes est celle que contient le paquet `eccodes` ; sa version est notée dans chaque manifeste (`eccodes_version`).
2. Cloner le dépôt si ce n'est pas fait, puis le mettre à jour :

   ```powershell
   git clone https://github.com/louistouquet/PowAtlas.git D:\Codage\PowAtlas
   cd D:\Codage\PowAtlas
   git pull
   ```

3. Créer l'environnement Python et installer `powatlas` :

   ```powershell
   py -3.14 -m venv .venv
   .venv\Scripts\python -m pip install -e .
   .venv\Scripts\powatlas --version
   ```

   Résultat attendu : `powatlas 0.1.0`.

## 2. Jeton GitHub (à créer par le pilote)

Le téléchargement des artefacts exige un jeton, même pour un dépôt public. Sur GitHub : *Settings* → *Developer settings* → *Personal access tokens* → *Fine-grained tokens* → *Generate new token* :

- nom : `PowAtlas sync` ; expiration : 1 an ;
- *Repository access* : *Only select repositories* → `louistouquet/PowAtlas` ;
- *Permissions* → *Repository permissions* → **Actions : Read-only** (rien d'autre).

Copier le jeton dans le fichier `D:\Codage\PowAtlas\.env` (ignoré par Git, **jamais commité**) :

```text
POWATLAS_GITHUB_TOKEN=github_pat_...
```

## 3. Premier rapatriement

```powershell
cd D:\Codage\PowAtlas
.venv\Scripts\powatlas sync --data D:\Codage\PowAtlas\data
.venv\Scripts\powatlas status --data D:\Codage\PowAtlas\data --from 2026-10-22 --to 2026-11-01
```

Le premier affiche `new N, replaced 0, kept 0, rejected 0` ; le second, un tableau par source et par jour (`C` complet, `P` partiel, `M` manquant, `-` absent). Coller ces deux sorties dans la session Claude.

Codes de sortie de `sync` : 0 si tout va bien ; 1 si un artefact a été rejeté (il sera retenté) ou si le dernier artefact a plus de 48 h (voir § 5).

## 4. Tâche planifiée Windows

Dans une invite PowerShell ordinaire (pas besoin d'administrateur) :

```powershell
$a = New-ScheduledTaskAction -Execute 'D:\Codage\PowAtlas\.venv\Scripts\powatlas.exe' -Argument 'sync --data D:\Codage\PowAtlas\data --env D:\Codage\PowAtlas\.env'
$t = New-ScheduledTaskTrigger -Daily -At 12:00
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "PowAtlas sync" -Action $a -Trigger $t -Settings $s -Force
```

La tâche tourne chaque jour à midi ; si le PC était éteint à midi, elle tourne dès qu'il est rallumé (`-StartWhenAvailable`). Un passage par semaine suffit : les artefacts restent 30 jours sur GitHub. Le 2026-10-23, `schtasks /SC ONLOGON` (tâche à l'ouverture de session) a répondu « Accès refusé » sans droits d'administrateur sur le PC du pilote : ce réglage la remplace. Vérifier : `Get-ScheduledTaskInfo -TaskName "PowAtlas sync"` affiche `NextRunTime`.

## 5. Rattrapage historique (une seule fois, reprenable)

D'abord l'essai de débit, à coller dans la session Claude :

```powershell
.venv\Scripts\powatlas backfill-probe --source ifs-0p25 --day 2025-01-10
```

Puis le rattrapage, source par source, par tranches de quelques heures (il reprend là où il s'est arrêté, les unités complètes sont sautées) :

```powershell
.venv\Scripts\powatlas backfill --source aifs-single --from 2025-02-26 --to 2026-04-30 --data D:\Codage\PowAtlas\data --max-hours 3
.venv\Scripts\powatlas backfill --source ifs-0p25 --from 2024-02-01 --to 2026-04-30 --data D:\Codage\PowAtlas\data --max-hours 3
.venv\Scripts\powatlas backfill --source gfs-0p25 --from 2021-11-01 --to 2026-04-30 --data D:\Codage\PowAtlas\data --max-hours 3
```

Seuls les mois de novembre à avril et les échéances jusqu'à +78 h sont pris ([cadrage](../specs/2026-10-22-sp1-archive-design.md), § 5) : environ 185 Go téléchargés au total, moins de 1 Go gardé. Relancer la même commande jusqu'à ce qu'elle affiche `done 0` : une unité encore partielle après 3 tentatives est abandonnée et le motif est noté dans son manifeste (`given up`). Ensuite, chaque semaine, la commande GFS avec `--from` à la date d'une semaine plus tôt et `--to` à la date du jour tient l'archive GFS à jour (les jours pas encore publiés sont ignorés).

## 6. Si la collecte s'arrête

- `sync` affiche `WARNING: newest artifact is N h old` : ouvrir l'onglet *Actions* du dépôt, workflow `collect`. Si GitHub l'a désactivé (60 jours sans activité du dépôt), cliquer sur *Enable workflow*. Une issue étiquetée `collecte` signale aussi les pertes définitives et l'inactivité à 45 jours.
- Si GitHub conteste l'usage d'Actions, la collecte bascule sur ce PC avec le même code (décision 0005) : demander la procédure à une session Claude.

## 7. Sauvegarde

L'archive n'existe qu'à un seul endroit tant qu'elle n'est pas publiée. Copier `D:\Codage\PowAtlas\data\` une fois par mois sur un disque externe (par exemple `robocopy D:\Codage\PowAtlas\data E:\PowAtlas-data /MIR`).
