# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import requests
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

# Définition des cadences par type de marchandise
equipes_dockers = {
    "Alumine": 357,
    "Bauxite": 384,
    "Carbonate de soude": 303,
    "Charbon": 330,
    "Chrome": 357,
    "Clinker": 257,
    "Petcoke": 351,
    "DAP": 380,
    "Drêche de maïs": 199,
    "Graines de colza": 480,
    "Pâte à papier (portique)": 531,
    "Pâte à papier (grue de terre)": 366,
    "Sulfate d'ammonium": 292,
    "Tourteaux de colza (export)": 443,
    "Tourteaux de soja": 394,
    "Tourteaux de tournesol": 357,
    "Tourteaux de soja trace (sans OGM)": 322,
    "Urée": 362,
    "Pierre ponce": 381,
    "Phosphate": 368,
    "NPK": 324,
    "Carbonate de fer": 371
}

shifts = [
    ("S1 (06h00-13h00)", 6.5),
    ("S2 (13h00-20h00)", 6.5),
    ("V1 (08h00-12h00)", 3.5),
    ("V2 (14h00-18h00)", 3.5),
    ("VS (20h00-23h00)", 3.0)
]

BULLDOZER_SEUIL = 0.23  # Seuil pour le bulldozer à 23% du tonnage

def proposer_shifts(duree_totale, heure_actuelle=6):
    shifts_utilises = []
    heure_actuelle = 6  # Début du premier shift à 06h00

    while duree_totale > 0:
        for shift, duree_shift in shifts:
            if duree_totale >= duree_shift and (
                (shift.startswith("S1") and heure_actuelle == 6) or
                (shift.startswith("S2") and heure_actuelle == 13) or
                (shift.startswith("V1") and heure_actuelle == 8) or
                (shift.startswith("V2") and heure_actuelle == 14) or
                (shift.startswith("VS") and heure_actuelle == 20)
            ):
                shifts_utilises.append(shift)
                duree_totale -= duree_shift
                heure_actuelle += duree_shift
                if heure_actuelle >= 24:
                    heure_actuelle = 6  # Reprise du cycle à 06h00 le lendemain
                break
    return shifts_utilises

st.title("Optimisation des Escales de Navires")

st.write(f"Version du code : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

nom_navire = st.text_input("Nom du navire")
nombre_cales = st.number_input("Nombre de cales", min_value=1, step=1)

tonnage_par_cale = []
type_cargaisons = []
cadence_par_cale = []

definition_cargaisons = list(equipes_dockers.keys())

for i in range(nombre_cales):
    tonnage = st.number_input(f"Tonnage de la cale {i+1} (tonnes)", min_value=0.0, step=100.0)
    tonnage_par_cale.append(tonnage)
    
    type_cargaison = st.selectbox(f"Type de cargaison pour la cale {i+1}", definition_cargaisons, key=f"cargaison_{i}")
    type_cargaisons.append(type_cargaison)
    
    default_cadence = equipes_dockers.get(type_cargaison, 50.0)
    cadence = st.number_input(f"Cadence pour la cale {i+1} (T/h)", min_value=50.0, step=10.0, value=float(default_cadence))
    cadence_par_cale.append(cadence)

if st.button("Calculer"):
    duree_dechargement_par_cale = [tonnage / cadence for tonnage, cadence in zip(tonnage_par_cale, cadence_par_cale)]
    seuil_bulldozer_par_cale = [duree * BULLDOZER_SEUIL for duree in duree_dechargement_par_cale]
    
    st.subheader("Résultats")
    st.write(f"Nom du navire : {nom_navire}")
    st.write("Durée estimée de déchargement par cale et seuil bulldozer")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    cale_labels = [f"Cale {i+1}" for i in range(nombre_cales)]
    bar_width = 0.4
    
    ax.barh(cale_labels, duree_dechargement_par_cale, color='blue', label="Durée de déchargement")
    ax.barh(cale_labels, seuil_bulldozer_par_cale, color='orange', label="Seuil bulldozer")
    
    for i, v in enumerate(duree_dechargement_par_cale):
        ax.text(v, i, f"{v:.2f} h", va='center', color='white', fontsize=10, weight='bold')
    for i, v in enumerate(seuil_bulldozer_par_cale):
        ax.text(v, i, f"{v:.2f} h", va='center', color='black', fontsize=8)
    
    ax.set_xlabel("Temps (h)")
    ax.set_title("Durée de déchargement et seuil bulldozer par cale")
    ax.legend()
    st.pyplot(fig)
    
    duree_totale = sum(duree_dechargement_par_cale)
    st.write(f"Durée totale estimée de l'escale (h) : {duree_totale:.2f}")
    
    shifts_recommandes = proposer_shifts(duree_totale, heure_actuelle=6)
    st.write(f"Shifts recommandés : {', '.join(shifts_recommandes)}")
if 'shifts_recommandes' in locals():
    st.write(f"Nombre total de working shifts nécessaires : {len(shifts_recommandes)}")
else:
    st.write("Erreur : les shifts recommandés n'ont pas été calculés correctement.")

st.write("Si cette heure ne change pas après une mise à jour, Streamlit n'exécute pas la dernière version du code.")
