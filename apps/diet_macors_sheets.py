from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests
from dotenv import load_dotenv

import os

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


def setup_diet_macros_sheets_dashboard(app):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/macros/')

    dash_app.layout = html.Div([
        html.H1("Dashboard Diet Macros Sheets"),
        dcc.Graph(id='macros-data-graph'),
        dcc.Graph(id='calories-data-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ])

    @dash_app.callback(
        [Output('macros-data-graph', 'figure'),
         Output('calories-data-graph', 'figure')],
        Input('interval-component', 'n_intervals')
    )
    def update_macros_data_graph(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/macros-sheet/diet-macros-sheets/all/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)

            # Gráfico de colunas agrupadas para macronutrientes
            macros_fig = px.bar(df,
                               x='id',
                               y=['cho', 'ptn', 'fat'],
                               title="Dados de Macronutrientes",
                               labels={"value": "Valor", "id": "ID"})
            macros_fig.update_layout(barmode='group')

            # Gráfico de linhas para calorias
            calories_fig = px.line(df,
                                  x='id',
                                  y='kcal',
                                  title="Calorias",
                                  labels={"kcal": "Calorias", "id": "ID"})

            return macros_fig, calories_fig
        except Exception as e:
            error_fig = px.bar(title=f"Error: {str(e)}")
            return error_fig, error_fig

