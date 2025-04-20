import uuid
from typing import Optional
from flask_login import UserMixin
from service import login_manager
from pydantic.dataclasses import dataclass

from sc_client.client import get_link_content, search_by_template
from sc_client.models import ScTemplate, ScAddr
from sc_client.constants import sc_types
from sc_kpm import ScKeynodes

@dataclass
class DirectoryResponse:
    title: str
    content: str

    def __str__(self) -> str:
        truncated = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"{self.title}: {truncated}"

@dataclass
class RequestResponse:
    content:str

    def __str__(self) -> str:
        return f"{self.content}"

class User(UserMixin):
    def __init__(
        self,
        sc_addr: str | None,
        gender: str,
        surname: str,
        name: str,
        fname: str,
        birthdate: str,
        reg_place: str,
        username: str,
        password: str
    ):
        self._sc_addr = sc_addr 
        self.gender = gender
        self.surname = surname
        self.name = name
        self.fname = fname
        self.birthdate = birthdate
        self.reg_place = reg_place
        self.username = username
        self.password = password

    @property
    def get_sc_addr_str(self):
        return self._sc_addr.value

    def get_id(self):
        return str(self.username)

    def __repr__(self):
        return f'<User {self.username} [{self.sc_addr_str}]>'

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
    template.triple_with_relation(
        user,
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.NODE_VAR >> "_birthdate",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_birthdate"]
    )
    result = search_by_template(template)[0]
    return User(
        sc_addr=str(user.value),
        gender=result.get("_gender"),
        surname=result.get("_surname"),
        name=result.get("_name"),
        fname=result.get("_patronymic"),
        birthdate=result.get("_birthdate"),
        reg_place=result.get("_address"),
        username=result.get("_login"),
        password=result.get("_password")
    )

@login_manager.user_loader
def load_user(username: str) -> Optional[User]:
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
    search_result = search_by_template(template)
    for result in search_result:
        try:
            return collect_user_info(result.get("_user"))
        except Exception as e:
            print(f"Error loading user: {e}")
    return None

def find_user_by_username(username: str) -> Optional[User]:
    template = ScTemplate()
    template.triple_with_relation(
        sc_types.NODE_VAR >> "_user",
        sc_types.EDGE_D_COMMON_VAR,
        sc_types.LINK_VAR >> "_login",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_user_login"]
    )
    
    results = search_by_template(template)
    
    for result in results:
        login_content = get_link_content(result.get("_login"))[0].data
        if login_content == username:
            return collect_user_info(result.get("_user"))
    return None