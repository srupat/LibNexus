from flask import Flask, request, redirect, url_for
from flask import render_template, render_template_string
from flask import current_app as app
# from application.models import *
from application.forms import ExtendedRegisterForm
from flask_security import login_required, roles_required

@app.route("/", methods = ["GET", "POST"])
@login_required
@roles_required()
def sections():
    return render_template("lib_dash.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and ExtendedRegisterForm(request.form).validate():
        return redirect(url_for('login'))

    return render_template('register.html', form=ExtendedRegisterForm())