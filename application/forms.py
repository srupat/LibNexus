from flask_security.forms import ConfirmRegisterForm, LoginForm
from wtforms import StringField, PasswordField
from flask_security.forms import Required, EqualTo
from flask_security.utils import _datastore, get_message


class ExtendedRegisterForm(ConfirmRegisterForm):
    username = StringField("Username", [Required()])
    email = StringField("Email", [Required()])
    password = PasswordField("Password", [Required()])
    confirm_password = PasswordField("Confirm Password", [EqualTo('password', message='Passwords must match')])

    def validate(self):
        if not super(ExtendedRegisterForm, self).validate():
            return False

        user_by_username = _datastore.get_user(self.username.data)
        user_by_email = _datastore.get_user(self.email.data)

        if user_by_username:
            self.username.errors.append(get_message("USERNAME_ALREADY_EXISTS")[0])
            return False

        if user_by_email:
            self.email.errors.append(get_message("EMAIL_ALREADY_EXISTS")[0])
            return False

        return True


class ExtendedLoginForm(LoginForm):
    email = StringField("Username or Email Address")
    username = StringField("Username")

    def validate(self):
        from flask_security.utils import (
            _datastore,
            get_message,
            hash_password,
        )
        from flask_security.confirmable import requires_confirmation

        if not super(LoginForm, self).validate():
            return False

        self.user = _datastore.get_user(self.email.data)

        if self.user is None:
            self.user = _datastore.get_user(self.username.data)

        if self.user is None:
            self.email.errors.append(get_message("USER_DOES_NOT_EXIST")[0])
            hash_password(self.password.data)
            return False
        if not self.user.password:
            self.password.errors.append(get_message("PASSWORD_NOT_SET")[0])
            hash_password(self.password.data)
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message("CONFIRMATION_REQUIRED")[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message("DISABLED_ACCOUNT")[0])
            return False
        return True