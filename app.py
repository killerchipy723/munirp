from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/radio")
def radiofm():
     return render_template('fmrio.html')

if __name__ == "__main__":
     app.run(debug=True, port=3200, host="0.0.0.0")