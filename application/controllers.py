from flask import Flask, request, redirect, url_for
from flask import render_template, render_template_string
from flask import current_app as app
from application.models import *
from application.forms import ExtendedRegisterForm
from flask_security import login_required, roles_required
from sqlalchemy import select

@app.route("/", methods = ["GET", "POST"])
@login_required
@roles_required()
def librarian_home():
    return render_template("lib_dash.html")


@app.route("/create/section", methods = ["GET", "POST"])
def sections_home():
    if request.method == "GET":
        return render_template("new_sec.html")
    if request.method == "POST":
        sec_name = request.form['name']
        desc = request.form['desc']
        with app.app_context():
            try:
                new_section = Section(sec_name = sec_name, desc = desc)
                db.session.close_all()
                db.session.add(new_section)
                db.session.commit()
            except:
                db.session.rollback()
                return render_template_string("section already exists")
        sections = Section.query.all()
        return render_template("lib_dash.html", sections = sections, sec_name = sec_name, desc = desc)


