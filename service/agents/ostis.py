from enum import Enum
import sc_client.client as client
from exceptions import ScServerError
from sc_client.client import is_connected
from sc_client.models import (
    ScAddr,
    ScEventSubscriptionParams,
    ScConstruction,
    ScIdtfResolveParams,
    ScLinkContent,
    ScLinkContentType,
    ScTemplate,
)
from sc_client.constants.common import ScEventType
from sc_client.constants import sc_types
from threading import Event

from service.agents.abstract.auth_agent import AuthAgent, AuthStatus
from service.agents.abstract.reg_agent import RegAgent, RegStatus, Gender
from config import Config
from service.exceptions import AgentError

payload = None
callback_event = Event()


def create_link(client, content: str):
    construction = ScConstruction()
    to_find_content = ScLinkContent(content, ScLinkContentType.STRING)
    construction.create_link(sc_types.LINK_CONST, to_find_content)
    link = client.generate_elements(construction)
    return link[0]


def get_node(client) -> ScAddr:
    construction = ScConstruction()
    construction.create_node(sc_types.NODE_CONST)
    main_node: ScAddr = client.generate_elements(construction)[0]
    return main_node


def call_back(src: ScAddr, connector: ScAddr, trg: ScAddr) -> Enum:
    global payload
    callback_event.clear()

    succ_node = client.resolve_keynodes(
        ScIdtfResolveParams(idtf='action_finished_successfully', type=sc_types.NODE_CONST_CLASS)
    )[0]
    unsucc_node = client.resolve_keynodes(
        ScIdtfResolveParams(idtf='action_finished_unsuccessfully', type=sc_types.NODE_CONST_CLASS)
    )[0]
    node_err = client.resolve_keynodes(
        ScIdtfResolveParams(idtf='action_finished_with_error', type=sc_types.NODE_CONST_CLASS)
    )[0]

    if trg.value == succ_node.value:
        nrel_result = client.resolve_keynodes(
            ScIdtfResolveParams(idtf='nrel_result', type=sc_types.NODE_CONST_CLASS)
        )[0]
        res_templ = ScTemplate()
        res_templ.triple_with_relation(
            src,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR_STRUCT >> "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nrel_result
        )
        res_templ.triple(
            "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.LINK_VAR >> "_link_res"
        )
        gen_res = client.template_search(res_templ)[0]
        link_res = gen_res.get("_link_res")
        link_data = client.get_link_content(link_res)[0].data
        payload = link_data
    elif trg.value == unsucc_node.value or trg.value == node_err.value:
        raise AgentError

    callback_event.set()
    if not payload:
        return result.FAILURE
    return result.SUCCESS


class result(Enum):
    SUCCESS = 0
    FAILURE = 1


class Ostis:
    def __init__(self, url):
        self.ostis_url = url

    def call_auth_agent(self, action_name: str, username, password) -> str:
        if is_connected():
            username_lnk = create_link(client, username)
            password_lnk = create_link(client, password)
            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_2 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_2', type=sc_types.NODE_CONST_ROLE))[0]
            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                username_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_1
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                password_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_2
            )
            template.triple(
                action_agent,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "_main_node",
            )
            template.triple(
                initiated_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "_main_node",
            )

            event_params = ScEventSubscriptionParams(main_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, call_back)
            client.events_create(event_params)
            client.template_generate(template)

            global payload
            if callback_event.wait(timeout=10):
                while not payload:
                    continue
                return payload
            else:
                raise AgentError(524, "Timeout")
        else:
            raise ScServerError
    
    def call_reg_agent(
            self, 
            action_name: str,
            gender: Gender, 
            surname: str,
            name: str,
            fname: str,
            birthdate: str,
            reg_place: str,
            username: str,
            password: str
        ):
        if is_connected():
            username_lnk = create_link(client, username)
            password_lnk = create_link(client, password)
            gender_lnk = create_link(client, gender)
            surname_lnk = create_link(client, surname)
            name_lnk = create_link(client, name)
            fname_lnk = create_link(client, fname)
            birthdate_lnk = create_link(client, birthdate)
            reg_place_lnk = create_link(client, reg_place)

            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_2 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_2', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_3 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_3', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_4 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_4', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_5 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_5', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_6 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_6', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_7 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_7', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_8 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_8', type=sc_types.NODE_CONST_ROLE))[0]

            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                username_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_1
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                password_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_2
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                fname_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_3
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                name_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_4
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                surname_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_5
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                birthdate_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_6
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                reg_place_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_7
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                gender_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_8
            )
            template.triple(
                action_agent,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "_main_node",
            )
            template.triple(
                initiated_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "_main_node",
            )

            event_params = ScEventSubscriptionParams(main_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, call_back)
            client.events_create(event_params)
            client.template_generate(template)

            global payload
            if callback_event.wait(timeout=10):
                while not payload:
                    continue
                return payload
            else:
                raise AgentError(524, "Timeout")
        else:
            raise ScServerError


class OstisAuthAgent(AuthAgent):
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def auth_agent(self, username: str, password: str):
        global payload
        payload = None
        agent_response = self.ostis.call_auth_agent("action_authentication", username, password)
        if agent_response == "Valid":
            return {"status": AuthStatus.VALID}
        elif agent_response == "Invalid":
            return {
                "status": AuthStatus.INVALID,
                "message": "Invalid credentials",
            }
        raise AgentError
    
class OstisRegAgent(RegAgent):
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def reg_agent(
        self,
        gender: str, 
        surname: str,
        name: str,
        fname: str,
        birthdate: str,
        reg_place: str,
        username: str,
        password: str
        ):
        global payload
        payload = None
        agent_response = self.ostis.call_reg_agent("action_register", 
                                                   username, 
                                                   password,
                                                   gender,
                                                   surname,
                                                   name,
                                                   fname,
                                                   birthdate,
                                                   reg_place
                                                   )
        if agent_response == "User created":
            return {"status": RegStatus.CREATED}
        elif agent_response == "User exists":
            return {
                "status": RegStatus.EXISTS,
                "message": "User with that credentials already exists.",
                }
        raise AgentError
