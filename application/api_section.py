from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import *
from application.validation import *

output_fields = {
    "sec_id" : fields.Integer,
    "sec_name" : fields.String
}

create_sec_pareser = reqparse.RequestParser()
create_sec_pareser.add_argument('sec_name')

update_sec_parser = reqparse.RequestParser()
update_sec_parser.add_argument('sec_name')

class SectionAPI(Resource):
    @marshal_with(output_fields)
    def get(self, sec_name):
        
        print('In SectionAPI GET Method', sec_name)
        section = db.session.query(Section).filter(Section.sec_name == sec_name).first()

        if section:
            return section
        else:
            raise NotFoundError(status_code = 404)

    @marshal_with(output_fields)
    def put(self, sec_name):
        args = update_sec_parser.parse_args()
        name = args.get('sec_name', None)
        
        if name is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1002", error_message = "name is required")
        
        section = db.session.query(Section).filter(Section.sec_name == name).first()

        if section:
            raise BusinessValidationError(status_code = 400, error_code = "BE1006", error_message = "duplicate section")

        if section is None:
            raise NotFoundError(status_code = 404)
        
        section.sec_name = name
        db.session.add(section)
        db.session.commit()

        return section
        


    def delete(self, sec_id):
        section = db.session.query(Section).filter(Section.sec_id == sec_id).first()

        if section is None:
            raise NotFoundError(status_code = 404)
        db.session.delete(section)
        db.session.commit()
        return "", 200

    @marshal_with(output_fields)
    def post(self):
        args = create_sec_pareser.parse_args()
        name = args.get("sec_name", None)

        if name is None:
            raise BusinessValidationError(status_code = 400, error_code = "BE1001", error_message = "section name is required")
        
        section = db.session.query(Section).filter(Section.sec_name == name).first()

        if section:
            raise BusinessValidationError(status_code = 400, error_code = "BE1004", error_message = "duplicate section")
        
        new_section = Section(sec_name = name)
        db.session.add(new_section)
        db.session.commit()
        return new_section, 201
    
