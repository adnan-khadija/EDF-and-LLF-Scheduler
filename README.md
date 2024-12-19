# Simulateur d'Ordonnancement EDF/LLF

Ce projet est un simulateur d'ordonnancement temps réel implémentant les algorithmes EDF (Earliest Deadline First) et LLF (Least Laxity First).

## Fonctionnalités

- Simulation des algorithmes EDF et LLF
- Interface graphique interactive avec Streamlit
- Visualisation du diagramme de Gantt
- Gestion des tâches périodiques
- Calcul automatique du taux d'utilisation
- Détection des deadlines manquées

## Installation

1. Cloner le repository :
```bash
[git clone https://github.com/VOTRE_USERNAME/EDF_LLF.git](https://github.com/adnan-khadija/EDF-and-LCM-Scheduler.git)
cd EDF-and-LCM-Scheduler
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Pour lancer l'application :
```bash
streamlit run app.py
```

## Structure du Projet

- `app.py` : Interface utilisateur Streamlit
- `edf_scheduler.py` : Implémentation de l'algorithme EDF
- `llf_scheduler.py` : Implémentation de l'algorithme LLF

