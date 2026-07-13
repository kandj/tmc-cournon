import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(page_title="TMC des Cournon", page_icon="🎾", layout="centered")
st.title("🎾 TMC du Tennis Club des Cournon")

# Lien de votre Google Sheets (Remplacez bien par VOTRE ID de fichier !)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BzEZQnOuA6-ut2z6VxqjhZ-G63d5O1Wi/export?format=xlsx"

@st.cache_data(ttl=60)
def load_data():
    df_matchs = pd.read_excel(SHEET_URL, sheet_name="Matchs")
    return df_matchs

try:
    df = load_data()
    
    # Sélection de l'affichage
    onglet = st.radio("Navigation :", ["Matchs en cours / Résultats", "Tableau Visuel (Arbre)"], horizontal=True)
    
    if onglet == "Matchs en cours / Résultats":
        sub_tab = st.selectbox("Afficher :", ["Matchs en cours", "Matchs terminés"])
        
        if sub_tab == "Matchs en cours":
            matchs_en_cours = df[df['Vainqueur'].isna() | (df['Vainqueur'] == "")]
            if not matchs_en_cours.empty:
                for idx, row in matchs_en_cours.iterrows():
                    st.info(f"**{row['Phase']}** : {row['Joueur 1']} 🆚 {row['Joueur 2']}")
            else:
                st.success("Aucun match en cours. Tous les matchs sont terminés !")
        else:
            matchs_termines = df[df['Vainqueur'].notna() & (df['Vainqueur'] != "")]
            for idx, row in matchs_termines.iterrows():
                st.success(f"🏆 **{row['Vainqueur']}** bat {row['Joueur 1'] if row['Vainqueur'] != row['Joueur 1'] else row['Joueur 2']}  \n👉 Score : {row['Texte Affichage Compact']}")
                
    elif onglet == "Tableau Visuel (Arbre)":
        st.subheader("Arborescence du Tableau Principal (Haut)")
        
        # Récupération des données pour construire le graphique
        # Nous associons les matchs des 1/8es vers les 1/4
        t1 = df[df['Phase'] == "1/8 Finale"].set_index('ID Match')
        t2 = df[df['Phase'] == "1/4 Finale (Haut)"].set_index('ID Match')
        
        # Dessin de l'arbre géométrique avec Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        
        # Coordonnées des nœuds du graphique
        # 1/8es de finale (Col 1)
        y_coords_t1 = [7, 6, 5, 4, 3, 2, 1, 0]
        for idx, match_id in enumerate(["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"]):
            if match_id in t1.index:
                j1 = str(t1.loc[match_id, 'Joueur 1'])[:15]
                j2 = str(t1.loc[match_id, 'Joueur 2'])[:15]
                v = t1.loc[match_id, 'Vainqueur']
                # Affichage des joueurs du match
                ax.text(0.5, y_coords_t1[idx] + 0.15, f"{j1}", fontsize=9, ha='left', va='bottom', weight='bold' if v == t1.loc[match_id, 'Joueur 1'] else 'normal')
                ax.text(0.5, y_coords_t1[idx] - 0.15, f"{j2}", fontsize=9, ha='left', va='top', weight='bold' if v == t1.loc[match_id, 'Joueur 2'] else 'normal')
                # Box du match
                rect = plt.Rectangle((0.4, y_coords_t1[idx] - 0.35), 2.2, 0.7, fill=True, color='#E8EEF5', ec='#1B365D', lw=1.5, zorder=1)
                ax.add_patch(rect)
                ax.text(0.45, y_coords_t1[idx] - 0.3, f"{match_id}", fontsize=7, color='#1B365D', alpha=0.7)

        # 1/4 de finale (Col 2)
        y_coords_t2 = [6.5, 4.5, 2.5, 0.5]
        for idx, match_id in enumerate(["M09", "M10", "M11", "M12"]):
            if match_id in t2.index:
                j1 = str(t2.loc[match_id, 'Joueur 1'])[:15] if pd.notna(t2.loc[match_id, 'Joueur 1']) else "À déterminer"
                j2 = str(t2.loc[match_id, 'Joueur 2'])[:15] if pd.notna(t2.loc[match_id, 'Joueur 2']) else "À déterminer"
                v = t2.loc[match_id, 'Vainqueur']
                
                ax.text(4.1, y_coords_t2[idx] + 0.15, f"{j1}", fontsize=9, ha='left', va='bottom', weight='bold' if v == t2.loc[match_id, 'Joueur 1'] else 'normal')
                ax.text(4.1, y_coords_t2[idx] - 0.15, f"{j2}", fontsize=9, ha='left', va='top', weight='bold' if v == t2.loc[match_id, 'Joueur 2'] else 'normal')
                
                rect = plt.Rectangle((4.0, y_coords_t2[idx] - 0.35), 2.2, 0.7, fill=True, color='#D0E1FD', ec='#1B365D', lw=1.5, zorder=1)
                ax.add_patch(rect)
                ax.text(4.05, y_coords_t2[idx] - 0.3, f"{match_id}", fontsize=7, color='#1B365D', alpha=0.7)

        # Tracé des lignes de connexion d'arbre (Huitièmes vers Quarts)
        # Connexion M01 & M02 -> M09
        ax.plot([2.6, 3.3, 3.3, 4.0], [7.0, 7.0, 6.5, 6.5], color='#1B365D', lw=1.5)
        ax.plot([2.6, 3.3, 3.3, 4.0], [6.0, 6.0, 6.5, 6.5], color='#1B365D', lw=1.5)
        
        # Connexion M03 & M04 -> M10
        ax.plot([2.6, 3.3, 3.3, 4.0], [5.0, 5.0, 4.5, 4.5], color='#1B365D', lw=1.5)
        ax.plot([2.6, 3.3, 3.3, 4.0], [4.0, 4.0, 4.5, 4.5], color='#1B365D', lw=1.5)

        # Connexion M05 & M06 -> M11
        ax.plot([2.6, 3.3, 3.3, 4.0], [3.0, 3.0, 2.5, 2.5], color='#1B365D', lw=1.5)
        ax.plot([2.6, 3.3, 3.3, 4.0], [2.0, 2.0, 2.5, 2.5], color='#1B365D', lw=1.5)

        # Connexion M07 & M08 -> M12
        ax.plot([2.6, 3.3, 3.3, 4.0], [1.0, 1.0, 0.5, 0.5], color='#1B365D', lw=1.5)
        ax.plot([2.6, 3.3, 3.3, 4.0], [0.0, 0.0, 0.5, 0.5], color='#1B365D', lw=1.5)

        # Paramètres d'affichage du graphique
        ax.set_xlim(0, 7)
        ax.set_ylim(-1, 8)
        
        st.pyplot(fig)

except Exception as e:
    st.error("En attente de la configuration de la base de données...")
