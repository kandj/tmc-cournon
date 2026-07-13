import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(page_title="TMC des Cournon", page_icon="🎾", layout="centered")

# Titre principal
st.title("🎾 TMC du Tennis Club des Cournon")

# ==========================================
# CONFIGURATION DE LA SOURCE DE DONNÉES
# ==========================================
# Remplacer 'VOTRE_ID_DE_FICHIER' par l'identifiant réel de votre Google Sheets partagé
SHEET_URL = "https://docs.google.com/spreadsheets/d/1BzEZQnOuA6-ut2z6VxqjhZ-G63d5O1Wi/export?format=xlsx"

@st.cache_data(ttl=30)  # Mise à jour des données toutes les 30 secondes
def load_data():
    df_matchs = pd.read_excel(SHEET_URL, sheet_name="Matchs")
    return df_matchs

try:
    df = load_data()
    
    # Barre de navigation principale
    onglet = st.radio("Navigation :", ["Matchs en cours / Résultats", "Tableau Visuel (Arbre)"], horizontal=True)
    
    # ==========================================
    # ONGLET 1 : LISTES DES MATCHS
    # ==========================================
    if onglet == "Matchs en cours / Résultats":
        sub_tab = st.selectbox("Afficher :", ["Matchs en cours / À venir", "Matchs terminés (Résultats)"])
        
        if sub_tab == "Matchs en cours / À venir":
            # Matchs sans vainqueur renseigné
            matchs_en_cours = df[df['Vainqueur'].isna() | (df['Vainqueur'] == "")]
            if not matchs_en_cours.empty:
                st.write(f"### ⏳ {len(matchs_en_cours)} match(s) en attente ou en cours")
                for idx, row in matchs_en_cours.iterrows():
                    st.info(f"**{row['Phase']}** ({row['ID Match']}) : {row['Joueur 1']} 🆚 {row['Joueur 2']}")
            else:
                st.success("🎉 Aucun match en cours. Tous les matchs de cette phase sont terminés !")
                
        else:
            # Matchs avec un vainqueur renseigné
            matchs_termines = df[df['Vainqueur'].notna() & (df['Vainqueur'] != "")]
            if not matchs_termines.empty:
                st.write(f"### 🏆 {len(matchs_termines)} match(s) terminés")
                for idx, row in matchs_termines.iterrows():
                    # Formatage de l'affichage du score complet
                    score_str = row['Texte Affichage Compact'] if 'Texte Affichage Compact' in df.columns else f"{row['Score Set 1']} {row['Score Set 2']}"
                    st.success(f"**{row['Phase']}** : 🏆 **{row['Vainqueur']}** bat {row['Joueur 1'] if row['Vainqueur'] != row['Joueur 1'] else row['Joueur 2']}  \n👉 Score : *{score_str}*")
            else:
                st.warning("Aucun match n'est encore terminé pour le moment.")
                
    # ==========================================
    # ONGLET 2 : TABLEAUX VISUELS (ARBRE)
    # ==========================================
    elif onglet == "Tableau Visuel (Arbre)":
        st.subheader("Arborescence des Tableaux TMC")
        
        # Choix du sous-tableau conforme aux principes du TMC
        type_tableau = st.radio("Sélectionnez le tableau à visualiser :", 
                                ["Tableau Principal (Places 1 à 8)", "Tableau Consolante (Places 9 à 16)"], 
                                horizontal=True)
        
        # Extraction et indexation du premier tour (commun aux deux branches)
        t1 = df[df['Phase'] == "1/8 Finale"].set_index('ID Match')
        
        # Configuration des variables selon le tableau choisi
        if type_tableau == "Tableau Principal (Places 1 à 8)":
            st.write("### 🥇 Course au titre (Flux des Vainqueurs du T1)")
            t2 = df[df['Phase'] == "1/4 Finale (Haut)"].set_index('ID Match')
            matchs_t1 = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"]
            matchs_t2 = ["M09", "M10", "M11", "M12"]
            color_box_t1 = '#E8EEF5'
            color_box_t2 = '#D0E1FD'
            line_style = '-'  # Lignes pleines pour le tableau principal
        else:
            st.write("### 🎯 Matches de Classement (Flux des Perdants du T1)")
            t2 = df[df['Phase'] == "1/4 Finale (Bas)"].set_index('ID Match')
            matchs_t1 = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"]
            matchs_t2 = ["M13", "M14", "M15", "M16"]
            color_box_t1 = '#FCE4D6'
            color_box_t2 = '#F8CBAD'
            line_style = '--'  # Lignes pointillées pour symboliser la bascule en consolante

        # Initialisation du graphique Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6.5))
        ax.axis('off')
        
        # 1. Rendu du Premier Tour (Huitièmes de finale)
        y_coords_t1 = [7, 6, 5, 4, 3, 2, 1, 0]
        for idx, match_id in enumerate(matchs_t1):
            if match_id in t1.index:
                j1 = str(t1.loc[match_id, 'Joueur 1'])[:15]
                j2 = str(t1.loc[match_id, 'Joueur 2'])[:15]
                v = t1.loc[match_id, 'Vainqueur']
                
                # Alignement et mise en gras du vainqueur
                ax.text(0.45, y_coords_t1[idx] + 0.15, f"{j1}", fontsize=9, ha='left', va='bottom', weight='bold' if v == t1.loc[match_id, 'Joueur 1'] else 'normal')
                ax.text(0.45, y_coords_t1[idx] - 0.15, f"{j2}", fontsize=9, ha='left', va='top', weight='bold' if v == t1.loc[match_id, 'Joueur 2'] else 'normal')
                
                # Encadré du match
                rect = plt.Rectangle((0.4, y_coords_t1[idx] - 0.35), 2.2, 0.7, fill=True, color=color_box_t1, ec='#1B365D', lw=1.2)
                ax.add_patch(rect)
                ax.text(0.43, y_coords_t1[idx] - 0.3, f"{match_id}", fontsize=7, color='#1B365D', alpha=0.6)

        # 2. Rendu du Second Tour (Quarts de finale correspondants)
        y_coords_t2 = [6.5, 4.5, 2.5, 0.5]
        for idx, match_id in enumerate(matchs_t2):
            if match_id in t2.index:
                j1 = str(t2.loc[match_id, 'Joueur 1'])[:15] if pd.notna(t2.loc[match_id, 'Joueur 1']) else "En attente..."
                j2 = str(t2.loc[match_id, 'Joueur 2'])[:15] if pd.notna(t2.loc[match_id, 'Joueur 2']) else "En attente..."
                v = t2.loc[match_id, 'Vainqueur']
                
                ax.text(4.05, y_coords_t2[idx] + 0.15, f"{j1}", fontsize=9, ha='left', va='bottom', weight='bold' if v == t2.loc[match_id, 'Joueur 1'] else 'normal')
                ax.text(4.05, y_coords_t2[idx] - 0.15, f"{j2}", fontsize=9, ha='left', va='top', weight='bold' if v == t2.loc[match_id, 'Joueur 2'] else 'normal')
                
                rect = plt.Rectangle((4.0, y_coords_t2[idx] - 0.35), 2.2, 0.7, fill=True, color=color_box_t2, ec='#1B365D', lw=1.5)
                ax.add_patch(rect)
                ax.text(4.03, y_coords_t2[idx] - 0.3, f"{match_id}", fontsize=7, color='#1B365D', alpha=0.7)

        # 3. Tracé des branchements reliant l'arbre
        for i in range(4):
            y_t1_inf = i * 2
            y_t1_sup = i * 2 + 1
            y_t2 = i * 2 + 0.5
            # Ligne supérieure du binôme de matchs vers le quart cible
            ax.plot([2.6, 3.3, 3.3, 4.0], [y_t1_sup, y_t1_sup, y_t2, y_t2], color='#1B365D', lw=1.5, linestyle=line_style)
            # Ligne inférieure du binôme de matchs vers le quart cible
            ax.plot([2.6, 3.3, 3.3, 4.0], [y_t1_inf, y_t1_inf, y_t2, y_t2], color='#1B365D', lw=1.5, linestyle=line_style)

        # Ajustements des limites d'affichage du canevas
        ax.set_xlim(0, 6.8)
        ax.set_ylim(-0.8, 7.8)
        
        # Rendu final du composant graphique dans la page Web
        st.pyplot(fig)

except Exception as e:
    st.error("Liaison avec le fichier Google Sheets interrompue. Vérifiez que l'identifiant du fichier dans SHEET_URL est correct et que l'accès général est configuré sur 'Tous les utilisateurs disposant du lien'.")

