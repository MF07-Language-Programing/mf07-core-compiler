from typing import Any, Optional, Dict, List, Tuple
from src.parser import Parser
import os
from src.lexer import Lexer
from src.interpreter import Interpreter
from src.lang_ast import (
    Program,
    VarDeclaration,
    FunctionDeclaration,
    ClassDeclaration,
    InterfaceDeclaration,
    Literal,
    ReturnStatement,
    Identifier,
    BinaryOp,
    UnaryOp,
    FunctionCall,
    JsonObject,
    JsonArray,
    NullLiteral,
    Assignment,
    ImportDeclaration,
)


class TypeErrorInfo:
    def __init__(self, message: str, node=None):
        self.message = message
        self.node = node

    def __str__(self):
        return self.message


class TypeChecker:
    """Very small, conservative TypeChecker.

    Currently supports:
    - var x: <type> = <literal>
    - intent return type check when intent returns a literal directly
    """

    def __init__(self):
        self.errors: List[TypeErrorInfo] = []
        # symbol table: stack of dicts
        self.scopes: List[Dict[str, Optional[str]]] = [{}]
        # intent signatures: name -> (param_types_list, return_type)
        self.func_signatures: Dict[str, Tuple[List[Optional[str]], Optional[str]]] = {}
        # interface signatures: name -> list of (method_name, param_types_list, return_type)
        self.interfaces: Dict[
            str, List[Tuple[str, List[Optional[str]], Optional[str]]]
        ] = {}

    def _normalize_type_name(self, name: Optional[str]) -> Optional[str]:
        if name is None:
            return None
        mapping = {
            "str": "string",
            "String": "string",
            "Int": "int",
            "Float": "float",
        }
        return mapping.get(name, name)

    def _split_generic_args(self, args: str) -> List[str]:
        result: List[str] = []
        current: List[str] = []
        depth = 0
        for ch in args:
            if ch == "<":
                depth += 1
                current.append(ch)
            elif ch == ">":
                depth -= 1
                current.append(ch)
            elif ch == "," and depth == 0:
                result.append("".join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            result.append("".join(current).strip())
        return result

    def _parse_generic(self, annotation: str) -> Tuple[str, List[str]]:
        annotation = annotation.strip()
        if "<" not in annotation:
            return annotation, []
        base, rest = annotation.split("<", 1)
        if rest.endswith(">"):
            rest = rest[:-1]
        args = self._split_generic_args(rest)
        return base.strip(), args

    def _type_matches(self, expected: Optional[str], actual: Optional[str]) -> bool:
        if expected is None or actual is None:
            return True

        expected = expected.strip()
        actual = actual.strip()

        if not expected or not actual:
            return True

        if expected.lower() == "any":
            return True

        base, args = self._parse_generic(expected)
        actual_base, actual_args = self._parse_generic(actual)

        if base == "Optional":
            if actual == "null":
                return True
            if not args:
                return True
            if actual_base == "Optional":
                if not actual_args:
                    return True
                limit = min(len(args), len(actual_args))
                for i in range(limit):
                    if self._type_matches(args[i], actual_args[i]):
                        return True
                return False
            for inner in args:
                if self._type_matches(inner, actual):
                    return True
            return False

        if base == "Union":
            for inner in args:
                if self._type_matches(inner, actual):
                    return True
            return False

        if actual_base == "Union":
            for inner in actual_args:
                if self._type_matches(expected, inner):
                    return True
            return False

        # match generics by base type when we do not have structural info yet
        if args:
            if self._normalize_type_name(base) != self._normalize_type_name(
                actual_base
            ):
                return False
            if not actual_args:
                return True
            # Compare inner arguments pairwise when both sides specify them
            limit = min(len(args), len(actual_args))
            for i in range(limit):
                if not self._type_matches(args[i], actual_args[i]):
                    return False
            return True

        # basic types with simple coercions
        exp_norm = self._normalize_type_name(expected)
        act_norm = self._normalize_type_name(actual)
        if exp_norm == act_norm:
            return True
        if exp_norm == "float" and act_norm == "int":
            return True
        return False

    def check(self, program: Program, base_dir: Optional[str] = None):
        self.errors.clear()
        # process imports first to gather external intent signatures
        interp = Interpreter()
        if base_dir:
            interp.current_file_dir = base_dir
        for stmt in program.statements:
            if isinstance(stmt, ImportDeclaration):
                try:
                    candidate = interp.resolve_import_path(stmt.name)
                    if candidate and os.path.exists(candidate):
                        with open(candidate, "r", encoding="utf-8") as f:
                            src = f.read()
                        lexer = Lexer(src)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        imported_prog = parser.parse()
                        # collect top-level functions from imported program
                        for s in imported_prog.statements:
                            if isinstance(s, FunctionDeclaration):
                                params = []
                                pmap = getattr(s, "param_types", None)
                                if pmap is not None and isinstance(pmap, dict):
                                    for p in s.params:
                                        params.append(pmap.get(p))
                                else:
                                    params = [None for _ in s.params]
                                self.func_signatures[s.name] = (params, s.return_type)
                except Exception:
                    # ignore import/parse errors for type checking
                    pass
        # First pass: collect top-level intent signatures
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                params: List[Optional[str]] = []
                stmt.param_types = getattr(stmt, "param_types", None)
                if getattr(stmt, "param_types", None) is not None:
                    for p in stmt.params:
                        pmap = stmt.param_types
                        if pmap is not None and isinstance(pmap, dict):
                            params.append(pmap.get(p))
                        else:
                            params.append(None)
                else:
                    params = [None for _ in stmt.params]
                self.func_signatures[stmt.name] = (params, stmt.return_type)
            # collect interfaces
            if isinstance(stmt, InterfaceDeclaration):
                methods = []
                for m in stmt.methods:
                    ptypes = []
                    pmap = getattr(m, "param_types", None)
                    if pmap is not None and isinstance(pmap, dict):
                        for p in m.params:
                            ptypes.append(pmap.get(p))
                    else:
                        ptypes = [None for _ in m.params]
                    methods.append((m.name, ptypes, m.return_type))
                self.interfaces[stmt.name] = methods

            if isinstance(stmt, ClassDeclaration):
                # collect class method signatures locally for checking implements later
                # store in func_signatures using class.method key
                for member in stmt.body:
                    if hasattr(member, "params"):
                        ptypes: List[Optional[str]] = []
                        pmap = getattr(member, "param_types", None)
                        if pmap is not None and isinstance(pmap, dict):
                            for p in getattr(member, "params", []):
                                ptypes.append(pmap.get(p))
                        else:
                            for _ in getattr(member, "params", []):
                                ptypes.append(None)
                        mname = getattr(member, "name", None)
                        if mname is not None:
                            self.func_signatures[f"{stmt.name}.{mname}"] = (
                                ptypes,
                                getattr(member, "return_type", None),
                            )

        # Second pass: check statements using signatures
        for stmt in program.statements:
            self._check_statement(stmt)

        # After checking statements, validate class implements
        for stmt in program.statements:
            if isinstance(stmt, ClassDeclaration) and stmt.implements:
                for iface in stmt.implements:
                    if iface not in self.interfaces:
                        self.errors.append(
                            TypeErrorInfo(
                                f"Class '{stmt.name}' implements unknown interface '{iface}'",
                                stmt,
                            )
                        )
                        continue
                    required = self.interfaces[iface]
                    # for each required method, look for class method
                    for mname, mptypes, mret in required:
                        key = f"{stmt.name}.{mname}"
                        sig = self.func_signatures.get(key)
                        if not sig:
                            self.errors.append(
                                TypeErrorInfo(
                                    f"Class '{stmt.name}' does not implement method '{mname}' required by interface '{iface}'",
                                    stmt,
                                )
                            )
                            continue
                        cls_ptypes, cls_ret = sig
                        # strict: check number of params
                        if len(cls_ptypes) != len(mptypes):
                            self.errors.append(
                                TypeErrorInfo(
                                    f"Method '{mname}' in class '{stmt.name}' has incompatible parameter count vs interface '{iface}'",
                                    stmt,
                                )
                            )
                            continue
                        # check param types when available
                        for i, expected in enumerate(mptypes):
                            if (
                                expected is not None
                                and cls_ptypes[i] is not None
                                and not self._type_matches(expected, cls_ptypes[i])
                            ):
                                self.errors.append(
                                    TypeErrorInfo(
                                        f"Parameter type mismatch in method '{mname}' of class '{stmt.name}' for param {i}: expected '{expected}' but found '{cls_ptypes[i]}'",
                                        stmt,
                                    )
                                )
                                break

    def _check_statement(self, node: Any):
        if isinstance(node, VarDeclaration):
            self._check_var_decl(node)
        elif isinstance(node, FunctionDeclaration):
            self._check_function_decl(node)
        elif isinstance(node, Assignment):
            # infer assignment value type
            val_type = self._infer_type(node.value)
            # If assignment target is an Identifier, set in scope
            target = getattr(node, "target", None)
            if isinstance(target, Identifier):
                for scope in reversed(self.scopes):
                    if target.name in scope:
                        scope[target.name] = val_type
                        break
            # If target is property access, we don't update scope here
        else:
            # Try to infer for expression nodes (FunctionCall at top-level etc.)
            try:
                self._infer_type(node)
            except Exception:
                pass
        # add more as needed

    def _check_var_decl(self, node: VarDeclaration):
        # push into current scope
        val_type = self._infer_type(node.value)
        stored_type = (
            node.type_annotation if node.type_annotation is not None else val_type
        )
        self.scopes[-1][node.name] = stored_type
        if node.type_annotation is None:
            return
        # If we can infer literal/expr type, check compatibility
        if val_type is not None and not self._type_matches(
            node.type_annotation, val_type
        ):
            self.errors.append(
                TypeErrorInfo(
                    f"Type mismatch for variable '{node.name}': annotated '{node.type_annotation}' but assigned expression of type '{val_type}'",
                    node,
                )
            )

    def _check_function_decl(self, node: FunctionDeclaration):
        # Create new scope for intent
        self.scopes.append({})
        # Bind parameter types
        if getattr(node, "param_types", None) is not None:
            pmap = node.param_types
            for p in node.params:
                if pmap is not None and isinstance(pmap, dict):
                    ptype = pmap.get(p)
                else:
                    ptype = None
                self.scopes[-1][p] = ptype

        # Walk intent body and check return statements
        for stmt in node.body:
            self._check_statement(stmt)
            if (
                isinstance(stmt, ReturnStatement)
                and stmt.value is not None
                and node.return_type is not None
            ):
                inferred = self._infer_type(stmt.value)
                if inferred is not None and not self._type_matches(
                    node.return_type, inferred
                ):
                    self.errors.append(
                        TypeErrorInfo(
                            f"Return type mismatch in intent '{node.name}': annotated '{node.return_type}' but returning expression of type '{inferred}'",
                            node,
                        )
                    )

        # pop intent scope
        self.scopes.pop()

    def _literal_type_name(self, v: Any) -> str:
        if isinstance(v, bool):
            return "bool"
        if isinstance(v, int):
            return "int"
        if isinstance(v, float):
            return "float"
        if isinstance(v, str):
            return "string"
        if v is None:
            return "null"
        return type(v).__name__

    def _infer_type(self, expr: Any) -> Optional[str]:
        # Return a simple string name for type or None if unknown
        if expr is None:
            return None
        if isinstance(expr, Literal):
            return self._literal_type_name(expr.value)
        if isinstance(expr, NullLiteral):
            return "null"
        if isinstance(expr, Identifier):
            # lookup in scopes
            for scope in reversed(self.scopes):
                if expr.name in scope:
                    # if value is a intent stored in scope, mark as 'intent'
                    val = scope[expr.name]
                    if callable(val) or (isinstance(val, str) and val == "intent"):
                        return "intent"
                    return val
            # maybe it's a intent name (value), leave None
            # It could refer to a top-level intent signature
            if expr.name in self.func_signatures:
                return "intent"
            return None
        if isinstance(expr, BinaryOp):
            left = self._infer_type(expr.left)
            right = self._infer_type(expr.right)
            # arithmetic
            if expr.operator in ["+", "-", "*", "/", "%"]:
                if left == "string" or right == "string":
                    # plus could be string concat, but for others prefer numeric
                    if expr.operator == "+" and (left == "string" or right == "string"):
                        return "string"
                    # numeric ops
                    if left in ("int", "float") and right in ("int", "float"):
                        if left == "float" or right == "float":
                            return "float"
                        return "int"
                if left in ("int", "float") and right in ("int", "float"):
                    if left == "float" or right == "float":
                        return "float"
                    return "int"
            # comparisons/logic
            if expr.operator in ["==", "!=", "<", ">", "<=", ">=", "and", "or"]:
                return "bool"
            return None
        if isinstance(expr, UnaryOp):
            return self._infer_type(expr.operand)
        if isinstance(expr, FunctionCall):
            # determine a usable key for looking up intent signatures;
            # FunctionCall implementations may expose the callee under different attribute names
            func_key = None
            name_attr = getattr(expr, "name", None)
            func_attr = getattr(expr, "func", None)
            callee_attr = getattr(expr, "callee", None)
            if name_attr is not None:
                func_key = name_attr
            elif func_attr is not None:
                func_key = func_attr
            elif callee_attr is not None:
                func_key = callee_attr

            # if the key is an Identifier node, extract its .name
            if isinstance(func_key, Identifier):
                func_key_str = func_key.name
            else:
                func_key_str = func_key if isinstance(func_key, str) else None

            sig = None
            if func_key_str is not None:
                sig = self.func_signatures.get(func_key_str)
            # check argument types against signature if available
            if sig:
                param_types, ret_type = sig
                for i, arg in enumerate(getattr(expr, "args", [])):
                    inferred = self._infer_type(arg)
                    expected = None
                    if i < len(param_types):
                        expected = param_types[i]
                    if (
                        expected is not None
                        and inferred is not None
                        and not self._type_matches(expected, inferred)
                    ):
                        name_for_msg = (
                            func_key_str if func_key_str is not None else "<intent>"
                        )
                        self.errors.append(
                            TypeErrorInfo(
                                f"Argument type mismatch in call to '{name_for_msg}': param {i} expected '{expected}' but got '{inferred}'",
                                expr,
                            )
                        )
                return ret_type
            return None
        if isinstance(expr, JsonObject):
            # try infer types of field values
            for k, v in expr.value.items():
                self._infer_type(v)
            return "object"
        if isinstance(expr, JsonArray):
            return "array"
        return None


def check_source(source: str):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    tc = TypeChecker()
    tc.check(program)
    print(f"Type checking completed with {len(tc.errors)} error(s).")
    return tc.errors


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python type_checker.py <file.mp>")
        sys.exit(1)
    fn = sys.argv[1]
    with open(fn, "r", encoding="utf-8") as f:
        src = f.read()
    errs = check_source(src)
    if not errs:
        print("No type errors")
    else:
        for e in errs:
            print("TypeError:", e)
