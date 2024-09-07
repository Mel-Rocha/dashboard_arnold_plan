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





def setup_daily_records_dashboard(app):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/daily-records/')

    dash_app.layout = html.Div([
        html.H1("Daily Records Dashboard"),
        dcc.Graph(id='meal-status-graph'),
        dcc.Graph(id='feeling-status-graph'),
        dcc.Graph(id='appetite-status-graph'),
        html.H2("Tabela de Aderência"),
        html.Div(id='adherence-table'),
        html.H2("Insight sobre Aderência ao Plano"),
        html.Div(id='adherence-insight'),
        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ])

    @dash_app.callback(
        [Output('meal-status-graph', 'figure'),
         Output('feeling-status-graph', 'figure'),
         Output('appetite-status-graph', 'figure'),
         Output('adherence-table', 'children'),
         Output('adherence-insight', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_daily_records_graphs(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/daily-records/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)

            # Converter a coluna 'date' para o formato datetime e garantir que o eixo mostre todas as datas corretamente
            df['date'] = pd.to_datetime(df['date'])

            # Substituir ID de refeição por um número sequencial ou nome fictício para fins de visualização
            df['meal'] = df['meal'].astype('category').cat.codes + 1

            # Gráfico 1: Meal Status ao longo dos dias
            meal_status_fig = px.bar(df, x='date', y='meal', color='meal_status',
                                     title="Meal Status por Dia",
                                     labels={"meal": "Refeição", "date": "Dia"},
                                     barmode='stack')

            # Gráfico 2: Feeling Status ao longo dos dias
            feeling_status_fig = px.bar(df, x='date', y='meal', color='feeling_status',
                                        title="Feeling Status por Dia",
                                        labels={"meal": "Refeição", "date": "Dia"},
                                        barmode='group')

            # Gráfico 3: Appetite Status ao longo dos dias
            appetite_status_fig = px.bar(df, x='date', y='meal', color='appetite_status',
                                         title="Appetite Status por Dia",
                                         labels={"meal": "Refeição", "date": "Dia"},
                                         barmode='group')

            # Atualizar o layout dos gráficos para garantir que todos os dias sejam mostrados no eixo x
            meal_status_fig.update_xaxes(dtick="D", tickformat="%b %d %Y")
            feeling_status_fig.update_xaxes(dtick="D", tickformat="%b %d %Y")
            appetite_status_fig.update_xaxes(dtick="D", tickformat="%b %d %Y")

            # Atualizar o layout dos gráficos para garantir que todos os dias sejam mostrados no eixo x
            meal_status_fig.update_xaxes(dtick="D", tickformat="%b %d %Y")
            feeling_status_fig.update_xaxes(dtick="D", tickformat="%b %d %Y")
            appetite_status_fig.update_xaxes(dtick="D", tickformat="%b %d %Y")

            # Tabela de resumo de refeições (concluídas, não concluídas)
            adherence_summary = df.groupby('meal_status').size().reset_index(name='count')
            adherence_table = html.Table([
                html.Thead(html.Tr([html.Th("Status da Refeição"), html.Th("Contagem")])),
                html.Tbody([html.Tr([html.Td(status), html.Td(count)]) for status, count in
                            zip(adherence_summary['meal_status'], adherence_summary['count'])])
            ])

            # Ajustar o cálculo de adesão ao plano:
            total_meals = len(df)
            completed_meals = len(
                df[df['meal_status'] == 'done'])  # Considerando apenas as refeições com status "done" como concluídas

            adherence_percentage = (completed_meals / total_meals) * 100

            # Definir o insight com base na porcentagem de refeições concluídas
            if adherence_percentage >= 80:  # Critério: Mais de 80% das refeições foram concluídas
                adherence_insight = f"O atleta está aderindo bem ao plano. {adherence_percentage:.2f}% das refeições foram concluídas."
            else:
                adherence_insight = f"O atleta não está aderindo ao plano. Apenas {adherence_percentage:.2f}% das refeições foram concluídas."

            return meal_status_fig, feeling_status_fig, appetite_status_fig, adherence_table, adherence_insight
        except Exception as e:
            error_fig = px.bar(title=f"Error: {str(e)}")
            error_table = html.Div(f"Erro ao gerar tabela: {str(e)}")
            return error_fig, error_fig, error_fig, error_table, f"Erro ao gerar insight: {str(e)}"