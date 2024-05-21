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

### Bug Possible

Pendant le developpement, il se peut que l'application Nuxt ne puisse plus se rafraîchir. Vous verrez alors dans le terminal du container ce genre d'erreur.


![bug nuxt](https://ina1.sharepoint.com/:i:/r/sites/2IA/Documents%20partages/IHMIA/Screenshot%202024-05-21%20154329.png?csf=1&web=1&e=NqgDuH)

En attendant de trouver une solution, supprimer le container `dev-frontend-1` et le relancer suffit
```bash
docker rm dev-frontend-1
docker compose up -d
```
