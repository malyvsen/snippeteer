import functools
import ast
from .nodes import node_children


def descend(ast_node, handlers, combiner=list.__add__, initial=[]):
    if isinstance(ast_node, str):
        raise TypeError("descend should only be used for parsed code, not strings")

    for node_type, handler in handlers.items():
        if isinstance(ast_node, node_type):
            return handler(ast_node)
    if isinstance(ast_node, list):
        return functools.reduce(
            combiner,
            [
                descend(
                    child_node,
                    handlers=handlers,
                    combiner=combiner,
                    initial=initial,
                )
                for child_node in ast_node
            ],
            initial,
        )
    return descend_children(
        ast_node, handlers=handlers, combiner=combiner, initial=initial
    )


def descend_children(ast_node, handlers, combiner, initial):
    for node_type, children in node_children.items():
        if isinstance(ast_node, node_type):
            return descend(
                [getattr(ast_node, child) for child in children],
                handlers=handlers,
                combiner=combiner,
                initial=initial,
            )

    raise NotImplementedError(f"Cannot parse {type(ast_node)}!")
