# run.py

from flask import Flask, render_template_string
from apps.taco import setup_taco_dashboard
from apps.diet_macors_sheets import setup_diet_macros_sheets_dashboard
from apps.meal_macros_sheets import setup_meal_macros_sheets_dashboard

app = Flask(__name__)

# Configurações dos Dashboards
setup_taco_dashboard(app)
setup_diet_macros_sheets_dashboard(app)
setup_meal_macros_sheets_dashboard(app)

@app.route('/')
def home():
    return render_template_string("""
        <html>
        <head><title>API Dashboard</title></head>
        <body>
            <h1>API Dashboard</h1>
            <button onclick="window.location.href='/dashboard/taco/'">Taco Data Dashboard</button><br><br>
            <button onclick="window.location.href='/dashboard/macros/'">Diet Macros Sheets Dashboard</button><br><br>
            <button onclick="window.location.href='/dashboard/meal-macros/'">Meal Macros Sheets Dashboard</button><br><br>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
