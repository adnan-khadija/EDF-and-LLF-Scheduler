import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from edf_scheduler import Task, lcm_for_periods, edf_gantt
from llf_scheduler import llf_gantt

# Définir les couleurs pour les différents états des tâches
COLORS = {
    "running": "#2ecc71",  # Vert pour tâche en cours d'exécution
    "waiting": "#f1c40f",  # Jaune pour tâche prête
    "idle": "#ecf0f1",    # Gris clair pour tâche inactive
    "deadline": "#e74c3c", # Rouge pour les deadlines
    "period": "#3498db"    # Bleu pour les périodes
}

def create_gantt_figure(gantt_data, start_time, total_time, algorithm="EDF"):
    if not gantt_data:
        return None

    # Créer un DataFrame à partir des données
    df = pd.DataFrame(gantt_data)
    
    # Obtenir la liste unique des tâches
    tasks = sorted(df['name'].unique())
    
    # Créer la figure
    fig = go.Figure()
    
    # Pour chaque tâche
    for i, task_name in enumerate(tasks):
        task_data = df[df['name'] == task_name]
        
        if not task_data.empty:
            # Ajouter les périodes comme des rectangles en arrière-plan
            periods = task_data.drop_duplicates(['period_start', 'period_end'])
            for _, period in periods.iterrows():
                fig.add_shape(
                    type="rect",
                    x0=period['period_start'],
                    x1=period['period_end'],
                    y0=i-0.4,
                    y1=i+0.4,
                    fillcolor=COLORS["period"],
                    opacity=0.3,
                    line_width=0,
                    layer="below"
                )

            # Ajouter les deadlines comme des lignes verticales
            deadlines = task_data.drop_duplicates('deadline')
            for _, deadline in deadlines.iterrows():
                fig.add_shape(
                    type="line",
                    x0=deadline['deadline'],
                    x1=deadline['deadline'],
                    y0=i-0.4,
                    y1=i+0.4,
                    line=dict(color=COLORS["deadline"], width=2, dash="dash"),
                    layer="below"
                )

            # Ajouter les états d'exécution
            for state in ["running", "waiting", "idle"]:
                state_data = task_data[task_data['state'] == state]
                if not state_data.empty:
                    hover_template = (
                        f"Tâche: {task_name}<br>"
                        "Temps: %{x}<br>"
                        f"État: {state}<br>"
                        "Temps restant: %{customdata[0]}<br>"
                        "Prochaine deadline: %{customdata[1]}"
                    )
                    if algorithm == "LLF" and "laxity" in state_data.columns:
                        hover_template += "<br>Laxité: %{customdata[2]}"
                        custom_data = state_data[['remaining', 'deadline', 'laxity']].values
                    else:
                        custom_data = state_data[['remaining', 'deadline']].values

                    fig.add_trace(go.Scatter(
                        x=state_data['time'],
                        y=[i] * len(state_data),
                        mode='markers',
                        marker=dict(
                            size=20,
                            symbol="square",
                            color=COLORS[state]
                        ),
                        name=f"{task_name} ({state})",
                        showlegend=True,
                        hovertemplate=hover_template,
                        customdata=custom_data
                    ))

    # Configurer la mise en page
    fig.update_layout(
        title=f"Diagramme de Gantt ({algorithm})",
        xaxis=dict(
            title="Temps",
            range=[start_time-0.5, total_time+0.5],
            dtick=1
        ),
        yaxis=dict(
            title="Tâches",
            ticktext=tasks,
            tickvals=list(range(len(tasks))),
            range=[-0.5, len(tasks)-0.5]
        ),
        height=100 + 100*len(tasks),  # Hauteur adaptative
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        hovermode='closest'
    )

    return fig

def main():
    st.title("Ordonnanceur EDF/LLF")

    # Sélection de l'algorithme
    algorithm = st.sidebar.radio(
        "Algorithme d'ordonnancement",
        ["EDF", "LLF"],
        help="EDF (Earliest Deadline First) ou LLF (Least Laxity First)"
    )

    with st.sidebar:
        st.header("Ajouter une tâche")
        task_name = st.text_input("Nom de la tâche")
        execution_time = st.number_input("Temps d'exécution", min_value=1, step=1)
        period = st.number_input("Période", min_value=1, step=1)
        deadline = st.number_input("Échéance", min_value=1, step=1)
        arrival_time = st.number_input("Temps d'arrivée", min_value=0, step=1)

        if st.button("Ajouter la tâche"):
            if 'tasks' not in st.session_state:
                st.session_state.tasks = []
            new_task = Task(task_name, execution_time, period, deadline, arrival_time)
            st.session_state.tasks.append(new_task)
            st.success(f"Tâche '{task_name}' ajoutée!")

        if 'tasks' in st.session_state and st.session_state.tasks:
            if st.button("Réinitialiser les tâches"):
                st.session_state.tasks = []
                st.success("Toutes les tâches ont été supprimées!")

    st.header("Liste des Tâches")
    if 'tasks' in st.session_state and st.session_state.tasks:
        task_data = {
            "Nom": [task.name for task in st.session_state.tasks],
            "Temps d'exécution": [task.execution_time for task in st.session_state.tasks],
            "Période": [task.period for task in st.session_state.tasks],
            "Échéance": [task.deadline for task in st.session_state.tasks],
            "Temps d'arrivée": [task.arrival_time for task in st.session_state.tasks]
        }
        task_df = pd.DataFrame(task_data)
        st.dataframe(task_df)

        # Calculer le temps total basé sur le LCM et le premier temps d'arrivée
        periods = [task.period for task in st.session_state.tasks]
        arrival_times = [task.arrival_time for task in st.session_state.tasks]
        start_time = min(arrival_times)
        lcm_time = lcm_for_periods(periods)
        total_time = start_time + lcm_time
        
        st.write(f"Temps de début: {start_time}")
        st.write(f"PPCM des périodes: {lcm_time}")
        st.write(f"Temps total de simulation: {total_time}")

        try:
            # Générer les données du diagramme de Gantt selon l'algorithme choisi
            if algorithm == "EDF":
                gantt_data = edf_gantt(st.session_state.tasks, total_time)
            else:  # LLF
                gantt_data = llf_gantt(st.session_state.tasks, total_time)
            
            # Créer et afficher le diagramme de Gantt
            fig = create_gantt_figure(gantt_data, start_time, total_time, algorithm)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Ajouter des métriques sur l'ordonnancement
            utilization = sum(task.execution_time / task.period for task in st.session_state.tasks) * 100
            st.metric(
                "Taux d'utilisation du processeur",
                f"{utilization:.1f}%",
                delta=f"{100 - utilization:.1f}% de marge",
                delta_color="inverse"
            )
            
        except Exception as e:
            st.error(f"Erreur lors de la génération du diagramme : {str(e)}")
    else:
        st.write("Aucune tâche ajoutée.")

if __name__ == "__main__":
    main()
