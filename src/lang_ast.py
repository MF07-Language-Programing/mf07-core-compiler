from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    docstring: Optional[str] = None


@dataclass
class VarDeclaration(ASTNode):
    name: str
    value: ASTNode
    type_annotation: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]
    is_async: bool = False
    param_types: Optional[Dict[str, Optional[str]]] = None
    param_defaults: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None
    return_type: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class LambdaExpression(ASTNode):
    params: List[str]
    body: List[ASTNode]
    param_types: Optional[Dict[str, Optional[str]]] = None
    param_defaults: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None
    return_type: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Assignment(ASTNode):
    # target can be a simple variable name (str) or an AST node like PropertyAccess
    target: Any
    value: ASTNode
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class ClassDeclaration(ASTNode):
    name: str
    body: List[ASTNode]  # methods and fields
    extends: Optional[str] = None
    implements: Optional[List[str]] = None
    is_abstract: bool = False
    generic_params: Optional[List[str]] = None  # For generic classes like List<T>
    docstring: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class MethodDeclaration(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]
    is_static: bool = False
    is_private: bool = False
    is_abstract: bool = False
    param_types: Optional[Dict[str, Optional[str]]] = None
    param_defaults: Optional[Dict[str, Any]] = None
    docstring: Optional[str] = None
    return_type: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class FieldDeclaration(ASTNode):
    name: str
    value: Optional[ASTNode] = None
    is_private: bool = False
    is_static: bool = False
    type_annotation: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class NewExpression(ASTNode):
    class_name: str
    args: List[ASTNode]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class ThisExpression(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class InterfaceDeclaration(ASTNode):
    name: str
    methods: List[MethodDeclaration]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class GenericTypeExpression(ASTNode):
    base_type: str
    type_parameters: List[str]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class JsonObject(ASTNode):
    value: Dict[str, Any]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class JsonArray(ASTNode):
    value: List[Any]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class NullLiteral(ASTNode):
    pass


@dataclass
class ImportDeclaration(ASTNode):
    name: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Await(ASTNode):
    expression: ASTNode
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode


@dataclass
class FunctionCall(ASTNode):
    # callee can be an identifier name (str) or an AST expression (e.g., PropertyAccess)
    callee: Any
    args: List[ASTNode]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class PropertyAccess(ASTNode):
    obj: ASTNode
    prop: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class IndexAccess(ASTNode):
    obj: ASTNode
    index: ASTNode
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class SuperExpression(ASTNode):
    # represents the bare 'super' expression
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_stmt: List[ASTNode]
    else_stmt: Optional[List[ASTNode]] = None


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ForStatement(ASTNode):
    """Traditional for loop: for (init; condition; update) { body }"""

    init: Optional[ASTNode]  # var i = 0
    condition: Optional[ASTNode]  # i < 10
    update: Optional[ASTNode]  # i++
    body: List[ASTNode]


@dataclass
class ForInStatement(ASTNode):
    """For-in loop: for (var item in collection) { body }"""

    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    type_annotation: Optional[str] = None


@dataclass
class ForOfStatement(ASTNode):
    """For-of loop: for (var item of collection) { body }"""

    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    type_annotation: Optional[str] = None


@dataclass
class CatchClause(ASTNode):
    exception_type: Optional[str]
    exception_var: Optional[str]
    body: List[ASTNode]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class TryStatement(ASTNode):
    try_block: List[ASTNode]
    catch_clauses: List[CatchClause]
    finally_block: Optional[List[ASTNode]] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class ThrowStatement(ASTNode):
    expression: Optional[ASTNode]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode] = None
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Literal(ASTNode):
    value: Union[int, float, str, bool]
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Identifier(ASTNode):
    name: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class TypeAnnotation(ASTNode):
    base: str
    args: Optional[List["TypeAnnotation"]] = None

    def __repr__(self):
        if not self.args:
            return self.base
        return f"{self.base}<" + ",".join(repr(a) for a in self.args) + ">"


@dataclass
class DatasetOperation(ASTNode):
    operation: str  # 'load', 'save', 'filter', etc.
    target: str
    params: Dict[str, Any]


@dataclass
class ModelOperation(ASTNode):
    operation: str  # 'create', 'train', 'predict', etc.
    model_name: str
    params: Dict[str, Any]


__all__ = [
    "ASTNode",
    "Program",
    "VarDeclaration",
    "FunctionDeclaration",
    "Assignment",
    "JsonObject",
    "JsonArray",
    "NullLiteral",
    "ImportDeclaration",
    "Await",
    "BinaryOp",
    "UnaryOp",
    "FunctionCall",
    "PropertyAccess",
    "IfStatement",
    "WhileStatement",
    "ForStatement",
    "ForInStatement",
    "ForOfStatement",
    "CatchClause",
    "TryStatement",
    "ThrowStatement",
    "ReturnStatement",
    "Literal",
    "Identifier",
    "DatasetOperation",
    "ModelOperation",
    "InterfaceDeclaration",
    "GenericTypeExpression",
]
