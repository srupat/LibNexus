from flask import Flask, request
from flask import render_template
from flask import current_app as app
from application.models import Article
from flask_security import login_required, roles_required

@app.route("/", methods = ["GET", "POST"])
def sections():
    return render_template("<html><title>Dashboard</title><body>Sections</body></html>")