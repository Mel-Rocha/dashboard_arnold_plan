import requests
from flask import Flask
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from dotenv import load_dotenv

import os

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


def setup_meal_macros_sheets_dashboard(app):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/meal-macros/')

    dash_app.layout = html.Div([
        html.H1("Dashboard Meal Macros Sheets"),
        dcc.Graph(id='macros-grams-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ])

    @dash_app.callback(
        Output('macros-grams-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_macros_grams_graph(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/macros-sheet/meal-macros-sheets/all/",
                                    headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)

            # Substitui os IDs por números sequenciais
            df['id'] = range(1, len(df) + 1)

            # Gráfico de colunas agrupadas para macros nutrientes em gramas
            fig_macros_grams = px.bar(df,
                                      x='id',
                                      y=['cho', 'ptn', 'fat'],
                                      title="Macronutrientes em Gramas",
                                      labels={"value": "Gramas", "id": "ID"},
                                      color_discrete_map={"cho": "blue", "ptn": "orange", "fat": "green"})
            fig_macros_grams.update_layout(barmode='group')

            return fig_macros_grams
        except Exception as e:
            return px.bar(title=f"Error: {str(e)}")
