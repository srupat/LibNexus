from flask import Flask, request
from flask import render_template, render_template_string
from flask import current_app as app
# from application.models import *
from flask_security import login_required, roles_required

@app.route("/", methods = ["GET", "POST"])
@login_required
@roles_required
def sections():
    return render_template_string("Sections")