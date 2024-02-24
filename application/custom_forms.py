from flask_security.forms import RegisterForm, LoginForm, Required
from wtforms import StringField, validators

class ExtendedRegisterForm(RegisterForm):
    username = StringField('Username', [Required()])

class ExtendedLoginForm(LoginForm):
    username = StringField('Username', [Required()])