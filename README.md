# MoltBot-Hub

Application Streamlit pour generer des comptes-rendus orthophoniques a partir d'une fiche patient et de grilles d'evaluation.

## Prerequis

- Git
- Python 3.11+ disponible via `py` ou `python`
- Poppler installe sur Windows
- Une cle `GOOGLE_API_KEY` Google AI Studio

## Installation rapide

1. Clonez le depot.
2. Lancez `install_et_lance.bat`.
3. Au premier lancement, le script :
   - cree `.venv`
   - installe les dependances Python
   - cree `.env` si besoin
   - demande la `GOOGLE_API_KEY` si elle manque
   - lance l'application Streamlit

## Configuration

Le projet versionne `.env.example`, pas la vraie cle API.

Si Poppler n'est pas detecte automatiquement, ajoutez cette ligne dans `.env` :

```env
POPPLER_PATH=C:\poppler\Library\bin
```

Le modele Gemini peut aussi etre force si besoin :

```env
GEMINI_MODEL=gemini-2.5-flash
```

## Utilisation

- Les fichiers importes sont ranges dans `data_entree/`.
- Les comptes-rendus Word generes sont ranges dans `data_sortie/`.
- Ces dossiers restent ignores par Git pour eviter de versionner des donnees patients.

## Fichiers principaux

- `interface_web.py` : interface Streamlit
- `lecteur_OCR.py` : extraction IA de la fiche patient
- `main.py` : analyse IA des grilles et calcul des baremes
- `install_et_lance.bat` : installation + lancement en un clic
