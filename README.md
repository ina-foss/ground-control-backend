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



uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
