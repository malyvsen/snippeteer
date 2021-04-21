from typing import List, Set
from .nodes import node_types, string_children
from .descend import descend, descend_children


def extract_names(ast_node) -> Set[str]:
    name_extractors = {
        node_type: (
            lambda child_names: lambda node: [
                getattr(node, child_name) for child_name in child_names
            ]
            + descend_children(
                node, handlers=name_extractors, combiner=list.__add__, initial=[]
            )
        )(child_names)
        for node_type, child_names in string_children.items()
    }
    return set(descend(ast_node, handlers=name_extractors)) - {None}


def extract_line_numbers(ast_node) -> List[int]:
    extractors = {
        node_type: lambda node: ([node.lineno] if hasattr(node, "lineno") else [])
        + descend_children(node, handlers=extractors, combiner=list.__add__, initial=[])
        for node_type in node_types
    }
    return descend(ast_node, handlers=extractors)
