from typing import List
import math
import streamlit as st
from edf_scheduler import Task, lcm_for_periods

def calculate_laxity(task: Task, current_time: int) -> int:
    if task.remaining_time == 0:  # Si la tâche est terminée
        return float('inf')  # Laxité infinie
    
    time_to_deadline = task.next_deadline - current_time
    if time_to_deadline < 0:  # Si on a dépassé la deadline
        # Calculer la prochaine deadline
        periods_passed = (current_time - task.arrival_time) // task.period
        next_period_deadline = task.arrival_time + (periods_passed + 1) * task.period + task.deadline
        time_to_deadline = next_period_deadline - current_time
    
    return time_to_deadline - task.remaining_time

def check_schedulability(tasks: List[Task]) -> bool:
    """Vérifier si l'ensemble des tâches est ordonnançable."""
    utilization = sum(task.execution_time / task.period for task in tasks)
    return utilization <= 1

def llf_gantt(tasks: List[Task], total_time: int):
    """Générer les données du diagramme de Gantt pour l'algorithme LLF."""
    gantt_data = []
    start_time = min(task.arrival_time for task in tasks)
    current_time = start_time
    active_tasks = tasks.copy()

    # Vérifier la faisabilité de l'ordonnancement
    if not check_schedulability(tasks):
        st.warning("Attention : Le taux d'utilisation du processeur dépasse 100%. L'ordonnancement pourrait ne pas être optimal.")
    
    # Réinitialiser l'état des tâches
    for task in active_tasks:
        task.remaining_time = task.execution_time
        task.next_deadline = task.arrival_time + task.deadline
        task.next_release = task.arrival_time + task.period

    # Pour chaque unité de temps
    missed_deadlines = []
    while current_time < total_time:
        # Mettre à jour les tâches qui commencent une nouvelle période
        for task in active_tasks:
            if current_time >= task.next_release:
                # Vérifier si la tâche a manqué sa deadline
                if task.remaining_time > 0:
                    missed_deadlines.append(f"Tâche {task.name} à t={current_time}")
                # Réinitialiser pour la nouvelle période
                task.remaining_time = task.execution_time
                task.next_deadline = task.next_release + task.deadline
                task.next_release += task.period

        # Sélectionner les tâches disponibles
        ready_tasks = [
            t for t in active_tasks 
            if t.arrival_time <= current_time 
            and t.remaining_time > 0 
            and t.next_release - t.period <= current_time
        ]

        # Sélectionner la tâche à exécuter selon LLF
        selected_task = None
        if ready_tasks:
            # Calculer la laxité pour toutes les tâches prêtes
            task_laxities = [(t, calculate_laxity(t, current_time)) for t in ready_tasks]
            
            # Trier d'abord par laxité, puis par deadline en cas d'égalité
            task_laxities.sort(key=lambda x: (x[1], x[0].next_deadline))
            
            selected_task = task_laxities[0][0]
            selected_task.remaining_time -= 1

        # Collecter les informations d'état pour chaque tâche
        task_states = []
        for task in active_tasks:
            laxity = calculate_laxity(task, current_time)
            state = {
                "name": task.name,
                "time": current_time,
                "state": "running" if task == selected_task else "waiting" if task in ready_tasks else "idle",
                "deadline": task.next_deadline,
                "remaining": task.remaining_time,
                "period_start": task.next_release - task.period,
                "period_end": task.next_release,
                "execution_time": task.execution_time,
                "laxity": laxity
            }
            task_states.append(state)

        gantt_data.extend(task_states)
        current_time += 1

    # Si des deadlines ont été manquées, ajouter un avertissement
    if missed_deadlines:
        st.warning(f"Deadlines manquées : {', '.join(missed_deadlines)}")

    return gantt_data
