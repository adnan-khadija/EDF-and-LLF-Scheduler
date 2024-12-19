# Simulateur d'Ordonnancement EDF/LLF

Ce projet est un simulateur d'ordonnancement temps réel implémentant les algorithmes EDF (Earliest Deadline First) et LLF (Least Laxity First).

## Fonctionnalités

- Simulation des algorithmes EDF et LLF
- Interface graphique interactive avec Streamlit
- Visualisation du diagramme de Gantt
- Gestion des tâches périodiques
- Calcul automatique du taux d'utilisation
- Détection des deadlines manquées

  ![Capture d'écran 2024-12-19 153639](https://github.com/user-attachments/assets/e93f4d13-f3fe-4b27-ac02-2b9dea465345)

  <img width="959" alt="image" src="https://github.com/user-attachments/assets/447cf478-ce11-4e41-a819-63115a71f96b" />

  ![Capture d'écran 2024-12-19 153748](https://github.com/user-attachments/assets/7c442bf6-b19f-4822-b306-115b3aae0b49)



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

