# modules/radio.py
from flask import Blueprint, render_template, Response
import requests

radio_bp = Blueprint('radio', __name__)
STREAM_URL = "http://200.58.106.156:8000/radio.mp3"

@radio_bp.route("/radio")
def radiofm():
    return render_template('fmrio.html')

@radio_bp.route("/radio.mp3")
def radio_stream():
    def generate():
        try:
            with requests.get(STREAM_URL, stream=True, timeout=10) as r:
                for chunk in r.iter_content(chunk_size=1024):
                    yield chunk
        except Exception as e:
            print(f"Error en radio: {e}")

    return Response(generate(), mimetype="audio/mpeg")