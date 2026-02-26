import pytesseract
from pdf2image import convert_from_path
import re

# IMPORTANT : Il faudra indiquer à Python où Tesseract est installé sur ton ordi
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Exemple pour Windows

def extraire_fiche_renseignement(chemin_pdf):
    print("🔄 Conversion du PDF en image...")
    # Convertir la première page du PDF en image
    images = convert_from_path(chemin_pdf)
    image_page_1 = images[0]

    print("🔍 Analyse de l'image par l'OCR...")
    # Extraire le texte (en précisant que c'est du français)
    texte_brut = pytesseract.image_to_string(image_page_1, lang='fra')
    
    # Dictionnaire qui va contenir nos futurs "Placeholders"
    donnees_patient = {}

    # --- LISTE DE NOS RECHERCHES (Regex) ---
    # On cherche le mot clé, les éventuels espaces/deux-points, et on capture la suite (.*)
    patterns = {
        "NOM_PATIENT": r"NOM DU PATIENT\s*[:\.]?\s*(.*)",
        "DATE_NAISSANCE": r"DATE DE NAISSANCE\s*[:\.]?\s*(.*)",
        "NUM_SECU": r"NUMERO DE SECURITE SOCIALE\s*[:\.]?\s*(.*)",
        "ECOLE": r"ECOLE\s*[:\.]?\s*(.*)",
        "CLASSE": r"CLASSE\s*[:\.]?\s*(.*)"
    }

    # On applique chaque recherche sur le texte brut
    for cle, regex in patterns.items():
        match = re.search(regex, texte_brut, re.IGNORECASE)
        if match:
            # On nettoie un peu le texte trouvé (enlever les espaces en trop)
            donnees_patient[cle] = match.group(1).strip()
        else:
            donnees_patient[cle] = "NON TROUVÉ"

    return donnees_patient

# --- TEST DU SCRIPT ---
if __name__ == "__main__":
    fichier_test = "Feuille de renseignement.pdf"
    resultats = extraire_fiche_renseignement(fichier_test)
    
    print("\n✅ Résultats de l'extraction :")
    for cle, valeur in resultats.items():
        print(f"{{{{{cle}}}}} -> {valeur}")