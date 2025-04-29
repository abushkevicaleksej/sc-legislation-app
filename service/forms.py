from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    gender = RadioField('Пол', validators=[DataRequired()])
    birthdate = StringField('Дата рождения', default=date.today(), validators=[DataRequired(), ])
    address = StringField('Адрес регистрации', validators=[DataRequired()])
    submit = SubmitField('Регистрация')

    def validate_on_submit(self):
        result = super(RegistrationForm, self).validate()
        if (self.birthdate > date.today()):
            return False
        else:
            return True