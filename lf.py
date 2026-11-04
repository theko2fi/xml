import urllib2
import sys
import os

BASE_URL = "https://raw.githubusercontent.com/USER/REPO/BRANCH/"
LOCAL_DIR = "/tmp/xlrelease_project"

# Liste des fichiers à récupérer
FILES = [
    "config.py",
    "utils.py",
    "main.py",
    "services/__init__.py",
    "services/api.py",
    "services/authentication.py",
    "services/database.py"
]

def download_file(path):

    url = BASE_URL + path
    response = urllib2.urlopen(url)
    content = response.read()
    response.close()

    local_path = os.path.join(LOCAL_DIR, path)
    local_parent = os.path.dirname(local_path)

    if not os.path.exists(local_parent):
        os.makedirs(local_parent)

    with open(local_path, "wb") as f:
        f.write(content)

    print("Downloaded: " + path)


# Télécharger les fichiers
for path in FILES:
    download_file(path)

# Ajouter le projet au chemin Python
sys.path.insert(0, LOCAL_DIR)

# Importer normalement
from services.api import ma_fonction

ma_fonction()
