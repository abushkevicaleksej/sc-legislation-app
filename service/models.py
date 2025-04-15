from flask_login import UserMixin
from service import login_manager

from sc_client.client import generate_elements, search_links_by_contents, get_link_content, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
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

def collect_user_info(user: ScAddr) -> User:
    template = ScTemplate()
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_login",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_login"]
    )
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_password",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_password"]
    )
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_surname",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_surname"]
    )
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_name",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_name"]
    )
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_patronymic",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_patronymic"]
    )
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_address",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_address"]
    )
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.NODE_VAR >> "_gender",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_gender"]
    )
    result = search_by_template(template)[0]
    user = User(
        gender=result.get("_gender"),
        surname=result.get("_surname"),
        name=result.get("_name"),
        fname=result.get("_patronymic"),
        birthdate=None,
        reg_place=result.get("_address"),
        username=result.get("_login"),
        password=result.get("_password")
    )
    print(user)
    return user

    
@login_manager.user_loader
def load_user(username):
    current_user = None
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
    result_item = search_by_template(template)[0]
    for _ in result:
        item = _.get("_login")
        item_str = get_link_content(item)[0]
        if item_str.data == username:
            print("OK")
            current_user = collect_user_info(result_item.get("_user"))

        else:
            print("False")
    return current_user