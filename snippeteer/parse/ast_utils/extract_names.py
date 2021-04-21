from typing import Set
from .node_children import string_children
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
    return set(descend(ast_node, handlers=name_extractors))
