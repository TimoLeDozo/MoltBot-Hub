import csv
import json
import re
import time

from google import genai
from google.genai import types
from PIL import Image
from pdf2image import convert_from_path

from app_config import BAREMES_PATH, get_api_key, get_model_name, get_pdf_conversion_kwargs

PLACEHOLDER = "[À COMPLÉTER]"
GENERAL_SCORE_KEYS = (
    "SCORE_PHONOLOGIE",
    "REUSSITES_PHONOLOGIE",
    "ERREURS_PHONOLOGIE",
    "SONS_CONFONDUS_PHONO",
    "SCORE_EVO_LEXICALE",
    "REUSSITES_EVO_LEXICALE",
    "ERREURS_EVO_LEXICALE",
    "SCORE_COMP_LEXICALE",
    "REUSSITES_COMP_LEXICALE",
    "ERREURS_COMP_LEXICALE",
    "SCORE_EXP_SYNTAXIQUE",
    "ERREURS_EXP_SYNTAXIQUE",
    "SCORE_COMP_SYNTAXIQUE",
    "SCORE_GRAPHISME",
    "OBSERVATION_GRAPHISME",
    "SCORE_LABYRINTHE",
    "OBSERVATION_LABYRINTHE",
)
LECTURE_SCORE_KEYS = (
    "SCORE_LECTURE_LETTRES",
    "CONFUSIONS_LETTRES",
    "SCORE_LECTURE_SYLLABES",
    "SCORE_LECTURE_MOTS",
    "SCORE_LECTURE_DIGRAPHES",
    "ERREURS_DIGRAPHES",
    "SCORE_LECTURE_TRIGRAPHES",
    "ERREURS_TRIGRAPHES",
    "SCORE_LECTURE_PHRASES",
    "ERREURS_LECTURE_PHRASES",
    "SCORE_TOTAL_LECTURE",
    "OBSERVATION_LECTURE_TEXTE",
    "MOTS_LUS_CORRECTEMENT",
    "SCORE_COMP_LECTURE_TEXTE",
    "SCORE_ORTHO_LETTRES",
    "CONFUSIONS_ORTHO_LETTRES",
    "SCORE_ORTHO_SYLLABES",
    "ERREURS_ORTHO_SYLLABES",
    "CONFUSIONS_SONS_ORTHO",
    "OBSERVATION_ORTHO_PHRASE",
    "EXEMPLES_ORTHO_PHRASE",
    "SCORE_TOTAL_ORTHO",
    "OBSERVATION_NUMERATION",
    "OBSERVATION_CALCUL_MENTAL",
    "OBSERVATION_RECONNAISSANCE_CHIFFRES",
    "SCORE_PROBLEMES",
    "OBSERVATION_PROBLEMES",
    "SCORE_TOTAL_MATHS",
)

cle_api = get_api_key()
modele_gemini = get_model_name()
client = genai.Client(api_key=cle_api) if cle_api else None


def appeler_gemini_avec_retry(client, model, contents):
    config = types.GenerateContentConfig(response_mime_type="application/json")
    for tentative in range(3):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as erreur:
            message = str(erreur)
            if "429" in message or "RESOURCE_EXHAUSTED" in message:
                match = re.search(r"retry.*?(\d+)s", message, re.IGNORECASE)
                delai = int(match.group(1)) + 2 if match else 25
                print(f"Quota atteint. Pause de securite de {delai}s...")
                time.sleep(delai)
            else:
                raise
    raise RuntimeError("Echec apres plusieurs tentatives de quota.")


def charger_baremes(chemin_csv):
    baremes = {}
    try:
        with open(chemin_csv, mode="r", encoding="utf-8") as fichier_baremes:
            reader = csv.DictReader(fichier_baremes)
            for row in reader:
                baremes[row["Epreuve"]] = {
                    "Moyenne": float(row["Moyenne"]),
                    "-1et": float(row["-1et"]),
                    "-2et": float(row["-2et"]),
                    "-3et": float(row["-3et"]),
                }
    except Exception:
        pass
    return baremes


def _donnees_par_defaut(type_test):
    cles = LECTURE_SCORE_KEYS if type_test == "lecture" else GENERAL_SCORE_KEYS
    return {cle: PLACEHOLDER for cle in cles}


def _charger_image_analyse(chemin_fichier):
    if chemin_fichier.lower().endswith(".pdf"):
        conversion_kwargs = get_pdf_conversion_kwargs()
        try:
            images = convert_from_path(chemin_fichier, **conversion_kwargs)
        except Exception:
            if conversion_kwargs:
                images = convert_from_path(chemin_fichier)
            else:
                raise
        if not images:
            raise ValueError("Le PDF ne contient aucune page lisible.")
        return images[0]

    with Image.open(chemin_fichier) as image:
        return image.copy()


def _json_depuis_reponse(reponse):
    texte = (getattr(reponse, "text", None) or "").strip()
    texte = texte.replace("```json", "").replace("```", "").strip()
    debut = texte.find("{")
    fin = texte.rfind("}")
    if debut != -1 and fin != -1 and fin > debut:
        texte = texte[debut : fin + 1]
    donnees = json.loads(texte)
    if not isinstance(donnees, dict):
        raise ValueError("La reponse Gemini ne contient pas un objet JSON.")
    return donnees


