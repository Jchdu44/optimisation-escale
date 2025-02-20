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
    "S2 (13h00-20h00)": 6.5
}

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
        else:
            plan_shifts.append("V1")
            duree_totale -= 3.5
            total_shift_time += 3.5
    
    return plan_shifts, total_shift_time

def allocation_dockers(type_cargaisons, plan_shifts):
    allocation_totale = {"CM": 0, "HP": 0, "Chauffeurs": 0, "HC": 0}
    for type_cargaison in type_cargaisons:
        equipe = equipes_dockers.get(type_cargaison, equipes_dockers["Autres"])
        for key in allocation_totale:
            allocation_totale[key] += equipe[key] * len(plan_shifts)
    return allocation_totale

def afficher_schema_navire(tonnage_par_cale, duree_par_cale):
    fig, ax = plt.subplots(figsize=(12, 3))
    cales = [f"Cale {i+1}" for i in range(len(tonnage_par_cale))]
    ax.barh(cales, tonnage_par_cale, color='steelblue')
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
    duree_par_cale, duree_totale = calcul_duree_escale(tonnage_par_cale, cadence_moyenne)
    plan_shifts, total_shift_time = optimiser_working_shifts(duree_totale)
    allocation_totale = allocation_dockers(type_cargaisons, plan_shifts)
    
    st.subheader("Résultats")
    st.write(f"Nom du navire : {nom_navire}")
    st.write(f"Durée totale estimée de l'escale (h) : {duree_totale:.2f}")
    st.write(f"Shifts recommandés : {', '.join(plan_shifts)}")
    st.write(f"Temps total de shift utilisé : {total_shift_time:.2f} h")
    
    st.subheader("Allocation des Dockers par Working Shift")
    for role, nombre in allocation_totale.items():
        st.write(f"{role} : {nombre}")
    
    st.subheader("Schéma du navire et répartition du tonnage")
    afficher_schema_navire(tonnage_par_cale, duree_par_cale)
