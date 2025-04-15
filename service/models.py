from flask_login import UserMixin
from service import login_manager

from sc_client.client import generate_elements, search_links_by_contents, get_link_content, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate
from sc_client.constants import sc_types
from sc_kpm import ScKeynodes

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
    template = ScTemplate()
    template.triple(
        ScKeynodes["registered_jurisprudence_user"],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        sc_types.NODE_VAR >> "_user"
    )
    template.triple_with_relation(
        "_user",
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_login",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_login"]
    )

    result = search_by_template(template)
    for _ in result:
        item = _.get("_login")
        item_str = get_link_content(item)[0]
        if item_str.data == username:
            print("OK")
            # todo return user from govno
        else:
            print("False")
