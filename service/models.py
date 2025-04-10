from flask_login import UserMixin

from run import login

class User(UserMixin):
    def __init__(
        self,
        gender: str, 
        surname: str,
        name: str,
        fname: str,
        birthdate,
        reg_place: str,
        username: str,
        password: str
        ):
        self.gender = gender
        self.surname = surname
        self.name = name
        self.fname = fname
        self.birthdate = birthdate
        self.reg_place = reg_place,
        self.username = username
        self.password = password

@login.user_loader
def load_user(id):
    pass