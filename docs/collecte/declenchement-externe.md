# Déclencher la collecte toutes les heures depuis cron-job.org

Guide du 2026-10-22, pour un débutant. Le 2026-10-22, les déclenchements planifiés (`schedule`) du workflow `collect` ne partaient pas sur GitHub, alors que les lancements manuels fonctionnaient. Ce guide fait appeler le workflow **toutes les heures** par un service gratuit, [cron-job.org](https://cron-job.org/en/) (« absolutely free and financed entirely by voluntary donations », page consultée le 2026-10-22).

Chaque appel lance la tâche `auto`, qui collecte tout ce qui est publié et pas encore complet, toutes sources confondues. Un appel manqué est donc rattrapé à l'heure suivante. Si les planifications de GitHub se mettent à marcher, elles s'ajoutent sans doublon : une unité déjà complète est sautée.

Il faut deux choses : un **jeton GitHub** qui a seulement le droit de lancer les workflows de ce dépôt, et une **tâche** sur cron-job.org.

## 1. Créer le jeton GitHub (5 minutes)

1. Se connecter sur https://github.com avec le compte `louistouquet`.
2. Cliquer sur sa photo en haut à droite, puis **Settings**.
3. Dans la colonne de gauche, tout en bas : **Developer settings**.
4. **Personal access tokens** → **Fine-grained tokens** → bouton **Generate new token**.
5. Remplir :
   - **Token name** : `PowAtlas cron-job` ;
   - **Expiration** : *Custom*, un an (le noter dans un agenda pour le renouveler) ;
   - **Repository access** : **Only select repositories**, puis choisir `louistouquet/PowAtlas` ;
   - **Permissions** → **Repository permissions** → **Actions** : choisir **Read and write**. Ne rien changer d'autre (*Metadata* passe tout seul en lecture).
6. Cliquer **Generate token**, puis **copier** le texte qui commence par `github_pat_`. Il ne sera plus jamais affiché : le coller tout de suite à l'étape 2.

Ce jeton permet seulement de lancer, annuler ou effacer des workflows et des artefacts de ce dépôt. Ne le mettre **nulle part ailleurs** que sur cron-job.org ; ne jamais le coller dans le dépôt, une issue ou une conversation.

## 2. Créer la tâche sur cron-job.org (10 minutes)

1. Aller sur https://console.cron-job.org/signup et créer un compte gratuit (adresse e-mail et mot de passe solide), puis confirmer l'adresse avec l'e-mail reçu.
2. Une fois connecté : **Cronjobs** → **Create cronjob**.
3. Onglet **Common** :
   - **Title** : `PowAtlas collect auto` ;
   - **URL** : `https://api.github.com/repos/louistouquet/PowAtlas/actions/workflows/collect.yml/dispatches` ;
   - **Execution schedule** : *Custom* (ou « every hour ») avec **minute 17**, toutes les heures, tous les jours ; fuseau **UTC** si le choix est proposé ;
   - laisser **Enable job** coché.
4. Onglet **Advanced** :
   - **Request method** : **POST** ;
   - **Request headers** : ajouter ces trois en-têtes (bouton *Add*), en remplaçant `COLLER_ICI_LE_JETON` par le jeton de l'étape 1 :

     | Key | Value |
     |---|---|
     | `Authorization` | `Bearer COLLER_ICI_LE_JETON` |
     | `Accept` | `application/vnd.github+json` |
     | `X-GitHub-Api-Version` | `2022-11-28` |

   - **Request body** :

     ```json
     {"ref": "main", "inputs": {"task": "auto"}}
     ```

   - **Notifications** (onglet ou section *Notifications*) : cocher l'envoi d'un e-mail en cas d'échec.
5. Enregistrer (**Create** ou **Save**).
6. Tester tout de suite : dans la liste des cronjobs, bouton **Test run** (ou *Execute now*). Réponse attendue : **204 No Content** (ou 200), ce qui veut dire que GitHub a accepté. Une réponse **401** ou **403** veut dire que le jeton est faux ou n'a pas la permission *Actions : Read and write* ; **404** veut dire que l'URL est mal recopiée.

## 3. Vérifier que ça marche

- Sur GitHub : dépôt `PowAtlas` → onglet **Actions** → workflow **collect**. Un nouveau run *workflow_dispatch* doit apparaître à chaque heure et 17 minutes.
- Sur cron-job.org : **History** de la tâche, avec une réponse 204 à chaque exécution.
- Dire à une session Claude « vérifie les déclenchements de cron-job.org » : elle liste les runs du workflow et contrôle qu'il y en a un par heure.

## 4. Si un jour ça s'arrête

- E-mail d'échec de cron-job.org avec une erreur 401 : le jeton a expiré. Refaire l'étape 1, puis remplacer la valeur de l'en-tête `Authorization` dans la tâche.
- Pour arrêter : décocher **Enable job** sur cron-job.org.
