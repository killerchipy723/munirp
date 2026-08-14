from flask import Flask, render_template, Response, redirect, url_for, request, flash
import requests

app = Flask(__name__)

# URL del servidor emisor de la radio
STREAM_URL = "http://200.58.106.156:8000/radio.mp3"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/radio")
def radiofm():
    return render_template('fmrio.html')

# --- PROXY PARA TRANSMISIÓN DE RADIO ---
@app.route("/radio.mp3")
def radio_stream():
    def generate():
        try:
            # Obtenemos la señal del servidor remoto en bloques de datos (chunks)
            with requests.get(STREAM_URL, stream=True, timeout=10) as r:
                for chunk in r.iter_content(chunk_size=1024):
                    yield chunk
        except Exception as e:
            print(f"Error en la transmisión de la radio: {e}")

    # Retornamos el flujo con el tipo MIME correcto para audio
    return Response(generate(), mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True, port=3200, host="0.0.0.0")