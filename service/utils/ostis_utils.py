import re

import sc_client.client as client
from sc_client.models import (
    ScAddr,
    ScConstruction,
    ScLinkContent,
    ScLinkContentType,
    ScTemplate,
)
from sc_client.constants import sc_types
from sc_kpm import ScKeynodes

from service.exceptions import ParseDataError

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

def set_birthdate_content(client, birthdate):
    pattern = r'(\d{2})\.(\d{2})\.(\d{4})'
    match = re.match(pattern, birthdate)
    if match:
        day, month, year = map(int, match.groups())
        print(day, month, year)
        _day_lnk = create_link(client, day)
        _month_lnk = create_link(client, month)
        _year_lnk = create_link(client, year)

        return _day_lnk, _month_lnk, _year_lnk
    else:
        raise ParseDataError(666, "Failed to parse args")