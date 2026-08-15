# app.py
from flask import Flask
from modules.main import main_bp
from modules.radio import radio_bp
from modules.noticias import noticias_bp
from modules.mtb import mtb_bp  # <--- 1. Importamos el módulo de MTB
from modules.inscripciones import inscripciones_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_muni_rio_piedras'

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# Registro de Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(radio_bp)
app.register_blueprint(noticias_bp)
app.register_blueprint(mtb_bp)  # <--- 2. Registramos el módulo de MTB
app.register_blueprint(inscripciones_bp)

if __name__ == "__main__":
    app.run(debug=True, port=3200, host="0.0.0.0")