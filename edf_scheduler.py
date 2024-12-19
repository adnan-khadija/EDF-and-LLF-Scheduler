from typing import List
import math
import pandas as pd

class Task:
    def __init__(self, name: str, execution_time: int, period: int, deadline: int, arrival_time: int):
        self.name = name
        self.execution_time = execution_time
        self.period = period
        self.deadline = deadline
        self.arrival_time = arrival_time
        self.remaining_time = execution_time
        self.next_deadline = arrival_time + deadline
        self.next_release = arrival_time + period

    def update_after_period(self):
        self.next_deadline = self.next_release + self.deadline
        self.next_release += self.period
        self.remaining_time = self.execution_time

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def lcm_for_periods(periods: List[int]):
    lcm_result = periods[0]
    for period in periods[1:]:
        lcm_result = lcm(lcm_result, period)
    return lcm_result

def check_schedulability(tasks: List[Task]) -> bool:
    # Calculer le taux d'utilisation du processeur
    utilization = sum(task.execution_time / task.period for task in tasks)
    
    # Pour EDF, la condition suffisante est U ≤ 1
    # Nous ne vérifions que cette condition car elle est nécessaire
    # Les conditions plus strictes peuvent être trop conservatrices
    return utilization <= 1

def edf_schedule(tasks: List[Task], total_time: int):
    schedule = []
    start_time = min(task.arrival_time for task in tasks)
    time = start_time
    active_tasks = tasks.copy()

    while time < total_time:
        # Mettre à jour les tâches qui commencent une nouvelle période
        for task in active_tasks:
            if time >= task.next_release:
                task.update_after_period()

        # Filtrer les tâches disponibles
        available_tasks = [
            task for task in active_tasks 
            if task.arrival_time <= time 
            and task.remaining_time > 0 
            and task.next_release - task.period <= time
        ]

        # Trier par deadline absolue
        available_tasks.sort(key=lambda t: t.next_deadline)

        if available_tasks:
            selected_task = available_tasks[0]
            schedule.append(selected_task.name)
            selected_task.remaining_time -= 1
        else:
            schedule.append("Idle")

        time += 1

    return schedule

def edf_gantt(tasks: List[Task], total_time: int):
    # Structure de données pour stocker l'état complet de chaque tâche à chaque instant
    gantt_data = []
    start_time = min(task.arrival_time for task in tasks)
    current_time = start_time
    active_tasks = tasks.copy()

    # Vérifier la faisabilité de l'ordonnancement de manière basique
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
                task.update_after_period()

        # Sélectionner les tâches disponibles
        ready_tasks = [
            t for t in active_tasks 
            if t.arrival_time <= current_time 
            and t.remaining_time > 0 
            and t.next_release - t.period <= current_time
        ]

        # Sélectionner la tâche à exécuter selon EDF
        selected_task = None
        if ready_tasks:
            ready_tasks.sort(key=lambda t: t.next_deadline)
            selected_task = ready_tasks[0]
            selected_task.remaining_time -= 1

        # Collecter les informations d'état pour chaque tâche
        task_states = []
        for task in active_tasks:
            state = {
                "name": task.name,
                "time": current_time,
                "state": "running" if task == selected_task else "waiting" if task in ready_tasks else "idle",
                "deadline": task.next_deadline,
                "remaining": task.remaining_time,
                "period_start": task.next_release - task.period,
                "period_end": task.next_release,
                "execution_time": task.execution_time
            }
            task_states.append(state)

        gantt_data.extend(task_states)
        current_time += 1

    # Si des deadlines ont été manquées, ajouter un avertissement
    if missed_deadlines:
        st.warning(f"Deadlines manquées : {', '.join(missed_deadlines)}")

    return gantt_data
