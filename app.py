# app.py
from flask import Flask
from modules.main import main_bp
from modules.radio import radio_bp
from modules.noticias import noticias_bp
from modules.mtb import mtb_bp  # <--- 1. Importamos el módulo de MTB
from modules.inscripciones import inscripciones_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_muni_rio_piedras'
# --- MANEJADOR DE ERROR PARA ARCHIVOS GRANDES ---
@app.errorhandler(413)
def request_entity_too_large(error):
    # Esto captura el error automáticamente si el usuario sube algo > 32MB
    return "La imagen es demasiado grande. Por favor, sube una foto de menos de 32MB.", 413

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


# Registro de Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(radio_bp)
app.register_blueprint(noticias_bp)
app.register_blueprint(mtb_bp)  # <--- 2. Registramos el módulo de MTB
app.register_blueprint(inscripciones_bp)

if __name__ == "__main__":
    app.run(debug=True, port=3200, host="0.0.0.0")