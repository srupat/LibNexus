import os
from flask import Flask, request
from flask import render_template, render_template_string
from application.config import LocalDevelopmentConfig
from flask_restful import Resource, Api
from application.database import db
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from application.models import Role, User, Section, Book
# from application.controllers import *
from flask_security import login_required, roles_required, auth_required
from application.forms import *


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)  
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    app.app_context().push()
    return app, api
    


app, api = create_app()

from application.api import *
api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>")


from application.controllers import *


@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8085)
    app.debug = True