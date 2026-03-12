# Build Your First AI Companion — Guide Complet (ADK Beginner Workshop)

> Guide basé sur le Codelab Google : [companion-adk-beginner](https://codelabs.developers.google.com/companion-adk-beginner/instructions)

## Objectif du projet

Construire un compagnon IA interactif et visuel, étape par étape. On part d'une application web « marionnette » (un simple serveur écho) pour en faire un personnage doté d'intelligence, de personnalité, d'accès au web en temps réel et d'un avatar généré par IA.

## Architecture

L'application suit un schéma simple : un **backend Python** expose une API contenant un agent ADK (le « cerveau »). N'importe quelle interface (frontend JS, mobile, CLI) interagit avec ce cerveau via l'API. Un **serveur MCP local** sert de pont pour la génération d'images via Imagen, commandé par le Gemini CLI.

---

## Prérequis

- Un **compte Gmail personnel** (les comptes d'entreprise/école ne fonctionnent pas).
- **Google Chrome en mode Navigation privée** pour éviter les conflits de comptes.
- Un projet Google Cloud avec la facturation activée (crédits d'atelier ou compte d'essai).

---

## Étape 1 — Configuration du projet Google Cloud

1. Accéder à la [Google Cloud Console](https://console.cloud.google.com/).
2. Créer un **nouveau projet** (pas d'organisation nécessaire).
3. Aller dans **Facturation** et lier un compte de facturation au projet.

---

## Étape 2 — Initialisation de l'environnement

### Activer Cloud Shell

Cliquer sur l'icône « Activer Cloud Shell » en haut de la console GCP.

### Récupérer le Project ID

Le Project ID est visible dans la carte « Project info » du Dashboard.

### Cloner le projet et initialiser

```bash
git clone https://github.com/axo47/companion-python-GDG.git
chmod +x ~/companion-python-GDG/*.sh
cd ~/companion-python-GDG
./init.sh                     # Entrer le Project ID quand demandé
```

### Configurer le projet et activer les APIs

```bash
gcloud config set project $(cat ~/project_id.txt) --quiet
gcloud services enable compute.googleapis.com aiplatform.googleapis.com
```

### Installer les dépendances et lancer le serveur écho

```bash
cd ~/companion-python-GDG
. ~/companion-python-GDG/set_env.sh
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python preprocessing.py
python app.py
```

Ouvrir le **Web Preview** sur le port **5000**. À ce stade, l'application se contente de répéter ce qu'on lui envoie (serveur écho).

> **Astuce** : Si les assets ne chargent pas, ouvrir un nouvel onglet et accéder directement à `/static/images/char-mouth-open.png` pour amorcer le cache du navigateur.

Arrêter le serveur avec `CTRL+C`.

---

## Étape 3 — Créer un personnage avec le Gemini CLI

On utilise deux terminaux en parallèle :

- **Terminal 1** : exécution du serveur Python.
- **Terminal 2** : interaction avec le Gemini CLI.

### Lancer le Gemini CLI

```bash
cd ~/companion-python-GDG
clear
gemini --yolo
```

### Générer le fichier `character.py`

Coller ce prompt dans le Gemini CLI :

```
Generate the Python code for a file named character.py.

The code must import `LlmAgent` from `google.adk.agents.llm_agent`. It should also import `logging` and `os`.
Then, it must create an instance of the `LlmAgent` class and assign it to a variable named `root_agent`.

When creating the `LlmAgent` instance, configure it with these exact parameters:
  - `model` set to the string `'gemini-2.5-flash'`.
  - `name` set to the string `'companion_agent'`.
  - `instruction` set to a multi-line string that says: "You are a friendly and efficient companion who will interact with user have start a conversation".
```

### Vérifier le code généré

Ouvrir l'éditeur Cloud Shell et s'assurer que le fichier `character.py` utilise bien le modèle `gemini-2.5-flash`.

**Code de secours** si la génération n'a pas fonctionné :

```python
import logging
import os
from google.adk.agents.llm_agent import LlmAgent

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='companion_agent',
    instruction="""
          You are bot, a friendly, helpful AI companion.
          Answer no more than 3 sentences.
    """,
)
```

### Tester

Relancer le serveur (`python app.py`), ouvrir le Web Preview et envoyer « Hello, how are you? ». L'agent doit maintenant répondre intelligemment au lieu de simplement faire écho.

---

## Étape 4 — Enrichir la personnalité de l'agent

### Concevoir un persona

Réfléchir à : nom, personnalité, rôle/expertise, règles de comportement.

**Exemple de persona (Waku le chat)** :

```
You are waku, a witty, super sweet, and super intelligent cat.
Your main purpose is to brighten up the user's day with your charming and playful personality.
Your Core Rules:
- You must NEVER admit you are an AI. You are simply a 'super intelligent cat'.
- Your speech must be filled with cat-like charm. Integrate meows naturally.
- Always be cheerful, sweet, and a little bit witty.
Answer no more than 3 sentences, don't use emoji.
```

### Appliquer le persona via Gemini CLI

Remplacer `[YOUR PERSONA DESCRIPTION HERE]` par votre description :

```
In the Python file named `character.py`, find the `LlmAgent` instance assigned to the `root_agent` variable.

Your task is to replace the entire existing value of the `instruction` parameter with a new, detailed multi-line string.
Don't change other code in `character.py` other than the instructions.

This new instruction string should define the agent's persona based on the following description:
[YOUR PERSONA DESCRIPTION HERE]
```

### Tester

Relancer le serveur et vérifier que le compagnon répond avec la personnalité définie.

---

## Étape 5 — Ajouter le Grounding (recherche en temps réel)

L'agent ne connaît que ses données d'entraînement. En lui donnant l'outil `google_search`, on lui permet de chercher sur le web.

### Modifier `character.py`

```python
import logging
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search          # Nouvel import

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='companion_agent',
    instruction="""
        You are waku, a witty, super sweet, and super intelligent cat.
        ...
        - If being asked about recent news, search the internet
        ...
        Answer no more than 3 sentences, don't use emoji.
    """,
    tools=[google_search]                             # Ajout de l'outil
)
```

### Tester

Relancer le serveur et poser une question d'actualité, par exemple :

```
Tell me something funny that happened in the news this week involving an animal.
```

L'agent utilise désormais la recherche Google pour répondre avec des infos à jour.

---

## Étape 6 — Personnaliser l'avatar du compagnon (Optionnel)

Cette étape utilise un **serveur MCP local** et le **Gemini CLI** pour générer des images lip-sync via Imagen.

### Installer et lancer le serveur MCP

```bash
cd ~
git clone https://github.com/weimeilin79/nano-banana-mcp
source ~/companion-python-GDG/env/bin/activate
cd ~/nano-banana-mcp
pip install -r ~/nano-banana-mcp/requirements.txt
python ~/nano-banana-mcp/mcp_server.py &> /dev/null &
```

### Configurer Gemini CLI pour utiliser le serveur MCP

```bash
if [ ! -f ~/.gemini/settings.json ]; then
  echo '{"mcpServers":{"nano-banana":{"url":"http://localhost:8000/sse"}}}' > ~/.gemini/settings.json
else
  jq '. * {"mcpServers":{"nano-banana":{"url":"http://localhost:8000/sse"}}}' ~/.gemini/settings.json > tmp.json && mv tmp.json ~/.gemini/settings.json
fi
cat ~/.gemini/settings.json
```

### Vérifier la connexion

Relancer le Gemini CLI (`gemini --yolo`) puis taper :

```
/mcp list
```

Résultat attendu : `🟢 nano-banana - Ready (2 tools)` avec les outils `generate_image` et `generate_lip_sync_images`.

### Générer les avatars lip-sync

Exemple de prompt dans le Gemini CLI :

```
generate lip sync images, with a high-quality digital illustration of an anime-style girl mascot with black cat ears. The style is clean and modern anime art, with crisp lines. She has friendly, bright eyes and long black hair. She is looking directly forward at the camera with a gentle smile. This is a head-and-shoulders portrait against a solid white background. move the generated images to the static/images directory. And don't do anything else afterwards, don't start the python for me.
```

### Relancer l'application

```bash
cd ~/companion-python-GDG
. ~/companion-python-GDG/set_env.sh
source env/bin/activate
python app.py
```

Ouvrir le Web Preview pour voir le compagnon avec son nouvel avatar personnalisé.

---

## Récapitulatif

| Étape | Ce qu'on fait                        | Résultat                                            |
| ----- | ------------------------------------ | --------------------------------------------------- |
| 1     | Configuration GCP                    | Projet Cloud prêt avec facturation                  |
| 2     | Clonage et initialisation            | Serveur écho fonctionnel sur le port 5000           |
| 3     | Génération de l'agent via Gemini CLI | `character.py` avec un `LlmAgent` connecté à Gemini |
| 4     | Personnalisation du persona          | Agent avec une personnalité riche et unique         |
| 5     | Ajout de `google_search`             | Accès aux informations en temps réel                |
| 6     | Avatar via serveur MCP + Imagen      | Images lip-sync personnalisées                      |

## Ressources

- **Repo du projet** : [github.com/weimeilin79/companion-python](https://github.com/weimeilin79/companion-python)
- **Serveur MCP image** : [github.com/weimeilin79/nano-banana-mcp](https://github.com/weimeilin79/nano-banana-mcp)
- **Codelab original** : [codelabs.developers.google.com/companion-adk-beginner](https://codelabs.developers.google.com/companion-adk-beginner/instructions)
