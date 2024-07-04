# Ground Control Backend



### Création du virtualenv

Si vous souhaitez lancer l'api sans le reste de la stack, exécutez les commandes suivantes depuis la racine de ce dépôt :

```bash
virtualenv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

### Lancement avec docker compose

Sinon, créez un dossier pour le projet ground-control et récupérez les projets front et back :

```bash
mkdir ground-control
git clone https://git.infra.sas.ina/ia/code/ground-control/front.git
git clone https://git.infra.sas.ina/ia/code/ground-control/backend.git
cd ground-control/backend/.dev
docker-compose up -d
```

### Alembic

Pour générer un script de révision alembic après avoir modifié les fichiers models de l'application, se positionner dans le docker ou le virtual env et éxécuter : 

```bash
alembic revision --autogenerate -m "Add model changes"
```

Pour mettre à jour la base avec la dernière révision, éxécuter : 

```bash
alembic upgrade head
```

### Documentation

La documentation utilise ![Sphinx](https://pypi.org/project/Sphinx/) et  ![myst](https://pypi.org/project/myst-parser/)
Pour générer une nouvelle version de la doc, se placer dans le répertoire /docs et éxécuter : 

```bash
sphinx-build -E -b html . ./_build/
```

### Bug Possible

Pendant le developpement, il se peut que l'application Nuxt ne puisse plus se rafraîchir. Vous verrez alors dans le terminal du container ce genre d'erreur.


![bug nuxt](https://ina1.sharepoint.com/:i:/r/sites/2IA/Documents%20partages/IHMIA/Screenshot%202024-05-21%20154329.png?csf=1&web=1&e=NqgDuH)

En attendant de trouver une solution, supprimer le container `dev-frontend-1` et le relancer suffit
```bash
docker rm dev-frontend-1
docker compose up -d
```

### Variables d'environnement :

Les variables d'environnement sont définies dans le fichier ![.env.local](https://git.infra.sas.ina/ia/code/ground-control/backend/-/blob/develop/.env.local) et sont utilisées dans la definition de l'url de connexion à la base de données (DATABASE_URL)

| NOM               | EXEMPLE           | DESCRIPTION                                                         |
|-------------------|-------------------|---------------------------------------------------------------------|
| PG_SERVER         | postgresql        | serveur de base de donnée utilisé                                   | 
| PG_DATABASE       | ground_control_db | nom de la base de données                                           | 
| PG_USERNAME       | user              | nom d'utilisateur comme login pour se connecté à la base de données | 
| PG_PASSWORD       | postgres          | le mot de passe associé au login                                    |
| PG_PORT           | 5432              | numero de port de la base de données                                | 
| DATABASE_HOSTNAME | @db               | nom du domaine                                                      |

### Configuration SSO

Le fichier `settings.yaml` permet de gerer les parametres de configuration (pour l'environnement de dev et du prod).
Il permet de stocker des paramètres de configuration de manière structurée et lisible.

| VARIABLE             | EXEMPLE                             | UTILITE                                                                          |
|----------------------|-------------------------------------|----------------------------------------------------------------------------------|
| url                  | "http://keycloak:9080/"             | L'URL de base pour le service SSO qui est Keycloak                               | 
| realm                | "ground-control"                    | le nom du lot defini dans keycloak qui gére le groupe d' utilisateurs            | 
| client_id            | "backend"                           | L'identifiant du client qui va se connecter à Keycloak (à definir dans keycloak) | 
| client_secret        | "S95Ja09NGqzB4UvXoUgbcM39IdTz8826"  | la clé secrete generer automatiquement avec keycloak                             |
