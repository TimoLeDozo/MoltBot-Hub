import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from PIL import Image

# =========================================================
# 1. CONFIGURATION DE L'IA ET CLÉ API
# =========================================================
load_dotenv()
cle_api = os.getenv("GOOGLE_API_KEY")

if not cle_api:
    print("⚠️ Attention : Clé API Gemini introuvable dans le fichier .env")
else:
    genai.configure(api_key=cle_api)

# =========================================================
# 2. BASE DE DONNÉES DES BARÈMES (Classe -> Épreuve -> Trimestre)
# =========================================================
# Cette base sera utilisée plus tard par notre moteur pour calculer les écarts
baremes_orthophonie = {
    "CP": {
        "Lecture_Phrases": {
            "1er_trimestre": {"Moyenne": 6.7, "-1et": 0, "-2et": 0},
            "3eme_trimestre": {"Moyenne": 16.1, "-1et": 14.1, "-2et": 12.1}
        },
        "Maths_Abrege": {
            "1er_trimestre": {"Moyenne": 10.7, "-1et": 7.5, "-2et": 4.3},
            "3eme_trimestre": {"Moyenne": 13.7, "-1et": 12.5, "-2et": 11.3}
        }
        # On pourra rajouter Phonologie, Evocation Lexicale, etc. ici.
    }
}

# =========================================================
# 3. LA FONCTION D'ANALYSE IA (VISION)
# =========================================================
def analyser_grille_ia(chemin_image_grille, type_test="general"):
    """
    Analyse l'image d'une grille avec l'IA.
    Le paramètre 'type_test' permet de choisir le bon prompt (ex: "general" ou "lecture").
    """
    print(f"🧠 Envoi de la grille {chemin_image_grille} à l'IA (Mode: {type_test})...")
    
    # On utilise le modèle Flash (rapide et très efficace pour la lecture de documents)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        image = Image.open(chemin_image_grille)
    except Exception as e:
        print(f"❌ Impossible d'ouvrir l'image {chemin_image_grille}: {e}")
        return {}

    # --- CHOIX DU PROMPT EN FONCTION DE L'ÉPREUVE ---
    if type_test == "lecture":
        consignes = """
        Tu es un assistant orthophoniste. Analyse cette grille d'évaluation de LECTURE.
        Extrais les scores manuscrits pour chaque sous-catégorie.
        Renvoie UNIQUEMENT un JSON valide, sans aucun texte autour, avec cette structure exacte :
        {
            "SCORE_LECTURE_LETTRES": "...",
            "CONFUSIONS_LETTRES": "...",
            "SCORE_LECTURE_SYLLABES": "...",
            "SCORE_LECTURE_MOTS": "...",
            "SCORE_LECTURE_DIGRAPHES": "...",
            "ERREURS_DIGRAPHES": "...",
            "SCORE_TOTAL_LECTURE": "..."
        }
        Si une information est introuvable ou illisible, mets la valeur "[À COMPLÉTER]".
        """
    else:
        # Mode "general" par défaut (pour Phono, Évocation lexicale, etc.)
        consignes = """
        Tu es l'assistant expert d'une orthophoniste. Analyse cette image d'une grille de test (EDA).
        Fais les actions suivantes :
        1. Trouve le score total (souvent écrit en bas, ex: 46/60 ou 16/20).
        2. Identifie 3 mots que l'enfant a bien prononcés ou nommés (les mots non barrés, ou avec une note > 0).
        3. Identifie 3 mots que l'enfant n'a pas réussi à dire (les mots barrés, raturés, ou avec une note de 0).
        
        Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte autour, en utilisant cette structure exacte :
        {
            "score_total": "...",
            "reussites": "mot1, mot2, mot3",
            "erreurs": "motA, motB, motC"
        }
        Si une information est introuvable ou illisible, mets la valeur "[À COMPLÉTER]".
        """
        
    # --- ENVOI À L'IA ET TRAITEMENT ---
    try:
        reponse = model.generate_content([consignes, image])
        
        # Nettoyage au cas où l'IA rajoute des balises Markdown (```json ...)
        texte_json = reponse.text.strip().replace('```json', '').replace('```', '')
        
        # Conversion du texte en vrai dictionnaire Python
        donnees_extraites = json.loads(texte_json)
        print("✅ Analyse IA réussie :", donnees_extraites)
        
        return donnees_extraites
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse IA : {e}")
        
        # En cas d'erreur IA, on renvoie des valeurs par défaut pour ne pas bloquer le Word
        if type_test == "lecture":
            return {
                "SCORE_LECTURE_LETTRES": "[À COMPLÉTER]", "CONFUSIONS_LETTRES": "[À COMPLÉTER]",
                "SCORE_LECTURE_SYLLABES": "[À COMPLÉTER]", "SCORE_LECTURE_MOTS": "[À COMPLÉTER]",
                "SCORE_LECTURE_DIGRAPHES": "[À COMPLÉTER]", "ERREURS_DIGRAPHES": "[À COMPLÉTER]",
                "SCORE_TOTAL_LECTURE": "[À COMPLÉTER]"
            }
        else:
            return {
                "score_total": "[À COMPLÉTER]",
                "reussites": "[À COMPLÉTER]",
                "erreurs": "[À COMPLÉTER]"
            }

# =========================================================
# 4. ZONE DE TEST (Pour quand tu auras une image)
# =========================================================
if __name__ == "__main__":
    # Pour tester, décommente ces lignes et mets une vraie image .jpg à côté du script
    
    # print("\n--- TEST GRILLE GÉNÉRALE ---")
    # resultat_phono = analyser_grille_ia("grille_test_image.jpg", type_test="general")
    
    # print("\n--- TEST GRILLE LECTURE ---")
    # resultat_lecture = analyser_grille_ia("grille_lecture_image.jpg", type_test="lecture")
    pass