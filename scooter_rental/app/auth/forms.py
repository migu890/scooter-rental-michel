from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired(), Length(min=3, max=40)])
    email = StringField("E-Mail", validators=[DataRequired(), Email()])
    role = SelectField("Rolle", choices=[("rider", "Rider"), ("provider", "Provider")], validators=[DataRequired()])
    password = PasswordField("Passwort", validators=[DataRequired(), Length(min=8, max=64)])
    password2 = PasswordField("Passwort wiederholen", validators=[DataRequired(), EqualTo("password")])

class LoginForm(FlaskForm):
    username = StringField("Benutzername oder E-Mail", validators=[DataRequired()])
    password = PasswordField("Passwort", validators=[DataRequired()])