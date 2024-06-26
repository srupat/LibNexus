from flask import Flask, request, redirect, url_for, send_file
from flask import render_template, render_template_string
from flask import current_app as app
from application.models import *
from application.forms import ExtendedRegisterForm
from flask_security import login_required, roles_required, current_user
from sqlalchemy import select, update, delete
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Response
import io
import matplotlib.pyplot as plt
import base64

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
        download_path = request.form['path']
        with app.app_context():
            try:
                new_book = Book(content = book_desc, author = book_author, name = book_name, sec_id = section_id, download_path = download_path)
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
        requested_book = BooksUsers.query.filter_by(user_id=user_id, book_id=book_id).first()
        if requested_book:
            if not requested_book.isReturned:
                return 'You have already requested for this book', 400

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
            if bu.isApproved and bu.isReturned:
                completed_book_ids.append(bu.book_id)
            elif bu.isApproved:
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

@app.route("/view-content/<int:book_id>", methods = ["GET"])
def view_content(book_id):
    bu = BooksUsers.query.filter_by(book_id = book_id).first()
    if(bu.return_date < datetime.date(bu.issue_date)):
        return render_template_string('please request this book again!')
    return render_template("view_content.html")

@app.route("/update/section/<int:sec_id>", methods = ["GET", "PUT", "POST"])
def update_section(sec_id):
    if request.method == "GET":
        return render_template("update_sec.html", sec_id = sec_id)
    if request.method == "POST" or request.form.get("_method") == "PUT":
        sec_name = request.form['name']
        desc = request.form['desc']
        section = Section.query.get(sec_id)
        if section:
            section.sec_name = sec_name
            section.desc = desc
            db.session.commit()
            return render_template("success.html")
        else:
            return "section not found", 404
        
@app.route("/delete/section/<int:sec_id>", methods = ["DELETE", "POST"])
def delete_section(sec_id):
    if request.method == "POST" or request.form.get("_method") == "DELETE":
        section = Section.query.get(sec_id)
        if section:
            db.session.delete(section)
            db.session.commit()
            return render_template("success.html")
        else:
            return "section not found", 404
        

@app.route("/update/book/<int:book_id>", methods = ["GET", "PUT", "POST"])
def update_book(book_id):
    if request.method == "GET":
        return render_template("update_book.html", book_id = book_id)
    if request.method == "POST" or request.form.get("_method") == "PUT":
        book_name = request.form['name']
        desc = request.form['desc']
        book_author = request.form['author']
        book = Book.query.get(book_id)
        if book:
            book.name = book_name
            book.desc = desc
            book.author = book_author
            db.session.commit()
            return render_template("success.html")
        else:
            return "book not found", 404
        
@app.route("/delete/book/<int:book_id>", methods = ["DELETE", "POST"])
def delete_book(book_id):
    if request.method == "POST" or request.form.get("_method") == "DELETE":
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return render_template("success.html")
        else:
            return "book not found", 404
        
@app.route("/feedback/<int:book_id>", methods = ["GET", "POST"])
def give_feedback(book_id):
    books_for_user = BooksUsers.query.filter_by(book_id = book_id).first()
    if request.method == "POST":
        if books_for_user:
            feedback = request.form['feedback']
            books_for_user.feedback = feedback
            db.session.commit()
            return render_template("success.html")
        else:
            return "feedback not submitted", 404
        

@app.route("/about", methods = ["GET"])
def about():
    return render_template("about.html")


@app.route('/requests', methods = ["GET", "POST"])
def librarian_requests():
    if request.method == "GET":
        books_users = BooksUsers.query.all()
        requests_not_granted = {}
        requests_granted = {}
        for book_user in books_users:
            book = Book.query.get(book_user.book_id)
            user = User.query.get(book_user.user_id)
            if book_user.isApproved and not book_user.isRejected:
                if user not in requests_granted:
                    requests_granted[user] = [book]
                else:
                    requests_granted[user].append(book)
            if not book_user.isApproved and not book_user.isRejected:
                if user not in requests_not_granted:
                    requests_not_granted[user] = [book]
                else:
                    requests_not_granted[user].append(book)
        return render_template('lib_requests.html', requests_granted = requests_granted, requests_not_granted = requests_not_granted)


