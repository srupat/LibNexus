from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import *
from application.validation import *

output_fields = {
    "book_author" : fields.String,
    "book_name" : fields.String,
    "book_path" : fields.String
}

create_book_parser = reqparse.RequestParser()
create_book_parser.add_argument('book_author')
create_book_parser.add_argument('book_name')
create_book_parser.add_argument('book_path')

update_book_parser = reqparse.RequestParser()
update_book_parser.add_argument('book_name')

class BookAPI(Resource):
    @marshal_with(output_fields)
    def get(self, book_id):
        
        print('In BookAPI GET Method', book_id)
        book = db.session.query(Book).filter(Book.id == book_id).first()

        if book:
            return book
        else:
            raise NotFoundError(status_code = 404)

    @marshal_with(output_fields)
    def put(self, book_id):
        args = update_book_parser.parse_args()
        name = args.get('book_name', None)
        
        if name is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1002", error_message = "name is required")
        
        book = db.session.query(Book).filter(Book.name == name).first()

        if book:
            raise BusinessValidationError(status_code = 400, error_code = "BE1006", error_message = "duplicate book")
        
        book = db.session.query(User).filter(Book.id == book_id).first()

        if book is None:
            raise NotFoundError(status_code = 404)
        
        Book.name = name
        db.session.add(book)
        db.session.commit()

        return book
        


    def delete(self, book_id):
        book = db.session.query(Book).filter(Book.id == book_id).first()

        if book is None:
            raise NotFoundError(status_code = 404)
        db.session.delete(book)
        db.session.commit()
        return "", 200

    @marshal_with(output_fields)
    def post(self):
        args = create_book_parser.parse_args()
        author = args.get("book_author", None)
        name = args.get("book_name", None)
        path = args.get("book_path", None)

        if author is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1001", error_message = "author name is required")
        
        if name is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1002", error_message = "name of book is required")
        
        
        book = db.session.query(Book).filter((Book.author == author) | (Book.name == name)).first()

        if book:
            raise BusinessValidationError(status_code = 400, error_code = "BE1004", error_message = "duplicate book")
        
        new_book = Book(name= name, author = author)
        db.session.add(new_book)
        db.session.commit()
        return new_book, 201
    
