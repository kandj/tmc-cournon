import streamlit as st
import pandas as pd

# Titre de l'application
st.set_page_config(page_title="TMC des Cournon", page_icon="🎾", layout="centered")
st.title("🎾 TMC du Tennis Club des Cournon")

# Lien vers votre Google Sheets (Remplacez par votre lien de partage "Lecteur" réel)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BzEZQnOuA6-ut2z6VxqjhZ-G63d5O1Wi/export?format=xlsx"

@st.cache_data(ttl=60)  # Met à jour les données toutes les minutes
def load_data():
    # Lit l'onglet Matchs
    df_matchs = pd.read_excel(SHEET_URL, sheet_name="Matchs")
    return df_matchs

try:
    df = load_data()
    
    # Boutons de filtres
    onglet = st.radio("Afficher :", ["Matchs en cours", "Matchs terminés"], horizontal=True)
    
    if onglet == "Matchs en cours":
        # Matchs sans vainqueur
        matchs_en_cours = df[df['Vainqueur'].isna() | (df['Vainqueur'] == "")]
        if not matchs_en_cours.empty:
            for idx, row in matchs_en_cours.iterrows():
                st.info(f"**{row['Phase']}** : {row['Joueur 1']} 🆚 {row['Joueur 2']}")
        else:
            st.success("Aucun match en cours. Tous les matchs sont terminés !")
            
    else:
        # Matchs terminés
        matchs_termines = df[df['Vainqueur'].notna() & (df['Vainqueur'] != "")]
        for idx, row in matchs_termines.iterrows():
            st.success(f"🏆 **{row['Vainqueur']}** bat {row['Joueur 1'] if row['Vainqueur'] != row['Joueur 1'] else row['Joueur 2']} \n\n 👉 Score : {row['Texte Affichage Compact']}")

except Exception as e:
    st.error("En attente de la configuration de la base de données...")