@app.route("/reject-access", methods = ["POST"])
def reject_book_access():
    book_id = request.form['book_id']
    book = BooksUsers.query.filter_by(book_id = book_id).first()
    if book:
        book.isApproved = 0
        book.isRejected = 1
        db.session.commit()
        return "Access rejected"
    else:
        return "Book not found", 404
    
@app.route("/revoke-access", methods = ["POST"])
def revoke_book_access():
    book_id = request.form['book_id']
    book = BooksUsers.query.filter_by(book_id = book_id).first()
    if book:
        book.isApproved = 1
        book.isRejected = 1
        db.session.commit()
        return "Access revoked"
    else:
        return "Book not found", 404
    
@app.route("/grant-access", methods = ["POST"])
def grant_book_access():
    book_id = request.form['book_id']
    book = BooksUsers.query.filter_by(book_id = book_id).first()
    if book:
        book.isRejected = 0
        book.isApproved = 1
        db.session.commit()
        return "Access given"
    else:
        return "Book not found", 404
    
@app.route('/section/search', methods=['GET'])
def search_sections():
    query = request.args.get('search_section')
    if query:
        sections = Section.query.filter(Section.sec_name.like("%" + query + "%")).all()
        return render_template('lib_dash.html', sections=sections)
    else:
        return "No search query provided", 400

@app.route('/book/search', methods=['GET'])
def search_books():
    query = request.args.get('search_book')
    if query:
        books = Book.query.filter(Book.name.like("%" + query + "%")).all()
        return render_template('lib_dash.html', books=books)
    else:
        return "No search query provided", 400

@app.route('/lib/stats', methods=['GET'])
def get_stats():
    sections = db.session.query(Section.sec_name, func.count(Book.id)) \
                        .join(Book, Section.sec_id == Book.sec_id) \
                        .group_by(Section.sec_name).all()

    section_names = [sec[0] for sec in sections]
    book_counts = [count for _, count in sections]

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.bar(section_names, book_counts, color='skyblue')
    ax.set_xlabel('Sections')
    ax.set_ylabel('Number of Books')
    ax.set_title('Number of Books in Each Section')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    # plt.close(fig)

    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')

    statuses = db.session.query(BooksUsers.isApproved, BooksUsers.isReturned, BooksUsers.isRejected).all()
    approved_count = sum(status[0] for status in statuses)
    returned_count = sum(status[1] for status in statuses)
    rejected_count = sum(status[2] for status in statuses)

    labels = ['Approved', 'Returned', 'Rejected']
    counts = [approved_count, returned_count, rejected_count]

    fig1 = Figure(figsize=(8, 6))
    ax1 = fig1.add_subplot(111)
    ax1.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    ax1.axis('equal') 
    ax1.set_title('Distribution of Book Status')

    output1 = io.BytesIO()
    FigureCanvas(fig1).print_png(output1)

    pngImageB64String1 = "data:image/png;base64,"
    pngImageB64String1 += base64.b64encode(output1.getvalue()).decode('utf8')
    
    return render_template("lib_stats.html", image=pngImageB64String, image1=pngImageB64String1)



@app.route('/download/<int:book_id>', methods = ['GET'])
def download_book(book_id):
    book = Book.query.get(book_id)
    file_path = book.download_path
    return send_file(file_path, as_attachment=True)


@app.route('/user/stats/<int:user_id>', methods=['GET'])
def books_read_by_section(user_id):
    books_read = db.session.query(Section.sec_name, func.count(Book.id)) \
                           .join(Book, Section.sec_id == Book.sec_id) \
                           .join(BooksUsers, Book.id == BooksUsers.book_id) \
                           .filter(BooksUsers.user_id == user_id) \
                           .group_by(Section.sec_name).all()

    section_names = [sec[0] for sec in books_read]
    book_counts = [count for _, count in books_read]

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.bar(section_names, book_counts, color='skyblue')
    ax.set_xlabel('Sections')
    ax.set_ylabel('Number of Books Read')
    ax.set_title('Number of Books Read by Section')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    pngImageB64String = "data:image/png;base64," + base64.b64encode(output.getvalue()).decode('utf8')

    return render_template("books_read_by_section.html", image=pngImageB64String)
