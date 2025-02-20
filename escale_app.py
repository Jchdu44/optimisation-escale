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

def calcul_duree_escale(tonnage_par_cale, cadence_moyenne):
    if not tonnage_par_cale or cadence_moyenne <= 0:
        return [], 0, []
    duree_par_cale = [tonnage / cadence_moyenne for tonnage in tonnage_par_cale]
    duree_totale = sum(duree_par_cale)
    seuil_bulldozer_temps = [(tonnage * (1 - BULLDOZER_SEUIL)) / cadence_moyenne for tonnage in tonnage_par_cale]
    return duree_par_cale, duree_totale, seuil_bulldozer_temps

def optimiser_working_shifts(duree_totale):
    plan_shifts = []
    total_shift_time = 0
    
    while duree_totale > 0:
        found_shift = False
        for shift, duration in sorted(shifts.items(), key=lambda x: -x[1]):
            if duree_totale >= duration:
                plan_shifts.append(shift)
                duree_totale -= duration
                total_shift_time += duration
                found_shift = True
                break
        if not found_shift:
            break  # Sécurité pour éviter une boucle infinie
    
    return plan_shifts, total_shift_time

def afficher_schema_navire(tonnage_par_cale, duree_par_cale, seuil_bulldozer_temps):
    fig, ax = plt.subplots(figsize=(12, 5))
    cales = [f"Cale {i+1}" for i in range(len(tonnage_par_cale))]
    
    bar_width = 0.4
    y_positions = np.arange(len(cales))
    
    ax.barh(y_positions, duree_par_cale, bar_width, label="Temps de déchargement", color='blue')
    ax.barh(y_positions + bar_width, seuil_bulldozer_temps, bar_width, label="Temps avant bulldozer", color='orange')
    
    for i, (duree, seuil_temps) in enumerate(zip(duree_par_cale, seuil_bulldozer_temps)):
        ax.text(duree / 2, i, f"{duree:.2f} h", va='center', ha='center', color='white')
        ax.text(seuil_temps / 2, i + bar_width, f"{seuil_temps:.2f} h", va='center', ha='center', color='black')
    
    ax.set_yticks(y_positions + bar_width / 2)
    ax.set_yticklabels(cales)
    ax.set_xlabel("Temps (h)")
    ax.set_title("Durée de déchargement et seuil d'embarquement du bulldozer par cale")
    ax.legend()
    
    st.pyplot(fig)

st.title("Optimisation des Escales de Navires")

nom_navire = st.text_input("Nom du navire")
nombre_cales = st.number_input("Nombre de cales", min_value=1, step=1)
cadence_moyenne = st.number_input("Cadence moyenne de déchargement (tonnes/h)", min_value=1.0, step=10.0)

tonnage_par_cale = []
type_cargaisons = []

for i in range(nombre_cales):
    tonnage = st.number_input(f"Tonnage de la cale {i+1} (tonnes)", min_value=0.0, step=100.0)
    tonnage_par_cale.append(tonnage)
    type_cargaisons.append(st.selectbox(f"Type de cargaison pour la cale {i+1}", list(equipes_dockers.keys()), key=f"cargaison_{i}"))

if st.button("Calculer"):
    try:
        duree_par_cale, duree_totale, seuil_bulldozer_temps = calcul_duree_escale(tonnage_par_cale, cadence_moyenne)
        if duree_totale == 0:
            st.warning("Veuillez saisir des valeurs valides pour le tonnage et la cadence de déchargement.")
        else:
            plan_shifts, total_shift_time = optimiser_working_shifts(duree_totale)
            
            st.subheader("Résultats")
            st.write(f"Nom du navire : {nom_navire}")
            st.write(f"Durée totale estimée de l'escale (h) : {duree_totale:.2f}")
            st.write(f"Shifts recommandés : {', '.join(plan_shifts)}")
            st.write(f"Temps total de shift utilisé : {total_shift_time:.2f} h")
            
            st.subheader("Schéma du navire et répartition du tonnage")
            afficher_schema_navire(tonnage_par_cale, duree_par_cale, seuil_bulldozer_temps)
    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
