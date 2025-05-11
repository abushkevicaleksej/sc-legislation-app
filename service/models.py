from typing import Optional, List
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
        return f"{self.title}: {self.content}"

@dataclass
class RequestResponse:
    term: str
    content: str
    related_concepts: List[str] = None
    related_articles: List[str] = None

    def __post_init__(self):
        self.related_concepts = self.related_concepts or []
        self.related_articles = self.related_articles or []

    def __str__(self) -> str:
        return f"{self.term} {self.content}"
    
@dataclass   
class AppEvent:
    user: str
    title: str
    date: str
    content: str

@dataclass
class EventResponse:
    events: list[AppEvent]

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
    
    def __str__(self):
        return (
            f"User: {self._sc_addr}\n"
            f"Gender: {self.gender}\n"
            f"Surname: {get_link_content(self.surname)[0].data}\n"
            f"Name: {get_link_content(self.name)[0].data}\n"
            f"Father's Name: {get_link_content(self.fname)[0].data}\n"
            f"Birthdate: {get_link_content(self.birthdate)[0].data}\n"
            f"Registration Place: {get_link_content(self.reg_place)[0].data}\n"
            f"Username: {get_link_content(self.username)[0].data}\n"
            f"Password: {get_link_content(self.password)[0].data}"
        )

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