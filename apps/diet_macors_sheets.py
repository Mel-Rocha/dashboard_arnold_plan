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
        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ])

    @dash_app.callback(
        Output('macros-data-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_macros_data_graph(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/macros-sheet/diet-macros-sheets/all/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)
            fig = px.bar(df, x='id', y=['cho', 'ptn', 'fat', 'kcal'], title="Dados de Macronutrientes", labels={"value": "Valor", "id": "ID"})
            fig.update_layout(barmode='group')
            return fig
        except Exception as e:
            return px.bar(title=f"Error: {str(e)}")
