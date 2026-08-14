# app.py
from flask import Flask
from modules.main import main_bp
from modules.radio import radio_bp
from modules.noticias import noticias_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_muni_rio_piedras'

# Registro de Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(radio_bp)
app.register_blueprint(noticias_bp)

if __name__ == "__main__":
    app.run(debug=True, port=3200, host="0.0.0.0")