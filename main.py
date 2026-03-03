import os
import json
import csv
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from pdf2image import convert_from_path

# =========================================================
# 1. CONFIGURATION UNIFIÉE
# =========================================================
load_dotenv()
cle_api = os.getenv("GOOGLE_API_KEY")
modele_gemini = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
poppler_path = r'C:\poppler-25.12.0\Library\bin'

client = genai.Client(api_key=cle_api) if cle_api else None

# =========================================================
# 2. FONCTION DE SÉCURITÉ (RETRY ANTI-QUOTA)
# =========================================================
def appeler_gemini_avec_retry(client, model, contents):
    config = types.GenerateContentConfig(response_mime_type="application/json")
    for tentative in range(3):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                match = re.search(r"retry.*?(\d+)s", msg, re.IGNORECASE)
                delai = int(match.group(1)) + 2 if match else 25
                print(f"⏳ Quota atteint. Pause de sécurité de {delai}s...")
                time.sleep(delai)
            else:
                raise e
    raise RuntimeError("Échec après plusieurs tentatives de quota.")

# =========================================================
# 3. MOTEUR DE BARÈMES & ANALYSE
# =========================================================
def charger_baremes(chemin_csv):
    baremes = {}
    try:
        with open(chemin_csv, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                baremes[row['Epreuve']] = {
                    'Moyenne': float(row['Moyenne']),
                    '-1et': float(row['-1et']),
                    '-2et': float(row['-2et']),
                    '-3et': float(row['-3et'])
                }
    except Exception: pass
    return baremes

def evaluer_score(valeur_texte, nom_epreuve, baremes):
    if nom_epreuve not in baremes or not valeur_texte or "[À COMPLÉTER]" in str(valeur_texte):
        return "[À COMPLÉTER]", "[À COMPLÉTER]"
    match = re.search(r"(\d+([.,]\d+)?)", str(valeur_texte))
    if not match: return "[À COMPLÉTER]", "[À COMPLÉTER]"
    score = float(match.group(1).replace(',', '.'))
    b = baremes[nom_epreuve]
    
    # On enlève les "à" et les points finaux pour une intégration parfaite au Word
    if score >= b['Moyenne']: return "la norme", "Le résultat est tout à fait dans la norme pour son âge"
    if score >= b['-1et']: return "la limite basse", "Le résultat montre une légère fragilité"
    if score >= b['-2et']: return "-1 ET", "Le résultat est faible, signant une fragilité avérée"
    if score >= b['-3et']: return "-2 ET", "Le résultat est déficitaire (pathologique)"
    return "-3 ET (ou pire)", "Le résultat est sévèrement déficitaire"

def analyser_grille_ia(chemin_fichier, type_test="general"):
    print(f"🧠 Analyse IA ({type_test}) : {chemin_fichier}...")
    try:
        if chemin_fichier.lower().endswith('.pdf'):
            images = convert_from_path(chemin_fichier, poppler_path=poppler_path)
            img = images[0]
        else:
            img = Image.open(chemin_fichier)
            
        if type_test == "lecture":
            prompt = """
            Analyse cette grille de lecture. Extrais les scores en JSON strict. TOUTES les valeurs doivent être du texte simple (String), jamais de liste [].
            Clés: SCORE_LECTURE_LETTRES, CONFUSIONS_LETTRES, SCORE_LECTURE_SYLLABES, SCORE_LECTURE_MOTS, SCORE_LECTURE_DIGRAPHES, ERREURS_DIGRAPHES, SCORE_LECTURE_TRIGRAPHES, ERREURS_TRIGRAPHES, SCORE_LECTURE_PHRASES, ERREURS_LECTURE_PHRASES, SCORE_TOTAL_LECTURE, OBSERVATION_LECTURE_TEXTE, MOTS_LUS_CORRECTEMENT, SCORE_COMP_LECTURE_TEXTE, SCORE_ORTHO_LETTRES, CONFUSIONS_ORTHO_LETTRES, SCORE_ORTHO_SYLLABES, ERREURS_ORTHO_SYLLABES, CONFUSIONS_SONS_ORTHO, OBSERVATION_ORTHO_PHRASE, EXEMPLES_ORTHO_PHRASE, SCORE_TOTAL_ORTHO, OBSERVATION_NUMERATION, OBSERVATION_CALCUL_MENTAL, OBSERVATION_RECONNAISSANCE_CHIFFRES, SCORE_PROBLEMES, OBSERVATION_PROBLEMES, SCORE_TOTAL_MATHS.
            Si non trouvé, écris "[À COMPLÉTER]".
            """
        else:
            prompt = """
            Analyse cette grille de langage oral. Extrais les scores en JSON strict. TOUTES les valeurs doivent être du texte simple (String), jamais de liste [].
            Clés: SCORE_PHONOLOGIE, REUSSITES_PHONOLOGIE, ERREURS_PHONOLOGIE, SONS_CONFONDUS_PHONO, SCORE_EVO_LEXICALE, REUSSITES_EVO_LEXICALE, ERREURS_EVO_LEXICALE, SCORE_COMP_LEXICALE, REUSSITES_COMP_LEXICALE, ERREURS_COMP_LEXICALE, SCORE_EXP_SYNTAXIQUE, ERREURS_EXP_SYNTAXIQUE, SCORE_COMP_SYNTAXIQUE, SCORE_GRAPHISME, OBSERVATION_GRAPHISME, SCORE_LABYRINTHE, OBSERVATION_LABYRINTHE.
            Si non trouvé, écris "[À COMPLÉTER]".
            """

        reponse = appeler_gemini_avec_retry(client, modele_gemini, [prompt, img])
        texte = reponse.text.replace("```json", "").replace("```", "").strip()
        donnees = json.loads(texte)
        
        # Calcul des barèmes
        baremes = charger_baremes("Baremes_Extrapoles_CP.csv")
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
        
        for k, v in mapping.items():
            if k in donnees:
                ecart, phrase = evaluer_score(donnees[k], v, baremes)
                donnees[f"ECART_{k.replace('SCORE_', '')}"] = ecart
                donnees[f"PHRASE_{k.replace('SCORE_', '')}"] = phrase
        print("✅ Analyse IA réussie :", donnees)
        return donnees
    except Exception as e:
        print(f"❌ Erreur IA : {e}")
        return {}
