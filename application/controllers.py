from flask import Flask, request, redirect, url_for
from flask import render_template, render_template_string
from flask import current_app as app
from application.models import *
from application.forms import ExtendedRegisterForm
from flask_security import login_required, roles_required, current_user
from sqlalchemy import select
from datetime import datetime

@app.route("/", methods = ["GET", "POST"])
@login_required
@roles_required()
def librarian_home():
    sections = Section.query.all()
    books = Book.query.all()
    if('librarian' in current_user.roles):
        return render_template("lib_dash.html", sections = sections)
    else:
        return render_template("user_dash.html", sections = sections, books = books)


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


@app.route("/create/books/<int:section_id>", methods = ["GET", "POST"])
def create_new_book(section_id):
    if request.method == "GET":
        return render_template("new_book.html", section_id = section_id)
    if request.method == "POST":
        book_name = request.form['name']
        book_desc = request.form['desc']
        book_genre = request.form['genre']
        date_of_return_str = request.form['date']
        print(date_of_return_str)
        date_of_return = datetime.strptime(date_of_return_str, '%Y-%m-%d').date()

        with app.app_context():
            try:
                new_book = Book(content = book_desc, genre = book_genre, name = book_name, dor = date_of_return, sec_id = section_id)
                db.session.close_all()
                db.session.add(new_book)
                db.session.commit()
                print("success")
            except Exception as e:
                db.session.rollback()
                print(e)
                return render_template_string("book already exists")
        # query the books here that match with the section id
        return render_template("success.html")
    

@app.route("/view/books/<int:section_id>", methods = ["GET"])
def view_books(section_id):
    books = Book.query.filter_by(sec_id = section_id).all()
    return render_template("sec_books.html", books = books)