def evaluer_score(valeur_texte, nom_epreuve, baremes):
    if nom_epreuve not in baremes or not valeur_texte or PLACEHOLDER in str(valeur_texte):
        return PLACEHOLDER, PLACEHOLDER
    match = re.search(r"(\d+([.,]\d+)?)", str(valeur_texte))
    if not match:
        return PLACEHOLDER, PLACEHOLDER
    score = float(match.group(1).replace(",", "."))
    bareme = baremes[nom_epreuve]

    if score >= bareme["Moyenne"]:
        return "la norme", "Le resultat est tout a fait dans la norme pour son age"
    if score >= bareme["-1et"]:
        return "la limite basse", "Le resultat montre une legere fragilite"
    if score >= bareme["-2et"]:
        return "-1 ET", "Le resultat est faible, signant une fragilite averee"
    if score >= bareme["-3et"]:
        return "-2 ET", "Le resultat est deficitaire (pathologique)"
    return "-3 ET (ou pire)", "Le resultat est severement deficitaire"


def analyser_grille_ia(chemin_fichier, type_test="general"):
    print(f"Analyse IA ({type_test}) : {chemin_fichier}...")
    donnees = _donnees_par_defaut(type_test)
    try:
        if client is None:
            raise RuntimeError("GOOGLE_API_KEY manquante dans le fichier .env.")

        image_source = _charger_image_analyse(chemin_fichier)

        if type_test == "lecture":
            prompt = f"""
            Analyse cette grille de lecture. Extrais les scores en JSON strict.
            TOUTES les valeurs doivent etre du texte simple (String), jamais de liste [].
            Cles: SCORE_LECTURE_LETTRES, CONFUSIONS_LETTRES, SCORE_LECTURE_SYLLABES, SCORE_LECTURE_MOTS,
            SCORE_LECTURE_DIGRAPHES, ERREURS_DIGRAPHES, SCORE_LECTURE_TRIGRAPHES, ERREURS_TRIGRAPHES,
            SCORE_LECTURE_PHRASES, ERREURS_LECTURE_PHRASES, SCORE_TOTAL_LECTURE, OBSERVATION_LECTURE_TEXTE,
            MOTS_LUS_CORRECTEMENT, SCORE_COMP_LECTURE_TEXTE, SCORE_ORTHO_LETTRES, CONFUSIONS_ORTHO_LETTRES,
            SCORE_ORTHO_SYLLABES, ERREURS_ORTHO_SYLLABES, CONFUSIONS_SONS_ORTHO, OBSERVATION_ORTHO_PHRASE,
            EXEMPLES_ORTHO_PHRASE, SCORE_TOTAL_ORTHO, OBSERVATION_NUMERATION, OBSERVATION_CALCUL_MENTAL,
            OBSERVATION_RECONNAISSANCE_CHIFFRES, SCORE_PROBLEMES, OBSERVATION_PROBLEMES, SCORE_TOTAL_MATHS.
            Si non trouve, ecris "{PLACEHOLDER}".
            """
        else:
            prompt = f"""
            Analyse cette grille de langage oral. Extrais les scores en JSON strict.
            TOUTES les valeurs doivent etre du texte simple (String), jamais de liste [].
            Cles: SCORE_PHONOLOGIE, REUSSITES_PHONOLOGIE, ERREURS_PHONOLOGIE, SONS_CONFONDUS_PHONO,
            SCORE_EVO_LEXICALE, REUSSITES_EVO_LEXICALE, ERREURS_EVO_LEXICALE, SCORE_COMP_LEXICALE,
            REUSSITES_COMP_LEXICALE, ERREURS_COMP_LEXICALE, SCORE_EXP_SYNTAXIQUE, ERREURS_EXP_SYNTAXIQUE,
            SCORE_COMP_SYNTAXIQUE, SCORE_GRAPHISME, OBSERVATION_GRAPHISME, SCORE_LABYRINTHE, OBSERVATION_LABYRINTHE.
            Si non trouve, ecris "{PLACEHOLDER}".
            """

        reponse = appeler_gemini_avec_retry(client, modele_gemini, [prompt, image_source])
        donnees.update(_json_depuis_reponse(reponse))

        baremes = charger_baremes(str(BAREMES_PATH))
        mapping = {
            "SCORE_PHONOLOGIE": "Phonologie",
            "SCORE_EVO_LEXICALE": "Evocation lexicale",
            "SCORE_COMP_LEXICALE": "Comprehension lexicale",
            "SCORE_EXP_SYNTAXIQUE": "Expression syntaxique",
            "SCORE_COMP_SYNTAXIQUE": "Comprehension syntaxique",
            "SCORE_GRAPHISME": "Graphisme",
            "SCORE_TOTAL_LECTURE": "Lecture_Phrases",
            "SCORE_COMP_LECTURE_TEXTE": "Comprehension_Texte",
            "SCORE_TOTAL_ORTHO": "Orthographe",
            "SCORE_TOTAL_MATHS": "Maths_Abrege",
        }

        for cle, epreuve in mapping.items():
            if cle in donnees:
                ecart, phrase = evaluer_score(donnees[cle], epreuve, baremes)
                donnees[f"ECART_{cle.replace('SCORE_', '')}"] = ecart
                donnees[f"PHRASE_{cle.replace('SCORE_', '')}"] = phrase

        print("Analyse IA reussie :", donnees)
        return donnees
    except Exception as erreur:
        print(f"Erreur IA : {erreur}")
        return donnees
