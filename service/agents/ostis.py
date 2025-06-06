from enum import Enum
from threading import Event

import sc_client.client as client
from ..exceptions import ScServerError
from sc_client.client import is_connected, search_links_by_contents
from sc_client.models import (
    ScAddr,
    ScEventSubscriptionParams,
    ScIdtfResolveParams,
    ScTemplate,
)
from sc_client.constants.common import ScEventType
from sc_client.constants import sc_types
from sc_kpm import ScKeynodes

from service.models import RequestResponse, DirectoryResponse, EventResponse, UserEvent
from service.models import get_user_by_login
from service.agents.abstract.auth_agent import AuthAgent, AuthStatus
from service.agents.abstract.reg_agent import RegAgent, RegStatus
from service.agents.abstract.user_request_agent import RequestAgent, RequestStatus
from service.agents.abstract.directory_agent import DirectoryAgent, DirectoryStatus
from service.agents.abstract.event_agents import (
    AddEventAgent,
    AddEventStatus,
    DeleteEventAgent,
    DeleteEventStatus,
    ShowEventAgent,
    ShowEventStatus
)
from service.exceptions import AgentError
from service.utils.ostis_utils import(
    create_link,
    get_node,
    set_gender_content,
    split_date_content,
    get_main_idtf,
    set_system_idtf
)
from config import Config

payload = None
callback_event = Event()

gender_dict = {
    "male": "мужчина",
    "female": "женщина"
}

class result(Enum):
    """
    Перечисление для представления результата выполнения агента
    """
    SUCCESS = 0
    FAILURE = 1 

def call_back(src: ScAddr, connector: ScAddr, trg: ScAddr) -> Enum:
    """
    Метод для реализации дефолтной колбэк-функции выполнения агента
    :param src: Адрес ноды для вызова агента
    :param connector: Коннектор
    :param trg: Адрес ноды, которая показывает результат выполнения агента
    :return: Результат выполнения агента
    """
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
        print(trg.value)
        print(succ_node.value)
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
    """
    Метод для реализации колбэк-функции выполнения агента юридических запросов
    :param src: Адрес ноды для вызова агента
    :param connector: Коннектор
    :param trg: Адрес ноды, которая показывает результат выполнения агента
    :return: Результат выполнения агента
    """
    global payload
    callback_event.clear()

    term: str
    content: str
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
        body_template = ScTemplate()
        related_article_template = ScTemplate()
        related_concept_template = ScTemplate()

        body_template.triple_with_relation(
            src,
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.LINK_VAR >> "_src_link",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            ScKeynodes["rrel_1"]
        )
        body_template.triple_with_relation(
            src,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR_STRUCT >> "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nrel_result
        )
        body_template.triple(
            "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.LINK_VAR >> "_link_body"
        )

        related_article_template.triple_with_relation(
            src,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR_STRUCT >> "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nrel_result
        )
        related_article_template.triple(
            "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR >> "_related_article"
        )
        related_article_template.triple(
            ScKeynodes["belarus_legal_article"],
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            "_related_article",
        )

        related_concept_template.triple_with_relation(
            src,
            sc_types.EDGE_D_COMMON_VAR,
            sc_types.NODE_VAR_STRUCT >> "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            nrel_result
        )
        related_concept_template.triple(
            "_res_struct",
            sc_types.EDGE_ACCESS_VAR_POS_PERM,
            sc_types.NODE_VAR_CLASS >> "_related_term"
        )

        body_result = client.template_search(body_template)
        for _body in body_result:
            src_link = _body.get("_src_link")
            link = _body.get("_link_body")
            term = client.get_link_content(src_link)[0].data
            content = client.get_link_content(link)[0].data

            related_articles = []
            related_concepts = []

            article_result = client.template_search(related_article_template)
            for _article in article_result:
                article_node = _article.get("_related_article")
                if article_node:
                    article_data = get_main_idtf(article_node)
                    if article_data:
                        related_articles.append(article_data)

            concept_result = client.template_search(related_concept_template)
            for _concept in concept_result:
                concept_node = _concept.get("_related_term")
                if concept_node:
                    concept_data = get_main_idtf(concept_node)
                    if concept_data:
                        related_concepts.append(concept_data)

            response = RequestResponse(
                term=term,
                content=content,
                related_articles=related_articles,
                related_concepts=related_concepts
            )

            content_list.append(response)

        payload = {"message": content_list}
    elif trg.value == unsucc_node.value or trg.value == node_err.value:
        payload = {"message": "Nothing"}

    callback_event.set()
    if not payload:
        return result.FAILURE
    return result.SUCCESS

