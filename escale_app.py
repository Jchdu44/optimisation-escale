# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

# Définition des équipes types en fonction de la cargaison
equipes_dockers = {
    "Tourteaux de soja": {"CM": 1, "HP": 2, "Chauffeurs": 2, "HC": 1},
    "Céréales": {"CM": 1, "HP": 1, "Chauffeurs": 1, "HC": 1},
    "Charbon": {"CM": 1, "HP": 3, "Chauffeurs": 2, "HC": 2},
    "Autres": {"CM": 1, "HP": 1, "Chauffeurs": 1, "HC": 1}
}

shifts = {
    "V1 (08h00-12h00)": 3.5,
    "V2 (14h00-18h00)": 3.5,
    "S1 (06h00-13h00)": 6.5,
    "S2 (13h00-20h00)": 6.5,
    "VS (20h00-23h00)": 3.0  # Ajout du shift VS
}

BULLDOZER_SEUIL = 0.2  # Seuil de 20% pour introduire un bulldozer

def predire_cadence(historique_data):
    return np.mean(historique_data) if len(historique_data) > 0 else 100  # Valeur par défaut

def calcul_duree_escale(tonnage_par_cale, cadence_moyenne):
    duree_par_cale = [tonnage / cadence_moyenne if cadence_moyenne > 0 else 0 for tonnage in tonnage_par_cale]
    duree_totale = sum(duree_par_cale)
    seuil_bulldozer_temps = [(tonnage * (1 - BULLDOZER_SEUIL)) / cadence_moyenne if cadence_moyenne > 0 else 0 for tonnage in tonnage_par_cale]
    return duree_par_cale, duree_totale, seuil_bulldozer_temps

def optimiser_working_shifts(duree_totale):
    plan_shifts = []
    total_shift_time = 0
    
    while duree_totale > 0:
        if duree_totale > 6.5:
            plan_shifts.append("S1 + S2")
            duree_totale -= 13.0
            total_shift_time += 13.0
        elif duree_totale > 3.5:
            plan_shifts.append("S1")
            duree_totale -= 6.5
            total_shift_time += 6.5
        elif duree_totale > 3.0:
            plan_shifts.append("VS")
            duree_totale -= 3.0
            total_shift_time += 3.0
        else:
            plan_shifts.append("V1")
            duree_totale -= 3.5
            total_shift_time += 3.5
    
    return plan_shifts, total_shift_time

def afficher_schema_navire(tonnage_par_cale, duree_par_cale, seuil_bulldozer_temps):
    fig, ax = plt.subplots(figsize=(12, 3))
    cales = [f"Cale {i+1}" for i in range(len(tonnage_par_cale))]
    colors = [
        'green' if tonnage > max(tonnage_par_cale) * BULLDOZER_SEUIL else 'red' if tonnage > max(tonnage_par_cale) * 0.1 else 'orange' 
        for tonnage in tonnage_par_cale
    ]
    ax.barh(cales, tonnage_par_cale, color=colors)
    for i, (duree, seuil_temps) in enumerate(zip(duree_par_cale, seuil_bulldozer_temps)):
        ax.text(tonnage_par_cale[i] / 2, i, f"{duree:.2f} h\nBulldozer: {seuil_temps:.2f} h", va='center', ha='center', color='white')
    ax.set_xlabel("Tonnage (T)")
    ax.set_title("Tonnage par cale et durée estimée")
    st.pyplot(fig)

st.title("Optimisation des Escales de Navires")

nom_navire = st.text_input("Nom du navire")
nombre_cales = st.number_input("Nombre de cales", min_value=1, step=1)
cadence_moyenne = st.number_input("Cadence moyenne de déchargement (tonnes/h)", min_value=1.0, step=10.0)

tonnage_par_cale = []
type_cargaisons = []

for i in range(nombre_cales):
    tonnage_par_cale.append(st.number_input(f"Tonnage de la cale {i+1} (tonnes)", min_value=0.0, step=100.0))
    type_cargaisons.append(st.selectbox(f"Type de cargaison pour la cale {i+1}", list(equipes_dockers.keys()), key=f"cargaison_{i}"))

if st.button("Calculer"):
    duree_par_cale, duree_totale, seuil_bulldozer_temps = calcul_duree_escale(tonnage_par_cale, cadence_moyenne)
    plan_shifts, total_shift_time = optimiser_working_shifts(duree_totale)
    
    st.subheader("Résultats")
    st.write(f"Nom du navire : {nom_navire}")
    st.write(f"Durée totale estimée de l'escale (h) : {duree_totale:.2f}")
    st.write(f"Shifts recommandés : {', '.join(plan_shifts)}")
    st.write(f"Temps total de shift utilisé : {total_shift_time:.2f} h")
    
    st.subheader("Schéma du navire et répartition du tonnage")
    afficher_schema_navire(tonnage_par_cale, duree_par_cale, seuil_bulldozer_temps)
