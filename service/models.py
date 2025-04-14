from flask_login import UserMixin
from service import login_manager

from sc_client.client import generate_elements, search_links_by_contents, get_link_content
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction


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
        self.reg_place = reg_place
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
@login_manager.user_loader
def load_user(username):
    print(username)
    link = search_links_by_contents(username)
    print(type(link))
    for _ in link:
        print(f"{len(_)}")
        for i in _:
            print(f"{i.is_valid()} CONTENT")
