import ast


node_children = {
    ast.Constant: [],
    ast.Pass: [],
    type(None): [],
    ast.Name: [],
    ast.Module: ["body"],
    ast.Assign: ["targets", "value"],
    ast.AugAssign: ["target", "value"],
    ast.Expression: ["body"],
    ast.Expr: ["value"],
    ast.Import: ["names"],
    ast.ImportFrom: ["names"],
    ast.alias: [],
    ast.ClassDef: ["bases", "keywords", "decorator_list", "body"],
    ast.Attribute: ["value"],
    ast.FunctionDef: ["decorator_list", "args", "body"],
    ast.Lambda: ["args", "body"],
    ast.arg: [],
    ast.arguments: [
        "posonlyargs",
        "args",
        "vararg",
        "kwonlyargs",
        "kwarg",
        "defaults",
        "kw_defaults",
    ],
    ast.Return: ["value"],
    ast.Call: ["func", "args", "keywords"],
    ast.keyword: ["value"],
    ast.If: ["test", "body", "orelse"],
    ast.IfExp: ["test", "body", "orelse"],
    ast.While: ["test", "body", "orelse"],
    ast.For: ["target", "iter", "body", "orelse"],
    ast.Try: ["body", "handlers", "orelse", "finalbody"],
    ast.ExceptHandler: ["type", "body"],
    ast.Tuple: ["elts"],
    ast.List: ["elts"],
    ast.Set: ["elts"],
    ast.Dict: ["keys", "values"],
    ast.ListComp: ["elt", "generators"],
    ast.SetComp: ["elt", "generators"],
    ast.DictComp: ["key", "value", "generators"],
    ast.comprehension: ["target", "iter", "ifs"],
    ast.JoinedStr: ["values"],
    ast.FormattedValue: ["value"],
    ast.Subscript: ["value", "slice"],
    ast.Index: ["value"],
    ast.Slice: ["lower", "upper", "step"],
    ast.UnaryOp: ["operand"],
    ast.BinOp: ["left", "right"],
    ast.BoolOp: ["values"],
    ast.Compare: ["left", "comparators"],
}

string_children = {
    ast.Name: ["id"],
    ast.ImportFrom: ["module"],
    ast.alias: ["name", "asname"],
    ast.ClassDef: ["name"],
    ast.Attribute: ["attr"],
    ast.FunctionDef: ["name"],
    ast.arg: ["arg"],
    ast.ExceptHandler: ["name"],
}

node_types = set(node_children.keys()) | set(string_children.keys())
leaf_types = {
    node_type for node_type, children in node_children.items() if len(children) == 0
}
