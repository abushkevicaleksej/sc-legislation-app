<<<<<<< HEAD
=======
from enum import Enum
from threading import Event
import re

>>>>>>> feat/directory
import sc_client.client as client
from sc_client.client import generate_by_template
from ..exceptions import ScServerError
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
from sc_kpm.utils.common_utils import (
    generate_node, 
    generate_role_relation, 
    get_link_content_data, 
<<<<<<< HEAD
    get_element_system_identifier
    )
from sc_kpm import ScKeynodes


from threading import Event
from enum import Enum
import re
=======
    get_element_system_identifier, 
    )
from sc_kpm import ScKeynodes
>>>>>>> feat/directory

from service.agents.abstract.auth_agent import AuthAgent, AuthStatus
from service.agents.abstract.reg_agent import RegAgent, RegStatus
from service.agents.abstract.user_request_agent import RequestAgent, RequestStatus
from service.agents.abstract.directory_agent import DirectoryAgent, DirectoryStatus
from service.exceptions import AgentError, ParseDataError
from config import Config

payload = None
callback_event = Event()

gender_dict = {
    "male": "мужчина",
    "female": "женщина"
}

class result(Enum):
    SUCCESS = 0
    FAILURE = 1

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

def get_main_idtf(node: ScAddr) -> str:
    template = ScTemplate()
    template.quintuple(
        node,
        sc_types.EDGE_D_COMMON_VAR,
        '_value',
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes['nrel_main_idtf']
        )
    template_result = client.template_search(template)
    value = ''
    if len(template_result):
        value = client.get_link_content(template_result[0].get('_value'))[0].data
    return value

def set_gender_content(gender) -> ScAddr:
    if gender == "male":
        return ScKeynodes['concept_man']
    if gender == "female":
        return ScKeynodes['concept_woman']
    else:
        raise ParseDataError(666, "Failed to parse args")

def set_birthdate_content(client, birthdate) -> ScAddr:
    pattern = r'(\d{2})\.(\d{2})\.(\d{4})'
    match = re.match(pattern, birthdate)
    day_node = generate_node(sc_types.NODE_CONST)
    month_node = generate_node(sc_types.NODE_CONST)
    year_node = generate_node(sc_types.NODE_CONST)
    if match:
        day, month, year = map(int, match.groups())
        day_lnk = create_link(client, day)
        month_lnk = create_link(client, month)
        year_lnk = create_link(client, year)

        day_template = ScTemplate()
        day_template.quintuple(
            day_node,
            sc_types.EDGE_D_COMMON_VAR,
            day_lnk,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes['nrel_main_idtf']
        )
        day_res = generate_by_template(day_template)

        month_template = ScTemplate()
        month_template.quintuple(
            month_node,
            sc_types.EDGE_D_COMMON_VAR,
            month_lnk,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes['nrel_main_idtf']
        )
        month_res = generate_by_template(month_template)

        year_template = ScTemplate()
        year_template.quintuple(
            year_node,
            sc_types.EDGE_D_COMMON_VAR,
            year_lnk,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes['nrel_main_idtf']
        )
        year_res = generate_by_template(year_template)

        return day_res[0], month_res[0], year_res[0]
    else:
        raise ParseDataError(666, "Failed to parse args") 


def call_back(src: ScAddr, connector: ScAddr, trg: ScAddr) -> Enum:
    global payload
    callback_event.clear()  # Clear the event at the start of callback
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
            succ_node,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            src
        )
        gen_res = client.template_search(res_templ)[0]
        payload = {"message": result.SUCCESS}
    elif trg.value == unsucc_node.value or trg.value == node_err.value:
        payload = {"message": result.FAILURE}

    callback_event.set()
    if not payload:
        return result.FAILURE
    return result.SUCCESS

