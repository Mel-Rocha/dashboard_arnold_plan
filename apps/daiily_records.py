import pandas as pd
import requests
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
from dotenv import load_dotenv


import os

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


def setup_daily_records_dashboard(app):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/daily-records/',
                    external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Layout do Dashboard
    dash_app.layout = dbc.Container([
        dbc.Row(dbc.Col(html.H1("Daily Records Dashboard", className="text-center"), width={"size": 6, "offset": 3})),

        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id='date-picker-range',
                start_date=pd.to_datetime('today').strftime('%Y-%m-%d'),
                end_date=pd.to_datetime('today').strftime('%Y-%m-%d'),
                display_format='YYYY-MM-DD',
                max_date_allowed=datetime.today().strftime('%Y-%m-%d')  # Desabilitar datas futuras
            ), width=4),
            dbc.Col(dcc.Dropdown(
                id='meal-dropdown',
                multi=True,
                placeholder='Selecione as Refeições'
            ), width=4)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='meal-status-graph'), width=12),
            dbc.Col(dcc.Graph(id='feeling-status-graph'), width=12),
            dbc.Col(dcc.Graph(id='appetite-status-graph'), width=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(html.H2("Tabela de Aderência"), width=12),
            dbc.Col(html.Div(id='adherence-table'), width=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(html.H2("Insight sobre Aderência ao Plano"), width=12),
            dbc.Col(html.Div(id='adherence-insight'), width=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(html.H2("Insights Detalhados"), width=12),
            dbc.Col(html.Div(id='detailed-insights'), width=12)
        ], className="mb-4"),

        dcc.Interval(
            id='interval-component',
            interval=10 * 60 * 1000,  # Atualiza a cada 10 minutos
            n_intervals=0
        )
    ], fluid=True)

    # Callback para atualizar os gráficos e tabelas
    @dash_app.callback(
        [Output('meal-status-graph', 'figure'),
         Output('feeling-status-graph', 'figure'),
         Output('appetite-status-graph', 'figure'),
         Output('adherence-table', 'children'),
         Output('adherence-insight', 'children'),
         Output('detailed-insights', 'children'),
         Output('meal-dropdown', 'options'),
         Output('meal-dropdown', 'value')],
        [Input('interval-component', 'n_intervals'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('meal-dropdown', 'value')],
        [State('meal-dropdown', 'options')]
    )
    def update_daily_records_graphs(n_intervals, start_date, end_date, selected_meals, meal_options):
        try:
            # Buscar os dados
            response = requests.get(f"{BASE_URL}/daily-records/", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)

            # Converter a coluna 'date' para o formato datetime
            df['date'] = pd.to_datetime(df['date'])

            # Aplicar filtros de data
            if start_date and end_date:
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

            # Verifica se existem refeições disponíveis após a filtragem de data
            if df.empty:
                return px.bar(
                    title="Sem dados disponíveis no intervalo de datas selecionado."), px.bar(), px.bar(), html.Div(
                    "Nenhum dado disponível."), "Nenhum dado para calcular aderência.", "Sem insights detalhados.", [], selected_meals

            # Atualizar o dropdown de refeições com base nos dados filtrados por data
            meal_options = [{'label': f'Refeição {meal}', 'value': meal} for meal in df['meal'].unique()]

            # Se refeições foram selecionadas, filtrar o DataFrame pelas refeições
            if selected_meals:
                df = df[df['meal'].isin(selected_meals)]

            # Formatar a data como 'dd/mm/yyyy'
            df['formatted_date'] = df['date'].dt.strftime('%d/%m/%Y')

            # Gráfico 1: Meal Status ao longo dos dias
            meal_status_fig = px.bar(df, x='formatted_date', y='meal', color='meal_status',
                                     title="Meal Status por Dia", barmode='stack')

            # Gráfico 2: Feeling Status ao longo dos dias
            feeling_status_fig = px.bar(df, x='formatted_date', y='meal', color='feeling_status',
                                        title="Feeling Status por Dia", barmode='group')

            # Gráfico 3: Appetite Status ao longo dos dias
            appetite_status_fig = px.bar(df, x='formatted_date', y='meal', color='appetite_status',
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

            # Prevenir divisão por zero
            adherence_percentage = (completed_meals / total_meals * 100) if total_meals > 0 else 0

            if adherence_percentage >= 80:
                adherence_insight = html.Div(
                    f"O atleta está aderindo bem ao plano. {adherence_percentage:.2f}% das refeições foram concluídas.",
                    style={'color': 'green'})
            else:
                adherence_insight = html.Div(
                    f"O atleta não está aderindo ao plano. Apenas {adherence_percentage:.2f}% das refeições foram concluídas.",
                    style={'color': 'red'})

            # Geração de insights detalhados
            meal_insight = df[df['meal_status'] == 'not_done']['meal'].mode()
            meal_insight_text = f"A refeição com maior taxa de não conclusão é a Refeição {meal_insight.iloc[0]}." if not meal_insight.empty else "Nenhuma refeição não concluída."

            common_feeling = df[df['meal_status'] == 'not_done']['feeling_status'].mode()
            feeling_insight_text = f"O sentimento mais comum nas refeições não concluídas é {common_feeling.iloc[0]}." if not common_feeling.empty else "Sentimento não disponível."

            common_appetite = df[df['meal_status'] == 'not_done']['appetite_status'].mode()
            appetite_insight_text = f"O apetite mais comum durante refeições não concluídas é {common_appetite.iloc[0]}." if not common_appetite.empty else "Apetite não disponível."

            detailed_insights = html.Div([
                html.H3("Insights Detalhados"),
                html.P(meal_insight_text),
                html.P(feeling_insight_text),
                html.P(appetite_insight_text),
            ])

            return meal_status_fig, feeling_status_fig, appetite_status_fig, adherence_table, adherence_insight, detailed_insights, meal_options, selected_meals

        except Exception as e:
            error_fig = px.bar(title=f"Error: {str(e)}")
            error_table = html.Div(f"Erro ao gerar tabela: {str(e)}")
            return error_fig, error_fig, error_fig, error_table, f"Erro ao gerar insight: {str(e)}", f"Erro ao gerar insights detalhados: {str(e)}", [], selected_meals