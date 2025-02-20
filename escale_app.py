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
    return duree_par_cale, duree_totale

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

def allocation_dockers_par_shift(type_cargaisons, plan_shifts):
    allocation_par_shift = []
    for shift in plan_shifts:
        allocation_shift = {"CM": 0, "HP": 0, "Chauffeurs": 0, "HC": 0}
        for type_cargaison in type_cargaisons:
            equipe = equipes_dockers.get(type_cargaison, equipes_dockers["Autres"])
            for key in allocation_shift:
                allocation_shift[key] += equipe[key]
        allocation_par_shift.append((shift, allocation_shift))
    return allocation_par_shift

def afficher_schema_navire(tonnage_par_cale, duree_par_cale):
    fig, ax = plt.subplots(figsize=(12, 3))
    cales = [f"Cale {i+1}" for i in range(len(tonnage_par_cale))]
    colors = ['green' if tonnage > max(tonnage_par_cale) * BULLDOZER_SEUIL else 'red' for tonnage in tonnage_par_cale]
    ax.barh(cales, tonnage_par_cale, color=colors)
    for i, duree in enumerate(duree_par_cale):
        ax.text(tonnage_par_cale[i] / 2, i, f"{duree:.2f} h", va='center', ha='center', color='white')
    ax.set_xlabel("Tonnage (T)")
    ax.set_title("Tonnage par cale et durée estimée")
    st.pyplot(fig)

def simulation_dechargement(tonnage_par_cale, cadence_moyenne):
    st.subheader("Simulation dynamique du déchargement")
    tonnage_restant = tonnage_par_cale[:]
    progress_bars = [st.progress(0) for _ in range(len(tonnage_par_cale))]
    temps = 0
    
    while sum(tonnage_restant) > 0:
        time.sleep(1)
        temps += 1
        for i in range(len(tonnage_par_cale)):
            if tonnage_restant[i] > 0:
                tonnage_restant[i] -= cadence_moyenne / 60
                tonnage_restant[i] = max(0, tonnage_restant[i])
                progress = int(((tonnage_par_cale[i] - tonnage_restant[i]) / tonnage_par_cale[i]) * 100)
                progress_bars[i].progress(progress)
        st.write(f"Temps écoulé : {temps} min")
    st.success("Déchargement terminé !")

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
    duree_par_cale, duree_totale = calcul_duree_escale(tonnage_par_cale, cadence_moyenne)
    plan_shifts, total_shift_time = optimiser_working_shifts(duree_totale)
    allocation_par_shift = allocation_dockers_par_shift(type_cargaisons, plan_shifts)
    
    st.subheader("Résultats")
    st.write(f"Nom du navire : {nom_navire}")
    st.write(f"Durée totale estimée de l'escale (h) : {duree_totale:.2f}")
    st.write(f"Shifts recommandés : {', '.join(plan_shifts)}")
    st.write(f"Temps total de shift utilisé : {total_shift_time:.2f} h")
    
    st.subheader("Détail des équipes de Dockers par Working Shift")
    allocation_df = pd.DataFrame([{**shift[1], "Shift": shift[0]} for shift in allocation_par_shift])
    allocation_df = allocation_df.set_index("Shift")
    st.dataframe(allocation_df)
    
    st.subheader("Schéma du navire et répartition du tonnage")
    afficher_schema_navire(tonnage_par_cale, duree_par_cale)
    
    if st.button("Démarrer la simulation du déchargement"):
        simulation_dechargement(tonnage_par_cale, cadence_moyenne)
