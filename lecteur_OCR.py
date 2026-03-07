import json
import re
import time

from google import genai
from google.genai import types
from pdf2image import convert_from_path

from app_config import get_api_key, get_model_name, get_pdf_conversion_kwargs

PLACEHOLDER = "[À COMPLÉTER]"
DEFAULT_PATIENT_DATA = {
    "NOM_PATIENT": PLACEHOLDER,
    "PRENOM_PATIENT": PLACEHOLDER,
    "DATE_NAISSANCE": PLACEHOLDER,
    "AGE_PATIENT": PLACEHOLDER,
    "NUM_SECU": PLACEHOLDER,
    "CLASSE_SCOLAIRE": PLACEHOLDER,
    "ADRESSE_PATIENT": PLACEHOLDER,
}

cle_api = get_api_key()
modele_gemini = get_model_name()
client = genai.Client(api_key=cle_api) if cle_api else None


def _charger_premiere_page_pdf(chemin_pdf):
    conversion_kwargs = get_pdf_conversion_kwargs()
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
    texte = (getattr(reponse, "text", None) or "").strip()
    texte = texte.replace("```json", "").replace("```", "").strip()
    debut = texte.find("{")
    fin = texte.rfind("}")
    if debut != -1 and fin != -1 and fin > debut:
        texte = texte[debut : fin + 1]

    try:
        donnees = json.loads(texte)
        return donnees if isinstance(donnees, dict) else {}
    except Exception:
        return {}


def appeler_gemini_avec_retry(client, model, contents, max_retries=3):
    config_json = types.GenerateContentConfig(response_mime_type="application/json")
    for tentative in range(1, max_retries + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config_json,
            )
        except Exception as erreur:
            message = str(erreur)
            if "429" in message or "RESOURCE_EXHAUSTED" in message:
                match = re.search(r"retry.*?(\d+)s", message, re.IGNORECASE)
                delai = int(match.group(1)) + 2 if match else 25
                if tentative < max_retries:
                    print(
                        f"Quota atteint. Attente de securite de {delai}s "
                        f"(tentative {tentative + 1}/{max_retries})..."
                    )
                    time.sleep(delai)
                else:
                    raise
            else:
                raise


def extraire_fiche_renseignement(chemin_pdf):
    print(f"Conversion de {chemin_pdf} en image...")
    try:
        if client is None:
            raise RuntimeError("GOOGLE_API_KEY manquante dans le fichier .env.")

        image_page_1 = _charger_premiere_page_pdf(chemin_pdf)
        print(f"Lecture de la fiche via Gemini ({modele_gemini})...")

        prompt = f"""
        Voici une fiche de renseignements d'un patient en orthophonie (probablement remplie a la main).
        Lis attentivement le document et extrais les informations.
        Renvoie UNIQUEMENT un objet JSON valide avec ces cles exactes :
        {{
            "NOM_PATIENT": "Nom de famille du patient",
            "PRENOM_PATIENT": "Prenom du patient",
            "DATE_NAISSANCE": "Date de naissance",
            "AGE_PATIENT": "Age lu sur la fiche ou calcule",
            "NUM_SECU": "Numero de securite sociale",
            "CLASSE_SCOLAIRE": "Classe de l'enfant (ex: CP, CE1...)",
            "ADRESSE_PATIENT": "Adresse postale complete"
        }}
        Si une information est totalement illisible ou absente de la fiche, ecris "{PLACEHOLDER}".
        N'ajoute aucun texte avant ou apres le JSON.
        """

        reponse = appeler_gemini_avec_retry(client, modele_gemini, [prompt, image_page_1])
        donnees_patient = DEFAULT_PATIENT_DATA.copy()
        donnees_patient.update(_json_depuis_reponse(reponse))
        print("Donnees extraites avec succes :", donnees_patient)
        return donnees_patient

    except Exception as erreur:
        print(f"Erreur lors de la lecture de la fiche par l'IA : {erreur}")
        return DEFAULT_PATIENT_DATA.copy()
