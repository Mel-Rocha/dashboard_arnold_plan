from flask import Flask, jsonify, request
import requests
from dash import Dash, dcc, html
import dash
import plotly.express as px
import pandas as pd

app = Flask(__name__)

BASE_URL = "https://3e38-187-48-122-242.ngrok-free.app"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1NzI4NjYyLCJpYXQiOjE3MjU3MjE0NjIsImp0aSI6ImMzYjFlNTI1ZGJkZTQ4NWNiMGVkM2RkODQyM2Y2OGYxIiwidXNlcl9pZCI6Ijk2MTljMmVmLTBhM2EtNDI4MS1hYmQ0LWQyMDA1ZjA1ZTViMiJ9.i9BWoemalCwAGNWMkf77jnwBCcF2QX8bPiaBxYfGmPY"

@app.route('/')
def home():
    return "API Flask rodando!"
# Rota no Flask que obtém todos os dados do Taco sem paginação

@app.route('/dashboard/taco-data', methods=['GET'])
def get_taco_data():
    url = f"{BASE_URL}/taco/taco/all/"  # Constrói a URL completa

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levanta exceção se a resposta não for 200
        data = response.json()
        return jsonify(data)
    except requests.HTTPError as exc:
        return jsonify({"error": str(exc)}), exc.response.status_code
    except Exception as exc:
        return jsonify({"error": "Erro ao buscar dados do Taco"}), 500


# Configuração do Dash
def setup_dash(app):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')

    dash_app.layout = html.Div([
        html.H1("Dashboard Taco"),
        dcc.Graph(id='nutritional-values-graph'),
        dcc.Graph(id='category-distribution-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ])

    @dash_app.callback(
        dash.dependencies.Output('nutritional-values-graph', 'figure'),
        dash.dependencies.Input('interval-component', 'n_intervals')
    )
    def update_nutritional_values_graph(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/taco/taco/all/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data['results'])

            # Criar gráfico de barras para valores nutricionais
            fig = px.bar(df,
                         x='food_description',
                         y=['moisture', 'energy_kcal', 'protein', 'lipids', 'cholesterol', 'carbohydrates',
                            'dietary_fiber', 'ashes'],
                         title="Valores Nutricionais dos Alimentos",
                         labels={"value": "Valor", "food_description": "Descrição do Alimento"})
            fig.update_layout(barmode='group')
            return fig
        except Exception as e:
            return px.bar(title=f"Error: {str(e)}")

    @dash_app.callback(
        dash.dependencies.Output('category-distribution-graph', 'figure'),
        dash.dependencies.Input('interval-component', 'n_intervals')
    )
    def update_category_distribution_graph(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/taco/taco/all/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data['results'])

            # Criar gráfico de pizza para distribuição de categorias
            fig = px.pie(df,
                         names='category',
                         title="Distribuição das Categorias dos Alimentos")
            return fig
        except Exception as e:
            return px.pie(title=f"Error: {str(e)}")

# Configura o Dash com o aplicativo Flask
setup_dash(app)

if __name__ == "__main__":
    app.run(debug=True)