def call_back_directory(src: ScAddr, connector: ScAddr, trg: ScAddr) -> Enum:
    """
    Метод для реализации колбэк-функции выполнения агента поиска
    :param src: Адрес ноды для вызова агента
    :param connector: Коннектор
    :param trg: Адрес ноды, которая показывает результат выполнения агента
    :return: Результат выполнения агента
    """
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
            sc_types.NODE_VAR >> "_article_node"
        )
        gen_res = client.template_search(res_templ)
        for _ in gen_res:
            node_res = _.get("_article_node")
            _templ = ScTemplate()
            _templ.triple_with_relation(
                node_res,
                sc_types.EDGE_D_COMMON_VAR,
                sc_types.LINK_VAR >> "_title_link",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes["nrel_main_idtf"],
            )
            _templ.triple(
                ScKeynodes["lang_ru"],
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "_title_link"
            )
            _templ.triple_with_relation(
                sc_types.NODE_VAR >> "_1",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                node_res,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes["rrel_key_sc_element"]
            )
            _templ.triple_with_relation(
                sc_types.NODE_VAR >> "_2",
                sc_types.EDGE_D_COMMON_VAR,
                "_1",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes["nrel_sc_text_translation"]
            )
            _templ.triple_with_relation(
                "_2",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_types.LINK_VAR >> "_content_link",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                ScKeynodes["rrel_example"]
            )
            _templ.triple(
                ScKeynodes["lang_ru"],
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                "_content_link"
            )
            _res = client.template_search(_templ)[0]
            _title_link = _res.get("_title_link")
            _content_link = _res.get("_content_link")
            title_data = client.get_link_content(_title_link)[0].data
            content_data = client.get_link_content(_content_link)[0].data
            content_list.append(
                DirectoryResponse(
                    title=title_data,
                    content=content_data)
                )
        payload = {"message": content_list}
    elif trg.value == unsucc_node.value or trg.value == node_err.value:
        payload = {"message": "Nothing"}

    callback_event.set()
    if not payload:
        return result.FAILURE
    return result.SUCCESS

def call_back_get_events(src: ScAddr, connector: ScAddr, trg: ScAddr) -> Enum:
    """
    Метод для реализации колбэк-функции выполнения агента получения событий
    :param src: Адрес ноды для вызова агента
    :param connector: Коннектор
    :param trg: Адрес ноды, которая показывает результат выполнения агента
    :return: Результат выполнения агента
    """
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

