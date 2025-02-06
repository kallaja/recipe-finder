from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, EqualTo, Length, DataRequired, Regexp


class RegisterForm(FlaskForm):
    """A form to register new users."""
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Password",
                             validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match'),
                                         Length(min=8),
                                         Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                                         message='Password must contain at least one uppercase letter, '
                                                 'one lowercase letter, one number, and one special character.')])
    confirm_password = PasswordField('Repeat Password', validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    """A form to login existing users."""
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")
