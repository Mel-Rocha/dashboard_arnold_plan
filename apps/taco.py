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

def setup_taco_dashboard(app):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/taco/')

    dash_app.layout = html.Div([
        html.H1("Dashboard Taco"),
        dcc.Graph(id='category-distribution-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ])

    @dash_app.callback(
        Output('category-distribution-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_category_distribution_graph(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/taco/taco/all/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data['results'])
            fig = px.pie(df, names='category', title="Distribuição das Categorias dos Alimentos")
            return fig
        except Exception as e:
            return px.pie(title=f"Error: {str(e)}")