class Ostis:
    """
    Класс для представления OSTIS-системы
    """
    def __init__(self, url):
        self.ostis_url = url

    def call_auth_agent(self, action_name: str, username, password) -> str:
        """
        Метод для вызова агента аутентификации
        :param action_name: Идентификатор action-ноды агента
        :param username: Логин пользователя для аутентификации
        :param password: Пароль пользователя для аутентификации
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
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
        """
        Метод для вызова агента регистрации
        :param action_name: Идентификатор action-ноды агента
        :param gender: Пол пользователя для регистрации
        :param surname: Фамилия пользователя для регистрации
        :param name: Имя пользователя для регистрации
        :param fname: Отчество пользователя для регистрации
        :param birthdate: Дата рождения пользователя для регистрации
        :param reg_place: Место регистрации пользователя для регистрации
        :param username: Логин пользователя для регистрации
        :param password: Пароль пользователя для регистрации
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
        if is_connected():
            day, month, year = split_date_content(birthdate)
            username_lnk = create_link(client, username)
            password_lnk = create_link(client, password)
            gender_node = set_gender_content(gender)
            surname_lnk = create_link(client, surname)
            name_lnk = create_link(client, name)
            fname_lnk = create_link(client, fname)
            day_node = set_system_idtf(day)
            month_node = set_system_idtf(month)
            year_node = set_system_idtf(year)
            reg_place_lnk = create_link(client, reg_place)

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
                surname_lnk,
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
                fname_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_5
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_types.NODE_VAR_TUPLE >> "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_6
            )
            template.triple_with_relation(
                "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                day_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_user_day
            )
            template.triple_with_relation(
                "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                month_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_user_month
            )
            template.triple_with_relation(
                "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                year_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_user_year
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
        """
        Метод для вызова агента юридических запросов
        :param action_name: Идентификатор action-ноды агента
        :param content: Контент, по которому происходит поиск в БЗ
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
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
        
    def call_directory_agent(self, action_name: str, content: str) -> str:
        """
        Метод для вызова агента поиска
        :param action_name: Идентификатор action-ноды агента
        :param content: Контент, по которому происходит поиск в БЗ
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
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

            event_params = ScEventSubscriptionParams(main_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, call_back_directory)
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

    def call_add_event_agent(self, action_name: str, user_name, event_name: str, event_date, event_description: str) -> str:
        """
        Метод для вызова агента добавления события
        :param action_name: Идентификатор action-ноды агента
        :param user_name: Логин пользователя
        :param event_name: Название события
        :param event_date: Дата события
        :param event_description: Описание события
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
        if is_connected():
            event_name_lnk = create_link(client, event_name)
            day, month, year = split_date_content(event_date)
            day_node = set_system_idtf(day)
            month_node = set_system_idtf(month)
            year_node = set_system_idtf(year)
            event_description_lnk = create_link(client, event_description)

            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_2 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_2', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_3 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_3', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_4 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_4', type=sc_types.NODE_CONST_ROLE))[0]

            rrel_event_day = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_event_day', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_event_month = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_event_month', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_event_year = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_event_year', type=sc_types.NODE_CONST_ROLE))[0]

            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            user = get_user_by_login(user_name)
            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                user,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_1
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                event_name_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_2
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                sc_types.NODE_VAR_TUPLE >> "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_3
            )
            template.triple_with_relation(
                "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                day_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_event_day
            )
            template.triple_with_relation(
                "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                month_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_event_month
            )
            template.triple_with_relation(
                "_tuple",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                year_node,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_event_year
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                event_description_lnk,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_4
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

    def call_delete_event_agent(self, action_name: str, username: str, event_name: str) -> str:
        """
        Метод для вызова агента удаления события
        :param action_name: Идентификатор action-ноды агента
        :param event_name: Название события
        :param username: Логин пользователя
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
        if is_connected():

            event_name_lnk = create_link(client, event_name)
            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]
            rrel_2 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_2', type=sc_types.NODE_CONST_ROLE))[0]

            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            user = get_user_by_login(username)
            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                user,
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                rrel_1
            )
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                event_name_lnk,
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

    def call_show_event_agent(self, action_name: str, username: str) -> str:
        """
        Метод для вызова агента просмотра события
        :param action_name: Идентификатор action-ноды агента
        :param username: Логин пользователя
        :return: Ответ сервера
        :raises AgentError: Возникает при истечении времени ожидания
        :raises ScServerError: Возникает при отсутствии запущенного sc-сервера
        """
        if is_connected():

            rrel_1 = client.resolve_keynodes(ScIdtfResolveParams(idtf='rrel_1', type=sc_types.NODE_CONST_ROLE))[0]

            initiated_node = client.resolve_keynodes(ScIdtfResolveParams(idtf='action_initiated', type=sc_types.NODE_CONST_CLASS))[0]
            action_agent = client.resolve_keynodes(ScIdtfResolveParams(idtf=action_name, type=sc_types.NODE_CONST_CLASS))[0]
            main_node = get_node(client)

            user = get_user_by_login(username)
            template = ScTemplate()
            template.triple_with_relation(
                main_node >> "_main_node",
                sc_types.EDGE_ACCESS_VAR_POS_PERM,
                user,
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

            event_params = ScEventSubscriptionParams(main_node, ScEventType.AFTER_GENERATE_INCOMING_ARC, call_back_get_events)
            client.events_create(event_params)
            client.template_generate(template)
            print("here")
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
    """
    Класс для представления агента аутентификации
    """
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def auth_agent(self, username: str, password: str):
        """
        Метод для запуска агента аутентификации
        :param username: Логин пользователя для аутентификации
        :param password: Пароль пользователя для аутентификации
        :return: Словарь со статусом результата выполнения агента аутентификации
        """
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
    """
    Класс для представления агента регистрации
    """
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
        """
        Метод для запуска агента регистрации
        :param gender: Пол пользователя для регистрации
        :param surname: Фамилия пользователя для регистрации
        :param name: Имя пользователя для регистрации
        :param fname: Отчество пользователя для регистрации
        :param birthdate: Дата рождения пользователя для регистрации
        :param reg_place: Место регистрации пользователя для регистрации
        :param username: Логин пользователя для регистрации
        :param password: Пароль пользователя для регистрации
        :return: Словарь со статусом результата выполнения агента регистрации
        """
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
    """
    Класс для представления агента юридических запросов
    """
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def request_agent(self, content: str):
        """
        Метод для запуска агента юридических запросов
        :param content: Контент, по которому происходит поиск в БЗ
        :return: Словарь со статусом результата выполнения агента юридических запросов
        """
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
    """
    Класс для представления агента поиска
    """
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def directory_agent(self, content: str):
        """
        Метод для запуска агента поиска
        :param content: Контент, по которому происходит поиск в БЗ
        :return: Словарь со статусом результата выполнения агента поиска
        """
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

class OstisAddEventAgent(AddEventAgent):
    """
    Класс для представления агента добавления события
    """
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def add_event_agent(self, 
                        user_name: ScAddr,
                        event_name: str, 
                        event_date, 
                        event_description: str
                        ):
        """
        Метод для запуска агента добавления события
        :param user_name: Логин пользователя
        :param event_name: Название события
        :param event_date: Дата события
        :param event_description: Описание события
        :return:
        """
        global payload
        payload = None
        agent_response = self.ostis.call_add_event_agent(
            action_name="action_add_event",
            user_name=user_name,
            event_name=event_name,
            event_date=event_date,
            event_description=event_description
            )
        if agent_response is not None:
            return {"status": AddEventStatus.VALID,
                    "message": agent_response["message"]}
        elif agent_response is None:
            return {
                "status": AddEventStatus.INVALID,
                "message": "Invalid credentials",
            }
        raise AgentError

class OstisDeleteEventAgent(DeleteEventAgent):
    """
    Класс для представления агента удаления события
    """
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def delete_event_agent(self,
                        username: str,
                        event_name: str,
                        ):
        """
        Метод для запуска агента удаления события
        :param event_name: Название события
        :param username: Логин пользователя
        :return:
        """
        global payload
        payload = None
        agent_response = self.ostis.call_delete_event_agent(
            action_name="action_del_event",
            username=username,
            event_name=event_name,
        )
        if agent_response is not None:
            return {"status": DeleteEventStatus.VALID,
                    "message": agent_response["message"]}
        elif agent_response is None:
            return {
                "status": DeleteEventStatus.INVALID,
                "message": "Invalid credentials",
            }
        raise AgentError

class OstisShowEventAgent(ShowEventAgent):
    """
    Класс для представления агента просмотра события
    """
    def __init__(self):
        self.ostis = Ostis(Config.OSTIS_URL)

    def show_event_agent(self,
                        username
                        ):
        """
        Метод для запуска агента просмотра события
        :param username: Логин пользователя
        :return:
        """
        global payload
        payload = None
        agent_response = self.ostis.call_show_event_agent(
            action_name="action_user_events",
            username=username
            )
        if agent_response is not None:
            return {"status": ShowEventStatus.VALID,
                    "message": agent_response["message"]}
        elif agent_response is None:
            return {
                "status": ShowEventStatus.INVALID,
                "message": "Invalid credentials",
            }