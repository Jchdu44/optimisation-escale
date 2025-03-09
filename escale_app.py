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

BULLDOZER_SEUIL = 0.2

def optimiser_working_shifts(duree_totale, heure_debut=6.0):
    shifts_utilises = []
    total_shift_time = 0
    heure_actuelle = heure_debut

    while duree_totale > 0:
        if heure_actuelle >= 6 and heure_actuelle < 13 and duree_totale >= 6.5:
            shifts_utilises.append("S1 (06h00-13h00)")
            duree_totale -= 6.5
            total_shift_time += 6.5
            heure_actuelle = 13
        elif heure_actuelle >= 13 and heure_actuelle < 20 and duree_totale >= 6.5:
            shifts_utilises.append("S2 (13h00-20h00)")
            duree_totale -= 6.5
            total_shift_time += 6.5
            heure_actuelle = 20
        elif heure_actuelle >= 8 and heure_actuelle < 12 and duree_totale >= 3.5:
            shifts_utilises.append("V1 (08h00-12h00)")
            duree_totale -= 3.5
            total_shift_time += 3.5
            heure_actuelle = 12
        elif heure_actuelle >= 14 and heure_actuelle < 18 and duree_totale >= 3.5:
            shifts_utilises.append("V2 (14h00-18h00)")
            duree_totale -= 3.5
            total_shift_time += 3.5
            heure_actuelle = 18
        else:
            shifts_utilises.append("VS (20h00-23h00)")
            duree_totale -= 3.0
            total_shift_time += 3.0
            heure_actuelle = 23

    return shifts_utilises, total_shift_time

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
    duree_totale = sum([tonnage / cadence for tonnage, cadence in zip(tonnage_par_cale, cadence_par_cale)])
    shifts_utilises, total_shift_time = optimiser_working_shifts(duree_totale)
    
    st.subheader("Résultats")
    st.write(f"Nom du navire : {nom_navire}")
    st.write(f"Durée totale estimée de l'escale (h) : {duree_totale:.2f}")
    st.write(f"Shifts recommandés : {', '.join(shifts_utilises)}")
    st.write(f"Temps total de shift utilisé : {total_shift_time:.2f} h")

st.write("Si cette heure ne change pas après une mise à jour, Streamlit n'exécute pas la dernière version du code.")
