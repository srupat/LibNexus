import os
from flask import Flask, request
from flask import render_template
from application.config import LocalDevelopmentConfig

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)

    return app


app = create_app()

@app.route("/", methods=["GET", "POST"])
def test():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8081)
    app.debug = True