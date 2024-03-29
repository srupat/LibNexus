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
        book_author = request.form['author']
        date_of_return_str = request.form['date']
        print(date_of_return_str)
        date_of_return = datetime.strptime(date_of_return_str, '%Y-%m-%d').date()

        with app.app_context():
            try:
                new_book = Book(content = book_desc, author = book_author, name = book_name, dor = date_of_return, sec_id = section_id)
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


@app.route("/books/request/<int:user_id>/<int:book_id>", methods = ["GET", "POST"])
def request_books(user_id, book_id):
    if request.method == "GET":
        books_for_user = BooksUsers.query.filter_by(user_id = user_id).all()
        print(len(books_for_user))
        if(len(books_for_user) > 5):
            return render_template("failure.html")
        return render_template("request_book.html", user_id = user_id, book_id = book_id)
    if request.method == "POST":
        with app.app_context():
            
            try:
                date_of_return_str = request.form['date']
                date_of_return = datetime.strptime(date_of_return_str, '%Y-%m-%d').date()
                print(date_of_return_str)
                newBookIssue = BooksUsers(return_date = date_of_return, user_id = user_id, book_id = book_id)
                db.session.close_all()
                db.session.add(newBookIssue)
                db.session.commit()
                print("success")
            except Exception as e:
                db.session.rollback()
                print(e)
                return render_template_string("user has already issued this book")
        return render_template("success.html")
    

@app.route("/my-books", methods = ["GET", "POST"])
def my_books():
    if request.method == "GET": 
        books_users = BooksUsers.query.filter_by(user_id = current_user.id).all()
        completed_book_ids = []
        current_book_ids = []
        for bu in books_users:
            if bu.isCompleted:
                completed_book_ids.append(bu.book_id)
            elif not bu.isReturned:
                current_book_ids.append(bu.book_id)

        user_current_books = Book.query.filter(Book.id.in_(current_book_ids)).all()
        user_completed_books = Book.query.filter(Book.id.in_(completed_book_ids)).all()
        return render_template("my_books.html", current = user_current_books, completed = user_completed_books)
    elif request.method == "POST":
        book_id = request.form.get('book_id')
        print(book_id)
        if book_id is not None:
            return return_book(int(book_id))
        else:
            return "No book ID provided in the form", 400

@app.route("/return/<int:book_id>", methods = ["POST"])
def return_book(book_id):
    book = BooksUsers.query.filter_by(book_id = book_id).first()
    print(book.isReturned)
    if book:
        book.isReturned = 1
        db.session.commit()
        return "Book updated successfully"
    else:
        return "Book not found", 404
    
@app.route("/view/<int:book_id>", methods = ["GET"])
def view_book_info(book_id):
    book = Book.query.get(book_id)
    return render_template("book_info.html", book = book)

@app.route("/view-content", methods = ["GET"])
def view_content():
    return render_template("view_content.html")

