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

La tâche lance chaque jour le script [`scripts/pc-daily.ps1`](../../scripts/pc-daily.ps1) :
1. `sync` ;
2. une tranche d'au plus 3 heures du rattrapage historique de chaque source (§ 5) ;
3. de ce fait, la mise à jour de GFS, qui n'est collecté que sur ce PC.

Tout est écrit dans `data\pc-daily.log`. Le script vient du dépôt : un `git pull` le met à jour sans toucher à la tâche.

Dans une invite PowerShell ordinaire, une ligne à la fois. Les lignes sont courtes exprès : le 2026-10-23, une ligne trop longue a été coupée au copier-coller.

```powershell
$ps1 = 'D:\Codage\PowAtlas\scripts\pc-daily.ps1'
$arg = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File $ps1"
$a = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg
$t = New-ScheduledTaskTrigger -Daily -At 12:00
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable
$s.DisallowStartIfOnBatteries = $false
$s.StopIfGoingOnBatteries = $false
$s.RunOnlyIfNetworkAvailable = $true
Register-ScheduledTask -TaskName "PowAtlas sync" -Action $a -Trigger $t -Settings $s -Force
```

Fonctionnement :
- La tâche tourne chaque jour à midi. Si le PC était éteint à midi, elle tourne quelques minutes après son allumage suivant (`-StartWhenAvailable`), y compris sur batterie : allumé à 13 h, elle part vers 13 h ; allumé seulement le lendemain matin, elle part ce matin-là. Elle tourne donc chaque jour où le PC est allumé, à n'importe quelle heure.
- Un passage par semaine suffit : les artefacts restent 30 jours sur GitHub.
- `-ExecutionPolicy Bypass` ne vaut que pour ce lancement ; il ne change pas le réglage de Windows.
- Constat du 2026-10-23 : malgré `-WindowStyle Hidden`, une fenêtre noire vide s'ouvre pendant la tâche (cause non établie ; hypothèse : le terminal par défaut des Windows récents). Elle se réduit, mais **ne doit pas être fermée**, sinon la tâche s'arrête ; tout reprend au lancement suivant.
- Sans réseau, rien n'est lancé : la tâche attend le réseau, et le script attend jusqu'à 10 minutes que `github.com` réponde. Sinon, un rattrapage hors ligne gaspillerait les 3 tentatives de chaque unité.

Constats du 2026-10-23 sur le PC du pilote :
- `schtasks /SC ONLOGON` (tâche à l'ouverture de session) a répondu « Accès refusé », faute de droits d'administrateur ;
- la tâche de ce paragraphe, elle, a été créée sans droits d'administrateur (état `Ready`) ;
- `LastTaskResult` 267011, soit 0x41303, veut dire « pas encore lancée ».

Pour vérifier :
- `Get-ScheduledTaskInfo -TaskName "PowAtlas sync"` affiche `NextRunTime` ;
- `Get-Content D:\Codage\PowAtlas\data\pc-daily.log -Tail 20` montre le dernier passage.

## 5. Rattrapage historique (reprenable)

Ce qui est pris : seuls les mois de novembre à avril et les échéances jusqu'à +78 h ([cadrage](../specs/2026-10-22-sp1-archive-design.md), § 5). Cela fait environ 185 Go téléchargés au total, et moins de 1 Go gardé.

Périodes (catalogue, `settings.backfill`) :
- AIFS : 2025-02-26 au 2026-04-30 ;
- IFS : 2024-02-01 au 2026-04-30 ;
- GFS : depuis le 2021-11-01, sans fin.

Les essais de débit du 2026-10-23 (4,9 et 5,0 requêtes par seconde) donnent un plancher d'environ 24 h de téléchargement. Le rattrapage reprend là où il s'est arrêté, et les unités complètes sont sautées. Quand le serveur ralentit (HTTP 503), `powatlas` espace ses requêtes jusqu'à 2 s et réessaie chacune jusqu'à 10 fois, avec des pauses de 60 s au plus. Dans le journal, chaque run apparaît deux fois : une ligne `collecting` au début, puis une ligne d'état avec sa durée, ses requêtes et ses reprises. Une unité restée partielle seulement à cause de ces refus est reprise au passage suivant, sans compter comme une tentative (10 passages au plus). Une unité encore partielle après 3 vraies tentatives est abandonnée, et le motif est noté dans son manifeste (`given up`). Couper le PC ne casse rien : chaque fichier est écrit puis renommé d'un coup, et une unité interrompue est refaite au passage suivant ([décision 0006](../decisions/0006-rattrapage-sur-le-pc-automatique.md)).

**Sans rien faire**, la tâche du § 4 avance chaque jour de 3 h au plus par source. Avec le rythme adaptatif, mesuré le 2026-10-23 à environ 20 s par run AIFS, le rattrapage complet prend quelques jours d'allumage : l'AIFS en moins de 3 h, l'IFS en une dizaine d'heures [estimation], GFS encore à mesurer. Elle ne lance pas de rattrapage si un autre `powatlas` tourne déjà.

**Pour savoir où on en est**, depuis `D:\Codage\PowAtlas` (la tâche l'écrit aussi à la fin de chaque passage dans `data\pc-daily.log`) :

```powershell
cd D:\Codage\PowAtlas
.venv\Scripts\powatlas progress --data data
```

Une barre par source, par exemple `ifs-0p25     [#########---------------------]  140/452   31 %`, et `finished` au bout de la ligne quand la source est finie ; `given up` signale des runs abandonnés. GFS n'a pas de fin : sa barre retombe un peu sous 100 % à chaque nouveau jour d'hiver, jusqu'au passage suivant.

**Pour aller plus vite**, lancer à la main une source à la fois, en lignes courtes, depuis `D:\Codage\PowAtlas`. Ne pas le faire pendant que la tâche de midi tourne, sinon deux rattrapages écriraient les mêmes fichiers (`Get-Process powatlas` ne doit rien afficher). Les périodes viennent du catalogue :

```powershell
cd D:\Codage\PowAtlas
Set-Alias pa D:\Codage\PowAtlas\.venv\Scripts\powatlas.exe
pa backfill --source ifs-0p25 --data data
pa backfill --source gfs-0p25 --data data
```

Chaque commande se termine par une ligne `done N (partial P), skipped S, given up G`. `--max-hours 3` ajouté en fin de ligne l'arrête proprement au bout de 3 h.

## 6. Si la collecte s'arrête

- `data\pc-daily.log` ou `sync` affiche `WARNING: newest artifact is N h old` : ouvrir l'onglet *Actions* du dépôt, workflow `collect`. Si GitHub l'a désactivé (60 jours sans activité du dépôt), cliquer sur *Enable workflow*. Une issue étiquetée `collecte` signale aussi les pertes définitives et l'inactivité à 45 jours.
- Si GitHub conteste l'usage d'Actions, la collecte bascule sur ce PC avec le même code (décision 0005) : demander la procédure à une session Claude.

## 7. Sauvegarde

L'archive n'existe qu'à un seul endroit tant qu'elle n'est pas publiée. Copier `D:\Codage\PowAtlas\data\` une fois par mois sur un disque externe (par exemple `robocopy D:\Codage\PowAtlas\data E:\PowAtlas-data /MIR`).
