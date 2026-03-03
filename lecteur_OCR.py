import json
import os
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pdf2image import convert_from_path

# =========================================================
# 1. CONFIGURATION IA
# =========================================================
load_dotenv()
cle_api = os.getenv("GOOGLE_API_KEY")
modele_gemini = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
poppler_path = os.getenv("POPPLER_PATH", r"C:\poppler-25.12.0\Library\bin")

client = genai.Client(api_key=cle_api) if cle_api else None

# =========================================================
# 2. OUTILS COMMUNS
# =========================================================
def _charger_premiere_page_pdf(chemin_pdf):
    """Convertit un PDF en image (première page) avec fallback."""
    conversion_kwargs = {}
    if poppler_path and os.path.isdir(poppler_path):
        conversion_kwargs["poppler_path"] = poppler_path
    try:
        images = convert_from_path(chemin_pdf, **conversion_kwargs)
    except Exception:
        if conversion_kwargs:
            images = convert_from_path(chemin_pdf)
        else:
            raise
    if not images:
        raise ValueError("Le PDF ne contient aucune page lisible.")
    return images[0]

def _json_depuis_reponse(reponse):
    """Extrait proprement un objet JSON de la réponse Gemini."""
    texte = (getattr(reponse, "text", None) or "").strip()
    texte = texte.replace("```json", "").replace("```", "").strip()
    debut = texte.find("{")
    fin = texte.rfind("}")
    if debut != -1 and fin != -1 and fin > debut:
        texte = texte[debut : fin + 1]
    
    try:
        donnees = json.loads(texte)
        return donnees
    except:
        return {}

# =========================================================
# 3. RETRY API GEMINI (Anti Quota)
# =========================================================
def appeler_gemini_avec_retry(client, model, contents, max_retries=3):
    config_json = types.GenerateContentConfig(response_mime_type="application/json")
    for tentative in range(1, max_retries + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config_json,
            )
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                match = re.search(r"retry.*?(\d+)s", msg, re.IGNORECASE)
                delai = int(match.group(1)) + 2 if match else 25
                if tentative < max_retries:
                    print(f"⏳ Quota atteint. Attente de sécurité de {delai}s (tentative {tentative + 1}/{max_retries})...")
                    time.sleep(delai)
                else:
                    raise
            else:
                raise

# =========================================================
# 4. FONCTION DE LECTURE INTELLIGENTE
# =========================================================
def extraire_fiche_renseignement(chemin_pdf):
    print(f"🔄 Conversion de {chemin_pdf} en image...")
    try:
        image_page_1 = _charger_premiere_page_pdf(chemin_pdf)
        print(f"🧠 Lecture de la fiche via Gemini ({modele_gemini})...")

        prompt = """
        Voici une fiche de renseignements d'un patient en orthophonie (probablement remplie à la main).
        Lis attentivement le document et extrais les informations.
        Renvoie UNIQUEMENT un objet JSON valide avec ces clés exactes :
        {
            "NOM_PATIENT": "Nom de famille du patient",
            "PRENOM_PATIENT": "Prénom du patient",
            "DATE_NAISSANCE": "Date de naissance",
            "AGE_PATIENT": "Age lu sur la fiche ou calculé",
            "NUM_SECU": "Numéro de sécurité sociale",
            "CLASSE_SCOLAIRE": "Classe de l'enfant (ex: CP, CE1...)",
            "ADRESSE_PATIENT": "Adresse postale complète"
        }
        Si une information est totalement illisible ou absente de la fiche, écris "[À COMPLÉTER]".
        N'ajoute aucun texte avant ou après le JSON.
        """

        reponse = appeler_gemini_avec_retry(client, modele_gemini, [prompt, image_page_1])
        donnees_patient = _json_depuis_reponse(reponse)
        print("✅ Données extraites avec succès :", donnees_patient)
        return donnees_patient

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la fiche par l'IA : {e}")
        return {
            "NOM_PATIENT": "[À COMPLÉTER]", "PRENOM_PATIENT": "[À COMPLÉTER]",
            "DATE_NAISSANCE": "[À COMPLÉTER]", "AGE_PATIENT": "[À COMPLÉTER]",
            "NUM_SECU": "[À COMPLÉTER]", "CLASSE_SCOLAIRE": "[À COMPLÉTER]",
            "ADRESSE_PATIENT": "[À COMPLÉTER]"
        }