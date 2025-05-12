from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from datetime import datetime


def future_birthdate_check():
    """
    Метод для проверки даты рождения на корректность в форме регистрации
    :return: Метод для проверки даты рождения в виде валидатора
    """
    def _future_birthdate_check(form, field):
        try:
            day, month, year = map(int, field.data.split('.'))
            if datetime(year, month, day).date() > datetime.today().date():
                raise ValidationError("Дата не может быть в будущем")
        except ValueError:
            raise ValidationError("Некорректная дата")

    return _future_birthdate_check


class LoginForm(FlaskForm):
    """
    Метод для представления формы для аутентификации
    """
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    """
    Метод для представления формы для регистрации
    """
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    gender = RadioField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')], validators=[DataRequired()])
    birthdate = StringField('Дата рождения', validators=[
        DataRequired(),
        Regexp(r'^\d{2}\.\d{2}\.\d{4}$', message="Формат даты: ДД.ММ.ГГГГ"),
        future_birthdate_check()
    ])
    reg_place = StringField('Место регистрации', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
        
class AddEventForm(FlaskForm):
    date = HiddenField('Дата', validators=[DataRequired()])
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')