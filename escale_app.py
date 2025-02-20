# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calcul_duree_escale(tonnage_par_cale, cadence_dechargement, nombre_cales):
    duree_par_cale = [tonnage_par_cale[i] / cadence_dechargement[i] if cadence_dechargement[i] > 0 else 0 for i in range(nombre_cales)]
    duree_totale = sum(duree_par_cale) if duree_par_cale else 0
    return duree_par_cale, duree_totale

def optimiser_working_shifts(duree_totale):
    shifts = {
        "V1 (08h00-12h00)": 3.5,
        "V2 (14h00-18h00)": 3.5,
        "S1 (06h00-13h00)": 6.5,
        "S2 (13h00-20h00)": 6.5
    }
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

def afficher_schema_navire(tonnage_par_cale, durees, nombre_cales, type_cargaison):
    fig, ax = plt.subplots(figsize=(12, 3))
    
    cale_positions = np.linspace(0, 1, nombre_cales + 2)[1:-1]  # Positions des cales
    bar_width = 1.0 / (nombre_cales + 2)  # Largeur des cales
    
    for i in range(nombre_cales):
        ax.add_patch(plt.Rectangle((cale_positions[i] - bar_width / 2, 0), bar_width, 0.5, 
                                   color='steelblue', edgecolor='black', alpha=0.7))
        ax.text(cale_positions[i], 0.25, f"Cale {i+1}\n{tonnage_par_cale[i]} T", 
                fontsize=10, ha='center', va='center', color='white')
        ax.text(cale_positions[i], -0.1, f"{durees[i]:.2f} h", fontsize=9, ha='center', color='black')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.2, 0.6)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Representation graphique du navire et duree de dechargement par cale")
    ax.axis('off')
    
    st.pyplot(fig)

st.title("Optimisation des Escales de Navires")

nom_navire = st.text_input("Nom du navire")
nombre_cales = st.number_input("Nombre de cales", min_value=1, step=1)
cadence_moyenne = st.number_input("Cadence moyenne de dechargement (tonnes/h)", min_value=1.0, step=10.0)

tonnage_par_cale, type_cargaison = [], []
for i in range(nombre_cales):
    tonnage_par_cale.append(st.number_input(f"Tonnage de la cale {i+1} (tonnes)", min_value=0.0, step=100.0))
    type_cargaison.append(st.text_input(f"Type de cargaison pour la cale {i+1}"))

if st.button("Calculer"):
    durees, duree_totale = calcul_duree_escale(tonnage_par_cale, [cadence_moyenne]*nombre_cales, nombre_cales)
    plan_shifts, total_shift_time = optimiser_working_shifts(duree_totale)
    
    st.subheader("Resultats")
    st.write(f"Nom du navire : {nom_navire}")
    st.write(f"Duree totale estimee de l'escale (h) : {duree_totale:.2f}")
    st.write(f"Shifts recommandes : {', '.join(plan_shifts)}")
    st.write(f"Temps total de shift utilise : {total_shift_time:.2f} h")
    
    st.subheader("Schema du navire et repartition du tonnage")
    afficher_schema_navire(tonnage_par_cale, durees, nombre_cales, type_cargaison)
