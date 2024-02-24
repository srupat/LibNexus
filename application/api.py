from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import User, Book
from application.validation import *

output_fields = {
    "user_id" : fields.Integer,
    "username" : fields.String,
    "email" : fields.String
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('email')

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('email')

class UserAPI(Resource):
    @marshal_with(output_fields)
    def get(self, username):
        
        print('In UserAPI GET Method', username)
        user = db.session.query(User).filter(User.username == username).first()

        if user:
            return user
        else:
            raise NotFoundError(status_code = 404)

    @marshal_with(output_fields)
    def put(self, username):
        args = update_user_parser.parse_args()
        email = args.get('email', None)
        
        if email is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1002", error_message = "email is required")
        
        if '@' in email:
            pass
        else:
            raise BusinessValidationError(status_code = 400, error_code = "BE1003", error_message = "invalid email")
        
        user = db.session.query(User).filter(User.email == email).first()

        if user:
            raise BusinessValidationError(status_code = 400, error_code = "BE1006", error_message = "duplicate email")
        
        user = db.session.query(User).filter(User.username == username).first()

        if user is None:
            raise NotFoundError(status_code = 404)
        
        user.email = email
        db.session.add(user)
        db.session.commit()

        return user
        


    def delete(self, username):
        user = db.session.query(User).filter(User.username == username).first()

        if user is None:
            raise NotFoundError(status_code = 404)
        db.session.delete(user)
        db.session.commit()
        return "", 200

    @marshal_with(output_fields)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)

        if username is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1001", error_message = "username is required")
        
        if email is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1002", error_message = "email is required")
        
        if '@' in email:
            pass
        else:
            raise BusinessValidationError(status_code = 400, error_code = "BE1003", error_message = "invalid email")
        
        user = db.session.query(User).filter((User.username == username) | (User.email == email)).first()

        if user:
            raise BusinessValidationError(status_code = 400, error_code = "BE1004", error_message = "duplicate user")
        
        new_user = User(username= username, email = email)
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201
    
