from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from datetime import datetime

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
    gender = RadioField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')], validators=[DataRequired()])
    birthdate = StringField('Дата рождения', validators=[
        DataRequired(),
        Regexp(r'^\d{2}\.\d{2}\.\d{4}$', message="Формат даты: ДД.ММ.ГГГГ")
    ])
    reg_place = StringField('Место регистрации', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_birthdate(self, field):
        try:
            day, month, year = map(int, field.data.split('.'))
            datetime(year, month, day)
            if datetime(year, month, day).date() > datetime.today().date():
                raise ValidationError("Дата не может быть в будущем")
        except ValueError:
            raise ValidationError("Некорректная дата")
        
class AddEventForm(FlaskForm):
    event_name = StringField('Название события', validators=[DataRequired()])
    event_date = StringField('Дата события', validators=[
        DataRequired(),
        Regexp(r'^\d{2}\.\d{2}\.\d{4}$', message="Формат даты: ДД.ММ.ГГГГ")
    ])
    event_description = StringField('Описание события', validators=[DataRequired()])
    submit = SubmitField('Добавить событие')

    def validate_date(self, field):
        try:
            day, month, year = map(int, field.data.split('.'))
            datetime(year, month, day)
            if datetime(year, month, day).date() < datetime.today().date():
                raise ValidationError("Дата события не может быть в прошлом")
        except ValueError:
            raise ValidationError("Некорректная дата")