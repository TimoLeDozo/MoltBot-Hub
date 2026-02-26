import streamlit as st
import os
from docx import Document

# Importation de tes propres scripts !
from lecteur_OCR import extraire_fiche_renseignement
from main import analyser_grille_ia

# --- INITIALISATION DES DOSSIERS ---
# On s'assure que les dossiers existent pour ne pas faire planter le script
os.makedirs("data_entree", exist_ok=True)
os.makedirs("data_sortie", exist_ok=True)

# --- FONCTION UTILITAIRE : SAUVEGARDE DES FICHIERS ---
def sauvegarder_fichier_upload(fichier_upload, nom_fichier):
    chemin = os.path.join("data_entree", nom_fichier)
    with open(chemin, "wb") as f:
        f.write(fichier_upload.getbuffer())
    return chemin

# --- FONCTION UTILITAIRE : GÉNÉRATION DU WORD ---
def generer_word(chemin_modele, chemin_sortie, donnees):
    doc = Document(chemin_modele)
    
    # Remplacement dans les paragraphes
    for p in doc.paragraphs:
        for cle, valeur in donnees.items():
            balise = f"{{{{{cle}}}}}"
            if balise in p.text:
                p.text = p.text.replace(balise, str(valeur))
                
    # Remplacement dans les tableaux (en-tête du document)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for cle, valeur in donnees.items():
                        balise = f"{{{{{cle}}}}}"
                        if balise in p.text:
                            p.text = p.text.replace(balise, str(valeur))
                            
    doc.save(chemin_sortie)

# =========================================================
# INTERFACE GRAPHIQUE STREAMLIT
# =========================================================

st.set_page_config(page_title="Générateur de Bilans Orthophoniques", page_icon="📝", layout="centered")

st.title("📝 Assistant Bilans Orthophoniques")
st.write("Bienvenue ! Cet outil vous aide à générer vos comptes-rendus automatiquement.")
st.divider()

# --- ÉTAPE 1 : LA FEUILLE DE RENSEIGNEMENT ---
st.header("1. Feuille de renseignement")
fichier_renseignement = st.file_uploader("Glissez le scan de la feuille de renseignement ici (PDF)", type=['pdf'])

if fichier_renseignement:
    st.success("✅ Fiche de renseignement chargée !")

st.divider()

# --- ÉTAPE 2 : LE QUESTIONNAIRE COMPLÉMENTAIRE ---
st.header("2. Informations complémentaires")
col1, col2 = st.columns(2)

with col1:
    num_secu = st.text_input("N° de Sécurité Sociale (si absent du scan)")
    
with col2:
    trimestre = st.selectbox("Période de la classe", ["Non précisé", "1er trimestre", "2ème trimestre", "3ème trimestre"])

type_bilan = st.selectbox("Quel type d'examens a été passé ?", [
    "Langage oral", 
    "Langage oral et écrit", 
    "Langage oral et logico-mathématique"
])

st.divider()

# --- ÉTAPE 3 : LES SCANS DES RÉSULTATS ---
st.header("3. Grilles de résultats")
st.write(f"Veuillez insérer les grilles pour le bilan : **{type_bilan}**")

grille_oral = st.file_uploader("📥 Scan de la grille : Langage Oral (Image ou PDF)", type=['jpg', 'jpeg', 'png', 'pdf'])
grille_ecrit = None

if type_bilan in ["Langage oral et écrit", "Langage oral et logico-mathématique"]:
    grille_ecrit = st.file_uploader("📥 Scan de la grille : Langage Écrit (Lecture/Orthographe)", type=['jpg', 'jpeg', 'png', 'pdf'])

st.divider()

# --- ÉTAPE 4 : LE BOUTON MAGIQUE ---
if fichier_renseignement and grille_oral:
    if st.button("✨ Générer le compte-rendu Word", type="primary", use_container_width=True):
        with st.spinner('Lecture des documents et analyse par l\'IA en cours... Veuillez patienter ⏳'):
            
            # 1. Préparation du grand dictionnaire de données
            donnees_finales = {
                "NUM_SECU": num_secu if num_secu else "[À COMPLÉTER]",
                "TRIMESTRE": trimestre
            }
            
            # 2. Lecture de la fiche de renseignement (Tesseract)
            chemin_rens = sauvegarder_fichier_upload(fichier_renseignement, "fiche_patient.pdf")
            donnees_patient = extraire_fiche_renseignement(chemin_rens)
            donnees_finales.update(donnees_patient) # Ajoute le Nom, Prénom, Age, etc.
            
            # 3. Analyse de la grille d'oral (Gemini IA)
            chemin_oral = sauvegarder_fichier_upload(grille_oral, "grille_oral." + grille_oral.name.split('.')[-1])
            res_oral = analyser_grille_ia(chemin_oral, type_test="general")
            
            # On relie les résultats de l'IA générale aux placeholders du Word
            donnees_finales["SCORE_PHONOLOGIE"] = res_oral.get("score_total", "[À COMPLÉTER]")
            donnees_finales["REUSSITES_PHONOLOGIE"] = res_oral.get("reussites", "[À COMPLÉTER]")
            donnees_finales["ERREURS_PHONOLOGIE"] = res_oral.get("erreurs", "[À COMPLÉTER]")
            
            # 4. Analyse de la grille d'écrit (Lecture) si elle a été fournie
            if grille_ecrit:
                chemin_ecrit = sauvegarder_fichier_upload(grille_ecrit, "grille_ecrit." + grille_ecrit.name.split('.')[-1])
                res_ecrit = analyser_grille_ia(chemin_ecrit, type_test="lecture")
                # L'IA "lecture" génère directement les bonnes clés (ex: SCORE_LECTURE_LETTRES)
                donnees_finales.update(res_ecrit) 

            # 5. Génération du document Word
            nom_patient = donnees_finales.get("NOM_PATIENT", "Patient").replace(" ", "_")
            chemin_sortie_word = f"data_sortie/CR_{nom_patient}.docx"
            
            # On appelle notre fonction pour créer le Word
            generer_word("Test_PlaceHolder.docx", chemin_sortie_word, donnees_finales)
            
            st.success("🎉 Le compte-rendu a été généré avec succès !")
            
            # 6. Création du bouton de téléchargement du fichier généré
            with open(chemin_sortie_word, "rb") as file:
                btn = st.download_button(
                    label="📥 Télécharger le compte-rendu final",
                    data=file,
                    file_name=f"CR_{nom_patient}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
else:
    st.info("💡 Chargez au moins la feuille de renseignement et la grille de Langage Oral pour générer le bilan.")