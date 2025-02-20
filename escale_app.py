# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calcul_duree_escale(tonnage_par_cale, cadence_dechargement, nombre_cales):
    duree_par_cale = [tonnage_par_cale[i] / cadence_dechargement[i] if cadence_dechargement[i] > 0 else 0 for i in range(nombre_cales)]
    duree_totale = sum(duree_par_cale) if duree_par_cale else 0
    return duree_par_cale, duree_totale

def allocation_dockers(nombre_cales, dockers_par_cale, nombre_navires):
    return sum(dockers_par_cale) * nombre_navires if dockers_par_cale else 0

def calcul_cout_dockers(dockers_total, duree_totale, taux_horaire):
    return dockers_total * taux_horaire * duree_totale if dockers_total > 0 and duree_totale > 0 else 0

def calcul_cout_materiel(materiel_par_cale, durees, taux_horaire_materiel):
    return sum(materiel_par_cale[i] * taux_horaire_materiel * durees[i] for i in range(len(durees))) if materiel_par_cale else 0

def selection_working_shift():
    shifts = {
        "08h00-12h00 / 14h00-18h00": 1.0,
        "06h00-13h00 / 13h00-20h00": 1.0,
        "20h00-23h00 (majore)": 1.5
    }
    return min(shifts, key=shifts.get), shifts[min(shifts, key=shifts.get)]

def afficher_schema_navire(tonnage_par_cale, nombre_cales):
    fig, ax = plt.subplots(figsize=(10, 5))
    cales = [f"Cale {i+1}" for i in range(nombre_cales)]
    ax.barh(cales, tonnage_par_cale, color='steelblue')
    ax.set_xlabel("Tonnage (T)")
    ax.set_title("Répartition du tonnage par cale")
    st.pyplot(fig)

st.title("Optimisation des Escales de Navires")

nombre_navires = st.number_input("Nombre de navires en escale", min_value=1, step=1)
nombre_cales = st.number_input("Nombre de cales par navire", min_value=1, step=1)
taux_horaire = st.number_input("Taux horaire des dockers (€)", min_value=0.0, step=0.5)
taux_horaire_materiel = st.number_input("Taux horaire du materiel (€)", min_value=0.0, step=0.5)

tonnage_par_cale, cadence_dechargement, dockers_par_cale, type_cargaison, materiel_par_cale = [], [], [], [], []
nom_navires = [st.text_input(f"Nom du navire {i+1}") for i in range(nombre_navires)]

for i in range(nombre_cales):
    tonnage_par_cale.append(st.number_input(f"Tonnage de la cale {i+1} (tonnes)", min_value=0.0, step=100.0))
    cadence_dechargement.append(st.number_input(f"Cadence de dechargement de la cale {i+1} (tonnes/heure)", min_value=1.0, step=10.0))
    dockers_par_cale.append(st.number_input(f"Nombre de dockers affectes a la cale {i+1}", min_value=1, step=1))
    type_cargaison.append(st.text_input(f"Type de cargaison pour la cale {i+1}"))
    materiel_par_cale.append(st.number_input(f"Nombre d'unites de materiel (ex: bulldozer) pour la cale {i+1}", min_value=0, step=1))

if st.button("Calculer"):
    durees, duree_totale = calcul_duree_escale(tonnage_par_cale, cadence_dechargement, nombre_cales)
    dockers_total = allocation_dockers(nombre_cales, dockers_par_cale, nombre_navires)
    cout_total = calcul_cout_dockers(dockers_total, duree_totale, taux_horaire)
    cout_materiel = calcul_cout_materiel(materiel_par_cale, durees, taux_horaire_materiel)
    working_shift, shift_cost_factor = selection_working_shift()
    cout_total_shift = cout_total * shift_cost_factor
    
    results = pd.DataFrame({
        "Cale": [f"Cale {i+1}" for i in range(nombre_cales)],
        "Tonnage (T)": tonnage_par_cale,
        "Cadence (T/h)": cadence_dechargement,
        "Duree Dechargement (h)": durees,
        "Dockers Affectes": dockers_par_cale,
        "Type de Cargaison": type_cargaison,
        "Materiel Utilise": materiel_par_cale
    })
    
    st.subheader("Resultats")
    st.write("Nom des navires en escale :", ", ".join(nom_navires))
    st.write("Duree totale estimee de l'escale (h):", duree_totale)
    st.write("Nombre total de dockers necessaires:", dockers_total)
    st.write("Cout total estime des dockers (€) avant shift :", cout_total)
    st.write("Cout total estime du materiel (€) :", cout_materiel)
    st.write("Shift recommande :", working_shift)
    st.write("Cout total ajuste apres application du shift (€) :", cout_total_shift)
    st.dataframe(results)
    
    st.subheader("Schema du navire et repartition du tonnage")
    afficher_schema_navire(tonnage_par_cale, nombre_cales)