def call_back_request(src: ScAddr, connector: ScAddr, trg: ScAddr) -> Enum:
    global payload
    callback_event.clear()
    content_list = []
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
        gen_res = client.template_search(res_templ)
        for _ in gen_res:
            link_res = _.get("_link_res")
            link_data = client.get_link_content(link_res)[0].data
            content_list.append(link_data)
        payload = {"message": content_list}
    elif trg.value == unsucc_node.value or trg.value == node_err.value:
        payload = {"message": "Nothing"}

    callback_event.set()
    if not payload:
        return result.FAILURE
    return result.SUCCESS

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
            gender: str, 
            surname: str,
            name: str,
            fname: str,
            birthdate,
            reg_place: str,
            username: str,
            password: str
        ):
        if is_connected():
            username_lnk = create_link(client, username)
            password_lnk = create_link(client, password)
            gender_node = set_gender_content(gender)
            surname_lnk = create_link(client, surname)
            name_lnk = create_link(client, name)
            fname_lnk = create_link(client, fname)
            day_node, month_node, year_node = set_birthdate_content(client, birthdate)
            reg_place_lnk = create_link(client, reg_place)

            args = [
                get_link_content_data(username_lnk),
                get_link_content_data(password_lnk),
                get_element_system_identifier(gender_node),
                get_link_content_data(surname_lnk),
                get_link_content_data(name_lnk),
                get_link_content_data(fname_lnk),
                get_link_content_data(reg_place_lnk),
                get_main_idtf(day_node),
                get_main_idtf(month_node),
                get_main_idtf(year_node),
            ]
            for _ in args:
                print(_)

            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_2 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_2', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_3 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_3', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_4 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_4', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_5 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_5', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_6 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_6', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_7 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_7', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_8 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_8', type=sc_types.NODE_CONST_ROLE))[0]

            rrel_user_day = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_user_day', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_user_month = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_user_month', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_user_year = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_user_year', type=sc_types.NODE_CONST_ROLE))[0]

            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            birthdate_con = generate_node(sc_types.NODE_CONST_TUPLE)
            generate_role_relation(birthdate_con, day_node, rrel_user_day)
            generate_role_relation(birthdate_con, month_node, rrel_user_month)
            generate_role_relation(birthdate_con, year_node, rrel_user_year)

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
                birthdate_con,
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
                gender_node,
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
        
    def call_user_request_agent(self,
                                action_name: str,
                                content: str
                                ):
        if is_connected():
            request_lnk = create_link(client, content)

            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
    
            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                request_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_1
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

            event_params = ScEventSubscriptionParams(main_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, call_back_request)
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
        
    def call_directory_agent(self, action_name, content: str) -> str:
        if is_connected():
            part_node = ScKeynodes["CONCEPT_FULL_SEARCH"]
            area_node = ScKeynodes["FULL_SEARCH"]
            content_lnk = create_link(client, content)

            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_2 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_2', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_3 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_3', type=sc_types.NODE_CONST_ROLE))[0]

            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                part_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_1
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                area_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_2
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                content_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_3
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

            event_params = ScEventSubscriptionParams(main_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, call_back_request)
            client.events_create(event_params)
            client.template_generate(template)

            global payload
            if callback_event.wait(timeout=10):
                print("here")
                while not payload:
                    continue
                print(payload['message'])
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
        if agent_response['message'] == result.SUCCESS:
            return {"status": AuthStatus.VALID}
        elif agent_response['message'] == result.FAILURE:
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
        birthdate,
        reg_place: str,
        username: str,
        password: str
        ):
        global payload
        payload = None
        agent_response = self.ostis.call_reg_agent(
            action_name="action_register", 
            username=username, 
            password=password,
            gender=gender,
            surname=surname,
            name=name,
            fname=fname,
            birthdate=birthdate,
            reg_place=reg_place
            )
        if agent_response['message'] == result.SUCCESS:
            return {"status": RegStatus.CREATED}
        elif agent_response['message'] == result.FAILURE:
            return {
                "status": RegStatus.EXISTS,
                "message": "User with that credentials already exists.",
                }
        raise AgentError

class OstisUserRequestAgent(RequestAgent):
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def request_agent(self, content: str):
        global payload
        payload = None
        agent_response = self.ostis.call_user_request_agent(
            action_name="action_user_request", 
            content=content
            )
        if agent_response is not None:
            return {"status": RequestStatus.VALID,
                    "message": agent_response["message"]}
        elif agent_response is None:
            return {
                "status": RequestStatus.INVALID,
                "message": "Invalid credentials",
            }
        raise AgentError
    
class OstisDirectoryAgent(DirectoryAgent):
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def directory_agent(self, content: str):
        global payload
        payload = None
        agent_response = self.ostis.call_directory_agent(
            action_name="action_search",
            content=content
            )
        if agent_response is not None:
            return {"status": DirectoryStatus.VALID,
                    "message": agent_response["message"]}
        elif agent_response is None:
            return {
                "status": DirectoryStatus.INVALID,
                "message": "Invalid credentials",
            }
        raise AgentError