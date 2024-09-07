from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests
from dotenv import load_dotenv
import dash_table


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
        html.H2("Insights Detalhados"),
        html.Div(id='detailed-insights'),
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
         Output('adherence-insight', 'children'),
         Output('detailed-insights', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_daily_records_graphs(n_intervals):
        try:
            response = requests.get(f"{BASE_URL}/daily-records/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)

            # Converter a coluna 'date' para o formato datetime
            df['date'] = pd.to_datetime(df['date'])
            df['meal'] = df['meal'].astype('category').cat.codes + 1

            # Gráfico 1: Meal Status ao longo dos dias
            meal_status_fig = px.bar(df, x='date', y='meal', color='meal_status',
                                     title="Meal Status por Dia", barmode='stack')

            # Gráfico 2: Feeling Status ao longo dos dias
            feeling_status_fig = px.bar(df, x='date', y='meal', color='feeling_status',
                                        title="Feeling Status por Dia", barmode='group')

            # Gráfico 3: Appetite Status ao longo dos dias
            appetite_status_fig = px.bar(df, x='date', y='meal', color='appetite_status',
                                         title="Appetite Status por Dia", barmode='group')

            # Tabela de resumo de aderência
            adherence_summary = df.groupby('meal_status').size().reset_index(name='count')
            adherence_table = html.Table([
                html.Thead(html.Tr([html.Th("Status da Refeição"), html.Th("Contagem")])),
                html.Tbody([html.Tr([html.Td(status), html.Td(count)]) for status, count in
                            zip(adherence_summary['meal_status'], adherence_summary['count'])])
            ])

            # Calcular aderência ao plano
            total_meals = len(df)
            completed_meals = len(df[df['meal_status'] == 'done'])
            adherence_percentage = (completed_meals / total_meals) * 100

            if adherence_percentage >= 80:
                adherence_insight = html.Div(f"O atleta está aderindo bem ao plano. {adherence_percentage:.2f}% das refeições foram concluídas.",
                                             style={'color': 'green'})
            else:
                adherence_insight = html.Div(f"O atleta não está aderindo ao plano. Apenas {adherence_percentage:.2f}% das refeições foram concluídas.",
                                             style={'color': 'red'})

            # Geração de insights detalhados
            # Insight 1: Qual refeição tem mais não concluídas?
            meal_insight = df[df['meal_status'] == 'not_done']['meal'].mode()
            meal_insight_text = f"A refeição com maior taxa de não conclusão é a Refeição {meal_insight.iloc[0]}."

            # Insight 2: Sentimento predominante nas refeições não concluídas
            common_feeling = df[df['meal_status'] == 'not_done']['feeling_status'].mode()
            feeling_insight_text = f"O sentimento mais comum nas refeições não concluídas é {common_feeling.iloc[0]}."

            # Insight 3: Apetite durante refeições não concluídas
            common_appetite = df[df['meal_status'] == 'not_done']['appetite_status'].mode()
            appetite_insight_text = f"O apetite mais comum durante refeições não concluídas é {common_appetite.iloc[0]}."

            detailed_insights = html.Div([
                html.H3("Insights Detalhados"),
                html.P(meal_insight_text),
                html.P(feeling_insight_text),
                html.P(appetite_insight_text),
            ])

            return meal_status_fig, feeling_status_fig, appetite_status_fig, adherence_table, adherence_insight, detailed_insights

        except Exception as e:
            error_fig = px.bar(title=f"Error: {str(e)}")
            error_table = html.Div(f"Erro ao gerar tabela: {str(e)}")
            return error_fig, error_fig, error_fig, error_table, f"Erro ao gerar insight: {str(e)}", f"Erro ao gerar insights detalhados: {str(e)}"