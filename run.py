# run.py

from flask import Flask
from apps.taco import setup_taco_dashboard
from apps.diet_macors_sheets import setup_diet_macros_sheets_dashboard

app = Flask(__name__)

# Configurações dos Dashboards
setup_taco_dashboard(app)
setup_diet_macros_sheets_dashboard(app)

@app.route('/')
def home():
    return "API Flask rodando!"

if __name__ == "__main__":
    app.run(debug=True)
