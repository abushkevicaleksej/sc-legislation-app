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
from sc_kpm.utils.common_utils import (
    generate_node, 
    generate_role_relation,
    generate_non_role_relation,
    generate_connector,
    check_connector,
    check_edge, 
    search_connector,
    generate_link
)

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

def get_system_idtf(node: ScAddr) -> str:
    template = ScTemplate()
    template.quintuple(
        node,
        sc_types.EDGE_D_COMMON_VAR,
        '_value',
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes['nrel_system_idtf']
        )
    template_result = client.template_search(template)
    value = ''
    if len(template_result):
        value = client.get_link_content(template_result[0].get('_value'))[0].data
    return value

def set_system_idtf(content: str) -> ScAddr:

    _link = generate_link(content)

    template = ScTemplate()

    template.quintuple(
        sc_types.NODE_VAR >> "_node",
        sc_types.EDGE_D_COMMON_VAR,
        _link >> "_link",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_system_identifier"]
    )
    
    result = client.generate_by_template(template)
    
    return result.get("_node")

def set_main_idtf(content: str) -> ScAddr:

    _link = generate_link(content)

    template = ScTemplate()

    template.quintuple(
        sc_types.NODE_VAR >> "_node",
        sc_types.EDGE_D_COMMON_VAR,
        _link >> "_link",
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        ScKeynodes["nrel_main_identifier"]
    )
    
    result = client.generate_by_template(template)
    
    return result.get("_node")

def set_gender_content(gender) -> ScAddr:
    if gender == "male":
        return ScKeynodes['concept_man']
    if gender == "female":
        return ScKeynodes['concept_woman']
    else:
        raise ParseDataError(666, "Failed to parse args")

def split_date_content(birthdate):
    pattern = r'(\d{2})\.(\d{2})\.(\d{4})'
    match = re.match(pattern, birthdate)
    if match:
        day, month, year = map(int, match.groups())
        return day, month, year
    else:
        raise ParseDataError(666, "Failed to parse args")
    
def get_term_titles() -> list[str]:
    template =  ScTemplate()
    term_list = []
    template.triple(
        ScKeynodes["belarus_legal_article"],
        sc_types.EDGE_ACCESS_VAR_POS_PERM,
        sc_types.NODE_VAR >> "_term_node"
    )

    template_result = client.template_search(template)
    print(f'total terms {len(template_result)}')
    for _ in template_result:
        node = _.get("_term_node")
        term_list.append(get_main_idtf(node))
    return term_list


