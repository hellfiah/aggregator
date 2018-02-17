from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import InputRequired, data_required, Email, Length


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class AddAccountForm(FlaskForm):
    type_id = SelectField('account type id', choices=[])


class RemoveAccountForm(FlaskForm):
    remove_account_id = HiddenField('account id', validators=[data_required()])


class UploadForm(FlaskForm):
    upload_account_id = HiddenField('account id', validators=[data_required()])
    csv_file = FileField('csv upload', validators=[FileRequired(), FileAllowed(['csv'], 'CSVs only!')])


class RemoveUploadForm(FlaskForm):
    upload_id = HiddenField('upload id', validators=[data_required()])
