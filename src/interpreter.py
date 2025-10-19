"""Interpreter and runtime moved into src package.

This file provides the Interpreter, Environment, intent/task runtime
and related helpers. It is a self-contained implementation that imports
the Parser and Lexer from the same package for handling imports.
"""

import re
import json
import traceback
import time
import os
import threading
import difflib
from typing import Any, Dict, List, Optional

from src.mf_native import connections as mf_connections_native
from src.mf_native import datetime as mf_datetime_native
from src.mf_native import sys_hash as mf_hash_native
from src.mf_native import fs as mf_fs_native, path as mf_path_native
from src.mf_native.http_client import HttpClient

from .logger import LogLevel, get_logger, debug, info, warn, error, trace
from .lexer import Lexer
from .parser import Parser
from .lang_ast import (
    Program,
    VarDeclaration,
    FunctionDeclaration,
    LambdaExpression,
    Assignment,
    JsonObject,
    JsonArray,
    NullLiteral,
    ImportDeclaration,
    Await,
    BinaryOp,
    UnaryOp,
    FunctionCall,
    PropertyAccess,
    IfStatement,
    WhileStatement,
    ForStatement,
    ForInStatement,
    ForOfStatement,
    ReturnStatement,
    Literal,
    Identifier,
    DatasetOperation,
    ModelOperation,
    ClassDeclaration,
    MethodDeclaration,
    FieldDeclaration,
    NewExpression,
    ThisExpression,
    InterfaceDeclaration,
    IndexAccess,
    SuperExpression,
    CatchClause,
    TryStatement,
    ThrowStatement,
)

# Helper to allow native Python-backed methods to access the current Interpreter
_CURRENT_INTERPRETER: Optional["Interpreter"] = None


def _get_current_interpreter() -> Optional["Interpreter"]:
    return _CURRENT_INTERPRETER


class RuntimeTypeError(Exception):
    pass


def _literal_type_name(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "string"
    # Handle InstanceObject - return the class name
    if hasattr(v, "class_obj") and hasattr(v.class_obj, "name"):
        return v.class_obj.name
    return type(v).__name__


def _split_generic_args(arg_str: str) -> List[str]:
    args: List[str] = []
    current: List[str] = []
    depth = 0
    for ch in arg_str:
        if ch == "<":
            depth += 1
            current.append(ch)
        elif ch == ">":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        args.append("".join(current).strip())
    return args


def _parse_generic_type(annotation: str) -> tuple[str, List[str]]:
    annotation = annotation.strip()
    if "<" not in annotation:
        return annotation, []
    base, rest = annotation.split("<", 1)
    # remove trailing '>' (assume balanced)
    if rest.endswith(">"):
        rest = rest[:-1]
    args = _split_generic_args(rest)
    return base.strip(), args


def _matches_type(value: Any, annotated: Optional[str]) -> bool:
    if annotated is None:
        return True

    annotated = annotated.strip()
    if not annotated:
        return True

    # 'any' accepts any value type
    if annotated.lower() == "any":
        return True

    base_type, generic_args = _parse_generic_type(annotated)

    # Handle Optional[...] annotations (accepts null or inner type)
    if base_type == "Optional":
        if value is None:
            return True
        if not generic_args:
            return True
        # If multiple types are specified (Optional<A, B>), succeed if any matches
        for inner in generic_args:
            if _matches_type(value, inner):
                return True
        return False

    if base_type == "Union":
        for inner in generic_args:
            if _matches_type(value, inner):
                return True
        return False

    t = _literal_type_name(value)

    # Handle generic types (e.g., "List<int>") by matching the base type
    if generic_args:
        return t == base_type

    # accept int <- float only if float has integer value? keep strict: float != int
    if annotated == "float" and t == "int":
        return True

    return t == annotated


def _ast_to_source(node: Any) -> str:
    # Render AST node to a readable source-like string (best-effort)
    try:
        from src.lang_ast import (
            VarDeclaration,
            FunctionDeclaration,
            Assignment,
            JsonObject,
            JsonArray,
            Literal,
            Identifier,
            FunctionCall,
            PropertyAccess,
            ReturnStatement,
            Await,
        )
    except Exception:
        # fallback minimal
        return str(node)

    def render(n: Any, depth: int = 0) -> str:
        if depth > 5:
            return "..."
        if n is None:
            return "null"
        if isinstance(n, Literal):
            return repr(n.value)
        if isinstance(n, Identifier):
            return n.name
        if isinstance(n, FunctionCall):
            args = ", ".join(render(a, depth + 1) for a in n.args)
            # FunctionCall may store the callee as an Identifier or a more complex expression;
            # prefer an explicit .name if present, otherwise render the callee expression.
            name_attr = getattr(n, "name", None)
            if name_attr:
                callee_repr = name_attr
            else:
                try:
                    callee_repr = render(getattr(n, "callee", "<call>"), depth + 1)
                except Exception:
                    callee_repr = str(getattr(n, "callee", "<call>"))
            return f"{callee_repr}({args})"
        if isinstance(n, PropertyAccess):
            return f"{render(n.obj, depth+1)}.{n.prop}"
        if isinstance(n, Assignment):
            # Assignment uses 'target' for the left-hand side (Identifier, PropertyAccess, etc.)
            return f"{render(n.target, depth+1)} = {render(n.value, depth+1)}"
        if isinstance(n, VarDeclaration):
            ta = f": {n.type_annotation}" if getattr(n, "type_annotation", None) else ""
            return f"var {n.name}{ta} = {render(n.value, depth+1)}"
        if isinstance(n, FunctionDeclaration):
            params = []
            pmap = getattr(n, "param_types", None) or {}
            for p in n.params:
                pt = pmap.get(p) if isinstance(pmap, dict) else None
                params.append(f"{p}: {pt}" if pt else p)
            ret = f": {n.return_type}" if getattr(n, "return_type", None) else ""
            return f"intent {n.name}({', '.join(params)}){ret} {{...}}"
        if isinstance(n, JsonObject):
            items = []
            for k, v in n.value.items():
                items.append(f"{k}: {render(v, depth+1)}")
            return "{" + ", ".join(items) + "}"
        if isinstance(n, JsonArray):
            elems = ", ".join(render(e, depth + 1) for e in n.value)
            return "[" + elems + "]"
        if isinstance(n, ReturnStatement):
            return (
                f"return {render(n.value, depth+1)}"
                if n.value is not None
                else "return"
            )
        if isinstance(n, Await):
            return f"await {render(n.expression, depth+1)}"
        # Fallback to repr of attributes
        try:
            if hasattr(n, "__dict__"):
                attrs = {
                    k: v for k, v in n.__dict__.items() if k not in ("line", "column")
                }
                return f"{n.__class__.__name__}({attrs})"
        except Exception:
            pass
        return str(n)

    try:
        return render(node)
    except Exception:
        return str(node)


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        # store declared types for variables in this scope
        self.types: Dict[str, Optional[str]] = {}

    def define(self, name: str, value: Any, type_annotation: Optional[str] = None):
        # If a type annotation is provided, enforce it now
        if type_annotation is not None:
            if not _matches_type(value, type_annotation):
                raise RuntimeTypeError(
                    f"Type mismatch on declaration of '{name}': annotated '{type_annotation}' but assigned value of type '{_literal_type_name(value)}'"
                )
        self.variables[name] = value
        # record type annotation (could be None)
        self.types[name] = type_annotation

    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variável '{name}' não definida")

    def set(self, name: str, value: Any):
        # Find where the variable is defined in the scope chain
        if name in self.variables:
            declared = self.types.get(name)
            if declared is not None and not _matches_type(value, declared):
                raise RuntimeTypeError(
                    f"Type mismatch on assignment to '{name}': annotated '{declared}' but assigning value of type '{_literal_type_name(value)}'"
                )
            self.variables[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise NameError(f"Variável '{name}' não definida")

    def get_declared_type(self, name: str) -> Optional[str]:
        if name in self.types:
            return self.types[name]
        if self.parent:
            return self.parent.get_declared_type(name)
        return None


class CorpLangFunction:
    def __init__(
        self,
        declaration: Any,
        closure: Optional[Environment],
        bound_this: Optional[Any] = None,
        bound_name: Optional[str] = None,
    ):
        # declaration can be FunctionDeclaration or MethodDeclaration; accept Any
        self.declaration = declaration
        self.closure = closure
        self.bound_this = bound_this
        self.bound_name = bound_name

    def call(self, interpreter, args: List[Any]) -> Any:
        env = Environment(self.closure)

        # Bind parameters
        pmap = getattr(self.declaration, "param_types", None)
        pdefaults = getattr(self.declaration, "param_defaults", None)
        for i, param in enumerate(self.declaration.params):
            ptype = None
            if pmap is not None and isinstance(pmap, dict):
                ptype = pmap.get(param)
            if i < len(args):
                # define with potential annotation (will enforce)
                env.define(param, args[i], type_annotation=ptype)
            else:
                # If a default expression exists, evaluate it in the new env
                if pdefaults and isinstance(pdefaults, dict) and param in pdefaults:
                    try:
                        default_node = pdefaults[param]
                        default_value = interpreter.evaluate_with_generic_context(
                            default_node, None
                        )
                    except Exception:
                        default_value = None
                    env.define(param, default_value, type_annotation=ptype)
                else:
                    env.define(param, None, type_annotation=ptype)

        # If this intent is bound to a 'this' (method), set it in the env
        if getattr(self, "bound_this", None) is not None:
            env.define("this", self.bound_this)

        # If intent is async, run in a background thread and return an AsyncTask
        if getattr(self.declaration, "is_async", False):
            task = AsyncTask()

            def runner():
                try:
                    # push frame
                    frame_name = self.bound_name or self.declaration.name
                    interpreter.call_stack.append(
                        {
                            "name": frame_name,
                            "node": self.declaration,
                            "file": interpreter.current_file_path,
                        }
                    )
                    try:
                        # Execute intent body in this interpreter with new env
                        interpreter.execute_block(self.declaration.body, env)
                    finally:
                        interpreter.call_stack.pop()
                    task.set_result(None)
                except ReturnException as ret:
                    task.set_result(ret.value)
                except Exception as e:
                    task.set_exception(e)

            task.start(runner)
            return task

        try:
            frame_name = self.bound_name or self.declaration.name
            interpreter.call_stack.append(
                {
                    "name": frame_name,
                    "node": self.declaration,
                    "file": interpreter.current_file_path,
                }
            )
            try:
                interpreter.execute_block(self.declaration.body, env)
            finally:
                interpreter.call_stack.pop()
        except ReturnException as ret:
            return ret.value

        return None


class ClassObject:
    def __init__(
        self,
        name: str,
        fields: Dict[str, FieldDeclaration],
        methods: Dict[str, MethodDeclaration],
        extends: Optional[str] = None,
        implements: Optional[List[str]] = None,
        is_abstract: bool = False,
    ):
        self.name = name
        # Separate instance and static members for clarity
        self.instance_fields: Dict[str, FieldDeclaration] = {}
        self.static_fields: Dict[str, FieldDeclaration] = {}
        self.instance_methods: Dict[str, MethodDeclaration] = {}
        self.static_methods: Dict[str, MethodDeclaration] = {}
        # evaluated static field values
        self.static_field_values: Dict[str, Any] = {}
        # parent class object (resolved at class registration time when possible)
        self.parent: Optional["ClassObject"] = None
        # Fill maps based on declarations
        for fname, fdecl in (fields or {}).items():
            if getattr(fdecl, "is_static", False):
                self.static_fields[fname] = fdecl
            else:
                self.instance_fields[fname] = fdecl

        for mname, mdecl in (methods or {}).items():
            if getattr(mdecl, "is_static", False):
                self.static_methods[mname] = mdecl
            else:
                self.instance_methods[mname] = mdecl
        self.extends = extends
        self.interfaces = implements or []
        self.is_abstract = is_abstract

    def get_instance_method(self, name: str) -> Optional[MethodDeclaration]:
        cur = self
        while cur:
            if name in cur.instance_methods:
                return cur.instance_methods[name]
            cur = cur.parent
        return None

    def get_static_method(self, name: str) -> Optional[MethodDeclaration]:
        cur = self
        while cur:
            if name in cur.static_methods:
                return cur.static_methods[name]
            cur = cur.parent
        return None

    def get_static_field_value(self, name: str) -> Optional[Any]:
        cur = self
        while cur:
            if name in cur.static_field_values:
                return cur.static_field_values[name]
            cur = cur.parent
        return None


class InstanceObject:
    def __init__(self, class_obj: ClassObject, interpreter: "Interpreter"):
        self.__class_obj = class_obj
        self.__interpreter = interpreter
        # store instance fields here
        self._fields: Dict[str, Any] = {}

    @property
    def class_obj(self) -> ClassObject:
        return self.__class_obj

    def get(self, name: str) -> Any:
        # instance field
        if name in self._fields:
            # if declared and private, enforce read access
            fdecl = self.__class_obj.instance_fields.get(name)
            if fdecl and getattr(fdecl, "is_private", False):
                # allow if caller is a method of this class
                if self.__interpreter.call_stack:
                    caller = self.__interpreter.call_stack[-1]
                    caller_name = caller.get("name", "")
                    if not caller_name.startswith(f"{self.__class_obj.name}."):
                        raise RuntimeError(
                            f"Cannot read private field '{name}' of class '{self.__class_obj.name}'"
                        )
            return self._fields[name]

        # instance method lookup (respect inheritance): return a CorpLangFunction bound to this
        mdecl = self.__class_obj.get_instance_method(name)
        if mdecl is not None:
            return CorpLangFunction(
                mdecl,
                self.__interpreter.globals,
                bound_this=self,
                bound_name=f"{self.__class_obj.name}.{mdecl.name}",
            )

        # static method access via instance should be allowed (fallback), respect inheritance
        mdecl = self.__class_obj.get_static_method(name)
        if mdecl is not None:
            return CorpLangFunction(
                mdecl,
                self.__interpreter.globals,
                bound_this=None,
                bound_name=f"{self.__class_obj.name}.{mdecl.name}",
            )
        # no field or method found
        raise AttributeError(
            f"'{self.__class_obj.name}' object has no attribute '{name}'"
        )

    def set(self, name: str, value: Any):
        # enforce private/private access: if field declared and is private, ensure only this instance methods can set it
        fdecl = self.__class_obj.instance_fields.get(name)
        if fdecl and getattr(fdecl, "is_private", False):
            # inspect call stack top to see if caller is a method of this class
            if self.__interpreter.call_stack:
                caller = self.__interpreter.call_stack[-1]
                caller_name = caller.get("name", "")
                # allow if caller starts with ClassName.
                if not caller_name.startswith(f"{self.__class_obj.name}."):
                    raise RuntimeError(
                        f"Cannot access private field '{name}' of class '{self.__class_obj.name}'"
                    )
        self._fields[name] = value


class AsyncTask:
    def __init__(self):
        self._thread = None
        self._result = None
        self._exc = None
        self._done = threading.Event()

    def start(self, target):
        def wrapper():
            try:
                target()
            finally:
                # ensure flag set
                self._done.set()

        # Use non-daemon thread so it can finish cleanly before interpreter exit
        self._thread = threading.Thread(target=wrapper, daemon=False)
        self._thread.start()

    def set_result(self, value):
        self._result = value
        self._done.set()

    def set_exception(self, exc):
        self._exc = exc
        self._done.set()

    def wait(self, timeout: Optional[float] = None):
        self._done.wait(timeout)
        if self._exc:
            raise self._exc
        # Ensure the background thread has fully terminated before returning
        try:
            if self._thread is not None:
                # join without blocking indefinitely if timeout provided
                if timeout is None:
                    self._thread.join()
                else:
                    # join at most the remaining timeout
                    self._thread.join(timeout)
        except Exception:
            pass

        return self._result


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class CorpLangRaisedException(RuntimeError):
    def __init__(self, value, message, frames, type_name, node=None):
        super().__init__(message)
        self.value = value
        self.frames = frames
        self.type_name = type_name
        self.node = node
        self.message = message


class Interpreter:
    def __init__(self):
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.datasets: Dict[str, Any] = {}
        self.models: Dict[str, Any] = {}
        # directory of the file currently being interpreted (for relative imports)
        self.current_file_dir: str = os.getcwd()
        # path to the current file being interpreted (used for traceback snippets)
        self.current_file_path: Optional[str] = None
        # call stack for traceback printing: list of frames {name, node}
        self.call_stack: List[Dict[str, Any]] = []
        # captured stack traces for exception values (id -> frames)
        self.exception_traces: Dict[int, List[Dict[str, Any]]] = {}
        # stack of active exceptions for rethrow handling
        self._active_exceptions: List[CorpLangRaisedException] = []
        # Initialize built-in functions and globals so they're available
        # to any threads or tasks started by this interpreter.
        self.define_builtins()
        # NOTE: core modules are available via load_core_modules().
        # We do NOT auto-load them here to avoid blocking startup when core
        # contains constructs not yet supported by the parser. Callers can
        # explicitly call `interpreter.load_core_modules()` when ready.

    def resolve_import_path(self, dotted_name: str) -> Optional[str]:
        """Resolve import dotted_name to a file path by trying:
        - relative to current_file_dir and its parent directories
        - project root (dotted -> path)
        Returns the first existing path or None.
        """
        rel_path = dotted_name.replace(".", os.sep) + ".mp"

        # try current directory and parents
        cur = self.current_file_dir
        # limit traversal to avoid infinite loops
        max_levels = 10
        while cur and max_levels > 0:
            candidate = os.path.join(cur, rel_path)
            if os.path.exists(candidate):
                return candidate
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
            max_levels -= 1

        # fallback to project-relative
        if os.path.exists(rel_path):
            return rel_path

        # As a last resort, scan workspace for a matching trailing path (slow, but permissive)
        workspace_root = os.getcwd()
        for root, dirs, files in os.walk(workspace_root):
            candidate = os.path.join(root, rel_path)
            if os.path.exists(candidate):
                return candidate

        return None

    def define_builtins(self):
        def print_func(*args):
            # Arguments are already evaluated before reaching builtin; just stringify
            output_parts = [str(a) for a in args]
            print(" ".join(output_parts))
            return None

        def len_func(obj):
            if isinstance(obj, (str, list)):
                return len(obj)
            return 0

        def type_func(obj):
            type_value = type(obj).__name__
            if obj is None:
                type_value = "null"
            elif type_value == "str":
                type_value = "string"
            return type_value

        def wait_seconds(seconds):
            try:
                seconds = float(seconds)
                time.sleep(seconds)
                return True
            except Exception:
                return False

        def json_parse(json_str):
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None

        def json_stringify(obj):
            try:
                return json.dumps(obj, ensure_ascii=False, indent=2)
            except TypeError:
                return str(obj)

        def get_keys(obj):
            if isinstance(obj, dict):
                return list(obj.keys())
            return []

        def get_values(obj):
            if isinstance(obj, dict):
                return list(obj.values())
            return []

        def list_push(lst, item):
            try:
                lst.append(item)
                return True
            except Exception:
                return False

        def exception_stack_trace(value):
            interp = _get_current_interpreter()
            if interp is None:
                return []
            return interp.get_exception_stack(value)

        def exception_message(value):
            interp = _get_current_interpreter()
            if interp is None:
                if value is None:
                    return "null"
                return str(value)
            return interp._format_exception_message(value)

        def exception_type(value):
            interp = _get_current_interpreter()
            if interp is None:
                if value is None:
                    return "null"
                return type(value).__name__
            return interp._detect_exception_type(value)

        self.globals.define("JSON.parser", json_parse)
        self.globals.define("JSON.stringify", json_stringify)
        self.globals.define("Object.keys", get_keys)
        self.globals.define("Object.values", get_values)
        self.globals.define("list.push", list_push)
        self.globals.define("exceptionStackTrace", exception_stack_trace)
        self.globals.define("exceptionMessage", exception_message)
        self.globals.define("exceptionType", exception_type)
        self.globals.define("waitSeconds", wait_seconds)
        self.globals.define("print", print_func)
        self.globals.define("sout", print_func)
        self.globals.define("len", len_func)
        self.globals.define("type", type_func)

        # Null values
        self.globals.define("null", None)
        self.globals.define("None", None)

        # --- Native MF07 core modules (mf.collections, mf.json, mf.objects, mf.utils)

        # Python-backed generic List implementation
        class NativeList(list):
            def append_item(self, item):
                self.append(item)

            def insert_at(self, index, item):
                self.insert(index, item)

            def remove_at(self, index):
                return self.pop(index)

            def index_of(self, item):
                try:
                    return self.index(item)
                except ValueError:
                    return -1

            def clear_all(self):
                self.clear()

            def map_fn(self, fn):
                res = NativeList()
                for v in self:
                    try:
                        try:
                            res.append(fn(v))
                        except TypeError:
                            # try CorpLangFunction.call with current interpreter
                            interp = _get_current_interpreter()
                            if interp is not None and hasattr(fn, "call"):
                                res.append(fn.call(interp, [v]))
                            else:
                                raise
                    except Exception:
                        res.append(None)
                return res

            def filter_fn(self, fn):
                res = NativeList()
                for v in self:
                    try:
                        ok = False
                        try:
                            ok = fn(v)
                        except TypeError:
                            interp = _get_current_interpreter()
                            if interp is not None and hasattr(fn, "call"):
                                ok = fn.call(interp, [v])
                            else:
                                raise
                        if ok:
                            res.append(v)
                    except Exception:
                        pass
                return res

            def for_each(self, fn):
                for v in self:
                    try:
                        try:
                            fn(v)
                        except TypeError:
                            interp = _get_current_interpreter()
                            if interp is not None and hasattr(fn, "call"):
                                fn.call(interp, [v])
                            else:
                                raise
                    except Exception:
                        pass

            def to_string(self):
                parts = []
                for v in self:
                    try:
                        parts.append(str(v))
                    except Exception:
                        parts.append("null")
                return "[" + ", ".join(parts) + "]"

            # Aliases expected by MF07 core modules
            def push(self, item):
                return self.append_item(item)

            def insertAt(self, index, item):
                return self.insert_at(index, item)

            def deleteAt(self, index):
                return self.remove_at(index)

            def indexOf(self, item):
                return self.index_of(item)

            def clear(self):
                return self.clear_all()

            def contains(self, item):
                return item in self

            def map(self, fn):
                return self.map_fn(fn)

            def filter(self, fn):
                return self.filter_fn(fn)

            def forEach(self, fn):
                return self.for_each(fn)

            def toString(self):
                return self.to_string()

            def length(self):
                return len(self)

        # Map backed by dict
        class NativeMap(dict):
            def set(self, key, value):
                self[key] = value

            def get(self, key):
                return super().get(key, None)

            def has(self, key):
                return key in self

            def delete(self, key):
                if key in self:
                    del self[key]
                    return True
                return False

            def size(self):
                return len(self)

            def keys(self):
                return list(super().keys())

            def values(self):
                return list(super().values())

            def entries(self):
                return list(super().items())

        # Set backed by Python set
        class NativeSet(set):
            def add(self, element):
                super().add(element)

            def has(self, element):
                return element in self

            def delete(self, element):
                if element in self:
                    super().remove(element)
                    return True
                return False

            def size(self):
                return len(self)

            def values(self):
                return list(self)

        # JSON utilities
        def mf_json_parse(s):
            try:
                return json.loads(s)
            except Exception:
                return None

        def mf_json_stringify(o):
            try:
                return json.dumps(o, ensure_ascii=False)
            except Exception:
                return str(o)

        # Object utilities
        def obj_keys(o):
            if isinstance(o, dict):
                return list(o.keys())
            try:
                return [k for k in dir(o) if not k.startswith("__")]
            except Exception:
                return []

        def obj_values(o):
            if isinstance(o, dict):
                return list(o.values())
            try:
                return [getattr(o, k) for k in dir(o) if not k.startswith("__")]
            except Exception:
                return []

        def obj_entries(o):
            if isinstance(o, dict):
                return list(o.items())
            try:
                return [(k, getattr(o, k)) for k in dir(o) if not k.startswith("__")]
            except Exception:
                return []

        def obj_clone(o):
            try:
                return json.loads(json.dumps(o))
            except Exception:
                return o

        # Register under mf namespace (as nested dict-like objects)
        mf_collections = {
            "List": NativeList,
            "Map": NativeMap,
            "Set": NativeSet,
        }

        mf_json = {
            "parse": mf_json_parse,
            "stringify": mf_json_stringify,
        }

        # Map utilities
        def map_put(map_obj, key, value):
            map_obj[key] = value

        def map_get(map_obj, key):
            return dict.get(map_obj, key, None)

        def map_has(map_obj, key):
            return key in map_obj

        def map_remove(map_obj, key):
            if key in map_obj:
                del map_obj[key]
                return True
            return False

        mf_objects = {
            "keys": obj_keys,
            "values": obj_values,
            "entries": obj_entries,
            "clone": obj_clone,
            "Map": NativeMap,
            "Set": NativeSet,
            "mapPut": map_put,
            "mapGet": map_get,
            "mapHas": map_has,
            "mapRemove": map_remove,
        }

        # String utilities
        def str_upper(s):
            if s is None:
                return ""
            return str(s).upper()

        def str_lower(s):
            if s is None:
                return ""
            return str(s).lower()

        def str_strip(s):
            if s is None:
                return ""
            return str(s).strip()

        mf_utils = {
            "len": len_func,
            "type": type_func,
            "upper": str_upper,
            "lower": str_lower,
            "strip": str_strip,
        }

        mf_fs = {
            "read_text": mf_fs_native.read_text,
            "write_text": mf_fs_native.write_text,
            "append_text": mf_fs_native.append_text,
            "read_json": mf_fs_native.read_json,
            "write_json": mf_fs_native.write_json,
            "read_bytes": mf_fs_native.read_bytes,
            "write_bytes": mf_fs_native.write_bytes,
            "exists": mf_fs_native.exists,
            "is_file": mf_fs_native.is_file,
            "is_dir": mf_fs_native.is_dir,
            "make_dir": mf_fs_native.make_dir,
            "touch": mf_fs_native.touch,
            "remove": mf_fs_native.remove,
            "list_dir": mf_fs_native.list_dir,
            "copy": mf_fs_native.copy,
            "move": mf_fs_native.move,
            "stat": mf_fs_native.stat,
            "glob": mf_fs_native.glob,
            "walk": mf_fs_native.walk,
            "cwd": mf_fs_native.cwd,
            "home": mf_fs_native.home,
            "separator": mf_fs_native.separator,
            "parent": mf_fs_native.parent,
        }

        mf_connections = {
            "tcp_connect": mf_connections_native.tcp_connect,
            "tcp_close": mf_connections_native.tcp_close,
            "tcp_send": mf_connections_native.tcp_send,
            "tcp_receive": mf_connections_native.tcp_receive,
            "tcp_listen": mf_connections_native.tcp_listen,
            "tcp_accept": mf_connections_native.tcp_accept,
            "tcp_shutdown": mf_connections_native.tcp_shutdown,
            "set_timeout": mf_connections_native.set_timeout,
            "connection_info": mf_connections_native.connection_info,
        }

        mf_path = {
            "join": mf_path_native.join,
            "join_all": mf_path_native.join_all,
            "basename": mf_path_native.basename,
            "dirname": mf_path_native.dirname,
            "stem": mf_path_native.stem,
            "extname": mf_path_native.extname,
            "parts": mf_path_native.parts,
            "split": mf_path_native.split,
            "normalize": mf_path_native.normalize,
            "resolve": mf_path_native.resolve,
            "relative_to": mf_path_native.relative_to,
            "is_absolute": mf_path_native.is_absolute,
            "match": mf_path_native.match,
            "common_path": mf_path_native.common_path,
            "with_suffix": mf_path_native.with_suffix,
            "expanduser": mf_path_native.expanduser,
            "to_posix": mf_path_native.to_posix,
            "to_windows": mf_path_native.to_windows,
            "cwd": mf_path_native.cwd,
            "home": mf_path_native.home,
            "drive": mf_path_native.drive,
        }

        mf_datetime = {
            "now": mf_datetime_native.now,
            "datetime": mf_datetime_native._datetime,
            "today": mf_datetime_native.today,
            "from_timestamp": mf_datetime_native.from_timestamp,
            "to_timestamp": mf_datetime_native.to_timestamp,
            "format": mf_datetime_native.format,
            "parse": mf_datetime_native.parse,
        }

        mf_hash = {
            "md5": mf_hash_native.md5,
            "sha1": mf_hash_native.sha1,
            "sha256": mf_hash_native.sha256,
            "sha512": mf_hash_native.sha512,
            "hmac": mf_hash_native.hmac,
            "hmac_sha256": mf_hash_native.hmac_sha256,
            "hmac_sha512": mf_hash_native.hmac_sha512,
            "uuid4": mf_hash_native.uuid4,
            "uuid3": mf_hash_native.uuid3,
            "uuid": mf_hash_native.uuid1,
            "uuid5": mf_hash_native.uuid5,
            "base64_encode": mf_hash_native.base64_encode,
            "base64_decode": mf_hash_native.base64_decode,
            "apply_hash_algorithm": mf_hash_native.apply_hash_algorithm,
        }

        # === PROTOTYPE METHODS FOR PRIMITIVE TYPES ===
        # Define methods that can be called on primitive values

        # String prototype methods
        def str_prototype_upper(s):
            return str(s).upper() if s is not None else ""

        def str_prototype_lower(s):
            return str(s).lower() if s is not None else ""

        def str_prototype_trim(s):
            return str(s).strip() if s is not None else ""

        def str_prototype_get_length(s):
            return len(str(s)) if s is not None else 0

        def str_prototype_contains(s, substring):
            if s is None or substring is None:
                return False
            return substring in str(s)

        def str_prototype_startswith(s, prefix):
            if s is None or prefix is None:
                return False
            return str(s).startswith(str(prefix))

        def str_prototype_endswith(s, suffix):
            if s is None or suffix is None:
                return False
            return str(s).endswith(str(suffix))

        def str_prototype_replace(s, old, new):
            if s is None:
                return ""
            return str(s).replace(str(old), str(new))

        # Number prototype methods
        def num_prototype_tostring(n):
            return str(n) if n is not None else "0"

        def num_prototype_format_currency(n, currency="USD"):
            if n is None:
                n = 0
            if currency.upper() == "BRL":
                return (
                    f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
            elif currency.upper() == "USD":
                return f"$ {n:,.2f}"
            elif currency.upper() == "EUR":
                return f"€ {n:,.2f}"
            else:
                return f"{currency} {n:,.2f}"

        def num_prototype_to_fixed(n, decimals=2):
            if n is None:
                n = 0
            return f"{n:.{decimals}f}"

        def num_prototype_abs(n):
            return abs(n) if n is not None else 0

        def num_prototype_round(n, decimals=0):
            if n is None:
                n = 0
            return round(n, decimals)

        # Store prototype methods in a registry
        self.prototype_methods = {
            "string": {
                "upper": str_prototype_upper,
                "lower": str_prototype_lower,
                "trim": str_prototype_trim,
                "length": str_prototype_get_length,
                "contains": str_prototype_contains,
                "startsWith": str_prototype_startswith,
                "endsWith": str_prototype_endswith,
                "replace": str_prototype_replace,
            },
            "str": {
                "upper": str_prototype_upper,
                "lower": str_prototype_lower,
                "trim": str_prototype_trim,
                "length": str_prototype_get_length,
                "contains": str_prototype_contains,
                "startsWith": str_prototype_startswith,
                "endsWith": str_prototype_endswith,
                "replace": str_prototype_replace,
            },
            "int": {
                "toString": num_prototype_tostring,
                "formatCurrency": num_prototype_format_currency,
                "toFixed": num_prototype_to_fixed,
                "abs": num_prototype_abs,
                "round": num_prototype_round,
            },
            "float": {
                "toString": num_prototype_tostring,
                "formatCurrency": num_prototype_format_currency,
                "toFixed": num_prototype_to_fixed,
                "abs": num_prototype_abs,
                "round": num_prototype_round,
            },
            "datetime": {
                "toString": num_prototype_tostring,
                "isoformat": lambda dt: dt.isoformat() if dt else "",
                "strftime": lambda dt, fmt: dt.strftime(fmt) if dt else "",
            },
        }

        # Strict HTTPS module (mocked, no real HTTP requests)
        def request(options: Any) -> dict:
            client = HttpClient(
                base_url=options.get("uri", ""),
                defaults_headers=options.get("headers", {}),
            )
            try:
                # For now, just return a mock response
                response = client.execute(options)
                return response
            except Exception as e:
                return {"error": str(e)}

        mf_strict_https = {"request": request}
        mf_payload_utils = {"request": request}
        mf_strict_connections = {"request": request}
        mf_strict_utils = {"request": request}

        # Auto-imported namespace registration (exposed as dotted names and as 'mf' top-level mapping)
        # expose a nested 'mf' mapping so code can use `mf.collections.List` syntax
        mf_namespace = {
            "collections": mf_collections,
            "json": mf_json,
            "strict": {
                "https": mf_strict_https,
                "payload": mf_payload_utils,
                "connections": mf_strict_connections,
                "utils": mf_strict_utils,
            },
            "connections": mf_connections,
            "objects": mf_objects,
            "utils": mf_utils,
            "fs": mf_fs,
            "path": mf_path,
            "datetime": mf_datetime,
            "hash": mf_hash,
        }
        self.globals.define("mf", mf_namespace)

        # keep dotted names for backwards compatibility - Http Requests
        self.globals.define("mf.strict.https", mf_strict_https)
        self.globals.define("mf.strict.payload", mf_payload_utils)
        self.globals.define("mf.strict.connections", mf_strict_connections)
        self.globals.define("mf.strict.utils", mf_strict_utils)

        # keep dotted names for backwards compatibility
        self.globals.define("mf.collections", mf_collections)
        self.globals.define("mf.json", mf_json)
        self.globals.define("mf.objects", mf_objects)
        self.globals.define("mf.utils", mf_utils)
        self.globals.define("mf.fs", mf_fs)
        self.globals.define("mf.path", mf_path)
        self.globals.define("mf.datetime", mf_datetime)
        self.globals.define("mf.hash", mf_hash)
        self.globals.define("mf.connections", mf_connections)

        # Expose convenient top-level aliases (e.g., List -> mf.collections.List)
        self.globals.define("List", NativeList)
        self.globals.define("Map", NativeMap)
        self.globals.define("Set", NativeSet)

        # JSON/Object utilities at top-level and under mf namespace
        self.globals.define("JSON.parse", mf_json_parse)
        self.globals.define("JSON.stringify", mf_json_stringify)

        # Object namespace
        object_namespace = {
            "keys": obj_keys,
            "values": obj_values,
            "entries": obj_entries,
            "clone": obj_clone,
        }
        self.globals.define("Object", object_namespace)

        # Keep dotted names for backwards compatibility
        self.globals.define("Object.keys", obj_keys)
        self.globals.define("Object.values", obj_values)
        self.globals.define("Object.entries", obj_entries)
        self.globals.define("Object.clone", obj_clone)

    def load_core_modules(self, core_dir: Optional[str] = None):
        """Load all .mp files inside the project's core/ directory and execute them
        into the global environment prior to user code execution. For each module we
        also register a `core.<modname>` mapping containing the exported symbols.
        """
        if core_dir is None:
            core_dir = os.path.join(os.getcwd(), "core")

        debug(f"Diretório core: {core_dir}", component="core-loader")
        if not os.path.isdir(core_dir):
            warn(
                f"Diretório core não encontrado: {core_dir} - nada a carregar",
                component="core-loader",
            )
            return

        # iterate sorted for deterministic order
        files = sorted([f for f in os.listdir(core_dir) if f.endswith(".mp")])

        # Professional logging: show summary instead of individual files
        loaded_modules = []
        for fname in files:
            path = os.path.join(core_dir, fname)
            modname = os.path.splitext(fname)[0]
            # Removed detailed logging per file for cleaner output

            try:
                trace(f"Lendo arquivo {path}", component="core-loader")
                with open(path, "r", encoding="utf-8") as f:
                    src = f.read()

                # snapshot globals before
                before_keys = set(self.globals.variables.keys())
                trace(
                    f"Snapshot de chaves antes: {len(before_keys)}",
                    component="core-loader",
                )

                # parse
                trace(f"Tokenizando {fname}", component="core-loader")
                lexer = Lexer(src)
                tokens = lexer.tokenize()
                trace(f"Tokens gerados: {len(tokens)}", component="core-loader")

                trace(f"Parseando AST de {fname}", component="core-loader")
                parser = Parser(tokens)
                trace(
                    "Tokens para AST prontos, iniciando parse...",
                    component="core-loader",
                )
                ast = parser.parse()
                # AST parsed successfully (detailed logging removed)

                prev_path = getattr(self, "current_file_path", None)
                prev_dir = getattr(self, "current_file_dir", None)
                self.current_file_path = os.path.abspath(path)
                self.current_file_dir = os.path.dirname(self.current_file_path)
                try:
                    # Interpret core module into global environment
                    trace(f"Interpretando AST de {fname}", component="core-loader")
                    self.interpret(ast)
                    # Interpretation completed (detailed logging removed)
                finally:
                    self.current_file_path = prev_path
                    self.current_file_dir = prev_dir or os.getcwd()

                # exported symbols: difference of globals
                after_keys = set(self.globals.variables.keys())
                new_keys = after_keys - before_keys
                exports = {}
                for k in new_keys:
                    exports[k] = self.globals.variables[k]

                # Auto-expose all core classes to global namespace
                for class_name in new_keys:
                    class_obj = self.globals.variables[class_name]
                    # Only auto-expose ClassObject instances (MF07 classes)
                    if isinstance(class_obj, ClassObject):
                        # Class is already in global scope from interpretation
                        pass  # Removed detailed logging
                    # Also auto-expose other useful exports like Utils, etc.
                    elif callable(class_obj) or hasattr(class_obj, "__call__"):
                        pass  # Removed detailed logging

                # register module under core.<modname>
                self.globals.define(f"core.{modname}", exports)
                loaded_modules.append(modname)  # Track for summary
            except Exception as e:
                # Don't let individual core module failures stop other modules from loading
                error(f"Erro ao carregar '{fname}': {e}", component="core-loader")
                warn("Continuando com próximo módulo...", component="core-loader")

        # Professional logging: show summary of loaded modules
        if loaded_modules:
            info(
                f"CorpLang Core: {len(loaded_modules)} modules loaded ({', '.join(loaded_modules)})",
                component="core-loader",
            )

        # After loading all core modules, override built-in namespaces with core implementations
        self._override_builtins_with_core()

    def _override_builtins_with_core(self):
        """Override built-in namespaces with core module implementations if they exist.
        Automatically replaces built-in classes/namespaces with core implementations."""

        # Map of built-in names to core class replacements
        builtin_replacements = {
            "Object": "objects",  # Object namespace from core/objects.mp
            "JSON": "json",  # JSON namespace from core/json.mp
            "Utils": "utils",  # Utils class from core/utils.mp
            "String": "string",  # String class from core/string.mp (if exists)
            "List": "list",  # List class from core/list.mp (if exists)
        }

        try:
            for builtin_name, core_module in builtin_replacements.items():
                # Check if we have a core class for this built-in
                if builtin_name in self.globals.variables:
                    core_class = self.globals.variables[builtin_name]

                    # Handle ClassObject (MF07 classes with static methods)
                    if (
                        isinstance(core_class, ClassObject)
                        and hasattr(core_class, "static_methods")
                        and core_class.static_methods
                    ):
                        # Create namespace from static methods
                        namespace = {}
                        for (
                            method_name,
                            method_decl,
                        ) in core_class.static_methods.items():
                            corp_func = CorpLangFunction(
                                method_decl,
                                self.globals,
                                bound_this=None,
                                bound_name=f"{builtin_name}.{method_name}",
                            )
                            namespace[method_name] = corp_func

                        # Replace built-in namespace with core implementation
                        self.globals.define(builtin_name, namespace)
                        # Namespace replacement completed (detailed logging removed)

                        # Also maintain dotted notation for compatibility
                        for method_name, corp_func in namespace.items():
                            self.globals.define(
                                f"{builtin_name}.{method_name}", corp_func
                            )

                    # Handle regular classes or callables - keep as-is since they're already global
                    elif isinstance(core_class, ClassObject):
                        # Core class already available (detailed logging removed)
                        pass

        except Exception as e:
            warn(f"Falha ao substituir builtins com core: {e}", component="core-loader")

    def _eval_interpolated_expression(self, expr_text: str) -> Any:
        """Parse and evaluate a small expression found inside { ... } in a string.
        If parsing or evaluation fails, raises Exception.
        """
        # Reuse Lexer/Parser to parse the expression
        try:
            lexer = Lexer(expr_text)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            node = parser.parse_expression()
            return self.evaluate(node)
        except Exception:
            # propagate to caller so caller can decide to keep placeholder
            raise

    def get_exception_stack(self, value) -> List[Dict[str, Any]]:
        return self.exception_traces.get(id(value), [])

    def _detect_exception_type(self, value: Any) -> str:
        if isinstance(value, InstanceObject):
            return value.class_obj.name
        if value is None:
            return "null"
        python_name = type(value).__name__
        alias = {
            "str": "string",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "dict": "Map",
            "list": "List",
        }
        return alias.get(python_name, python_name)

    def _format_exception_message(self, value: Any) -> str:
        if isinstance(value, InstanceObject):
            try:
                message_value = value.get("message")
                if message_value is not None:
                    return str(message_value)
            except Exception:
                pass
            try:
                to_string = value.get("toString")
                if hasattr(to_string, "call"):
                    result = to_string.call(self, [])
                    if result is not None:
                        return str(result)
            except Exception:
                pass
            return value.class_obj.name
        if value is None:
            return "null"
        return str(value)

    def _attach_stack_to_value(self, value: Any, frames: List[Dict[str, Any]]):
        try:
            self.exception_traces[id(value)] = frames
        except Exception:
            pass

        if isinstance(value, InstanceObject):
            try:
                attach = value.get("_attachStackTrace")
                if hasattr(attach, "call"):
                    attach.call(self, [frames])
                    return
            except Exception:
                pass
            try:
                value.set("stackTrace", frames)
            except Exception:
                pass
        elif isinstance(value, dict):
            try:
                value["stackTrace"] = frames
            except Exception:
                pass

    def _capture_traceback(self, node: Optional[Any]) -> List[Dict[str, Any]]:
        frames: List[Dict[str, Any]] = []
        cache: Dict[str, Optional[List[str]]] = {}

        def read_line_text(
            path: Optional[str], line_number: Optional[int]
        ) -> Optional[str]:
            if path is None or line_number is None:
                return None
            if path not in cache:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        cache[path] = f.readlines()
                except Exception:
                    cache[path] = None
            lines = cache.get(path)
            if not lines:
                return None
            index = line_number - 1
            if index < 0 or index >= len(lines):
                return None
            return lines[index].rstrip("\n")

        if node is not None:
            line = getattr(node, "line", None)
            column = getattr(node, "column", None)
            frames.append(
                {
                    "function": "<throw>",
                    "file": self.current_file_path,
                    "line": line,
                    "column": column,
                    "source": read_line_text(self.current_file_path, line),
                }
            )

        for frame in reversed(list(self.call_stack)):
            frame_node = frame.get("node")
            frame_file = frame.get("file") or self.current_file_path
            line = getattr(frame_node, "line", None)
            column = getattr(frame_node, "column", None)
            frames.append(
                {
                    "function": frame.get("name") or "<anonymous>",
                    "file": frame_file,
                    "line": line,
                    "column": column,
                    "source": read_line_text(frame_file, line),
                }
            )

        return frames

    def _exception_matches(
        self, exc: CorpLangRaisedException, type_name: Optional[str]
    ) -> bool:
        if type_name is None:
            return True
        normalized = type_name.split(".")[-1]
        detected = self._detect_exception_type(exc.value)
        if normalized == detected:
            return True
        if isinstance(exc.value, InstanceObject):
            current = exc.value.class_obj
            while current:
                if current.name == normalized:
                    return True
                current = current.parent
            if normalized == "Exception":
                return False
        if normalized == "Exception":
            return False
        return False

    def _execute_catch_clause(self, clause: CatchClause, exc: CorpLangRaisedException):
        catch_env = Environment(self.environment)
        previous = self.environment
        self.environment = catch_env
        try:
            if clause.exception_var:
                self.environment.define(clause.exception_var, exc.value)
            self.execute_block(clause.body)
        finally:
            self.environment = previous

    def _raise_runtime_exception(self, value: Any, node: Optional[Any]):
        message = self._format_exception_message(value)
        type_name = self._detect_exception_type(value)
        frames = self._capture_traceback(node)
        self._attach_stack_to_value(value, frames)
        raise CorpLangRaisedException(value, message, frames, type_name, node=node)

    def _execute_try_statement(self, node: TryStatement):
        captured: Optional[CorpLangRaisedException] = None
        handled = False
        try:
            self.execute_block(node.try_block)
        except CorpLangRaisedException as exc:
            captured = exc
            for clause in node.catch_clauses:
                if self._exception_matches(exc, clause.exception_type):
                    handled = True
                    self._active_exceptions.append(exc)
                    try:
                        self._execute_catch_clause(clause, exc)
                        captured = None
                    finally:
                        self._active_exceptions.pop()
                    break
        finally:
            if node.finally_block is not None:
                self.execute_block(node.finally_block)
        if captured is not None and not handled:
            raise captured

    def _print_traceback(self, exc: Exception, node: Optional[Any] = None):
        print("Traceback (most recent call last):")

        if isinstance(exc, CorpLangRaisedException):
            frames = exc.frames or self._capture_traceback(exc.node or node)
            exc_type = exc.type_name
            message = exc.message
        else:
            frames = self._capture_traceback(node)
            exc_type = type(exc).__name__
            message = str(exc)

        if frames:
            for entry in frames:
                file = entry.get("file") or "<unknown>"
                line = entry.get("line")
                column = entry.get("column")
                function = entry.get("function") or "<program>"
                source = entry.get("source")
                if line is not None and column is not None:
                    print(
                        f'  File "{file}", line {line}, column {column}, in {function}'
                    )
                elif line is not None:
                    print(f'  File "{file}", line {line}, in {function}')
                else:
                    print(f'  File "{file}", in {function}')
                if source:
                    print(f"    {source}")
                    if column and column > 0:
                        caret = " " * (column - 1) + "^"
                        print(f"    {caret}")
        else:
            if node is not None:
                snippet = _ast_to_source(node)
                print(f"  File <corplang>, in <program>\n    {snippet}")
            for frame in reversed(self.call_stack):
                print(f"  In {frame.get('name')}")

        print(f"{exc_type}: {message}")

    def _suggest_import_candidates(self, rel_path: str) -> List[str]:
        """Return up to 5 suggested candidate paths for a missing import by searching the workspace and using fuzzy matching."""
        workspace_root = os.getcwd()
        target_basename = os.path.basename(rel_path)
        candidates: List[str] = []

        # First pass: exact basename matches
        for root, dirs, files in os.walk(workspace_root):
            for f in files:
                if not f.endswith(".mp"):
                    continue
                if f == target_basename:
                    candidates.append(
                        os.path.relpath(os.path.join(root, f), workspace_root)
                    )
        if candidates:
            return candidates[:5]

        # Second pass: fuzzy match on filenames
        names = []
        paths_by_name: Dict[str, List[str]] = {}
        for root, dirs, files in os.walk(workspace_root):
            for f in files:
                if not f.endswith(".mp"):
                    continue
                names.append(f)
                paths_by_name.setdefault(f, []).append(
                    os.path.relpath(os.path.join(root, f), workspace_root)
                )

        close = difflib.get_close_matches(target_basename, names, n=5, cutoff=0.6)
        for c in close:
            candidates.extend(paths_by_name.get(c, []))

        # Third pass: any files whose trailing path contains the module name segments
        if not candidates:
            seg = rel_path.replace(os.sep, "/")
            for root, dirs, files in os.walk(workspace_root):
                for f in files:
                    if not f.endswith(".mp"):
                        continue
                    p = os.path.relpath(os.path.join(root, f), workspace_root).replace(
                        "\\", "/"
                    )
                    if seg in p or os.path.splitext(p)[0].endswith(
                        os.path.splitext(target_basename)[0]
                    ):
                        candidates.append(p)
                        if len(candidates) >= 5:
                            break
                if len(candidates) >= 5:
                    break

        return candidates[:5]

    def interpret(self, program: Program):
        # Execute top-level statements and collect any async tasks returned so we can wait them
        pending = []
        global _CURRENT_INTERPRETER
        prev_interp = _get_current_interpreter()
        _CURRENT_INTERPRETER = self
        for statement in program.statements:
            try:
                res = self.execute(statement)
                if hasattr(res, "wait"):
                    pending.append(res)
            except Exception as e:
                # For runtime/import/type errors show professional traceback and stop
                if isinstance(e, (RuntimeTypeError, RuntimeError, ImportError)):
                    try:
                        self._print_traceback(e, node=statement)
                    except Exception:
                        pass
                    raise
                # other exceptions: log and continue
                error(f"Erro ao executar statement: {e}", component="interpreter")
                # traceback.print_exc()

        # Wait for any pending async tasks started at top-level
        for task in pending:
            try:
                task.wait()
            except Exception as e:
                traceback.print_exc()
                print(f"Erro em tarefa assíncrona: {e}")
        _CURRENT_INTERPRETER = prev_interp

    def execute(self, node: Any) -> Any:
        if isinstance(node, Program):
            for stmt in node.statements:
                self.execute(stmt)

        elif isinstance(node, VarDeclaration):
            # Special handling for generic types: extract type parameters and pass to constructor
            value = self.evaluate_with_generic_context(node.value, node.type_annotation)
            try:
                self.environment.define(
                    node.name, value, type_annotation=node.type_annotation
                )
            except RuntimeTypeError as rte:
                # Build a message with a small AST snippet for context
                snippet = _ast_to_source(node)
                # include interpreter traceback-like output
                raise RuntimeTypeError(f"Runtime type error:\n  {rte}\n  at: {snippet}")

        elif isinstance(node, FunctionDeclaration):
            intent = CorpLangFunction(node, self.environment)
            self.environment.define(node.name, intent)

        elif isinstance(node, ClassDeclaration):
            # collect fields and methods
            fields: Dict[str, FieldDeclaration] = {}
            methods: Dict[str, MethodDeclaration] = {}
            for member in node.body:
                if isinstance(member, FieldDeclaration):
                    fields[member.name] = member
                elif isinstance(member, MethodDeclaration):
                    methods[member.name] = member

            class_obj = ClassObject(
                node.name,
                fields,
                methods,
                extends=node.extends,
                implements=node.implements,
                is_abstract=node.is_abstract,
            )
            # store class object in environment
            self.environment.define(node.name, class_obj)

            # If parent class exists in current environment, link it for inheritance lookup
            if node.extends:
                try:
                    parent = self.environment.get(node.extends)
                    if isinstance(parent, ClassObject):
                        class_obj.parent = parent
                except Exception:
                    # parent may be defined later; leave parent as None
                    pass

            # Evaluate static field defaults now and store their values
            for fname, fdecl in class_obj.static_fields.items():
                if fdecl.value is not None:
                    try:
                        val = self.evaluate(fdecl.value)
                    except Exception:
                        val = None
                else:
                    val = None
                class_obj.static_field_values[fname] = val

        elif isinstance(node, InterfaceDeclaration):
            # At runtime interfaces have no direct behavior; register interface AST for introspection
            try:
                self.environment.define(node.name, node)
            except Exception:
                # If a type error occurs during registration, ignore to keep runtime permissive
                self.environment.variables[node.name] = node

        elif isinstance(node, Assignment):
            value = self.evaluate(node.value)
            target = node.target
            # simple variable assignment
            if isinstance(target, Identifier):
                self.environment.set(target.name, value)
            # property assignment e.g., obj.prop = value
            elif isinstance(target, PropertyAccess):
                obj = self.evaluate(target.obj)
                if isinstance(obj, InstanceObject):
                    obj.set(target.prop, value)
                elif isinstance(obj, dict):
                    obj[target.prop] = value
                else:
                    try:
                        setattr(obj, target.prop, value)
                    except Exception:
                        raise RuntimeError(
                            f"Cannot assign property '{target.prop}' on object of type {type(obj)}"
                        )
            else:
                raise RuntimeError("Invalid assignment target")

        elif isinstance(node, IfStatement):
            condition = self.evaluate(node.condition)
            if self.is_truthy(condition):
                self.execute_block(node.then_stmt)
            elif node.else_stmt:
                self.execute_block(node.else_stmt)

        elif isinstance(node, WhileStatement):
            while self.is_truthy(self.evaluate(node.condition)):
                self.execute_block(node.body)

        elif isinstance(node, ForStatement):
            # Traditional for loop: for (init; condition; update)
            # Create new environment for loop scope
            loop_env = Environment(self.environment)
            previous_env = self.environment
            self.environment = loop_env

            try:
                # Execute init statement if present
                if node.init:
                    self.execute(node.init)

                # Loop while condition is true
                while node.condition is None or self.is_truthy(
                    self.evaluate(node.condition)
                ):
                    # Execute loop body
                    self.execute_block(node.body)

                    # Execute update statement/expression if present
                    if node.update:
                        self.execute(node.update)
            finally:
                self.environment = previous_env

        elif isinstance(node, ForInStatement):
            # for (var item in collection)
            iterable = self.evaluate(node.iterable)
            loop_env = Environment(self.environment)
            previous_env = self.environment
            self.environment = loop_env

            try:
                # Handle different iterable types
                if hasattr(iterable, "keys") and callable(iterable.keys):
                    # Dict-like object, iterate over keys
                    keys = iterable.keys()
                    for key in keys:  # type: ignore
                        self.environment.define(
                            node.variable, key, node.type_annotation
                        )
                        self.execute_block(node.body)
                elif hasattr(iterable, "__iter__"):
                    # Python iterable
                    for item in iterable:  # type: ignore
                        self.environment.define(
                            node.variable, item, node.type_annotation
                        )
                        self.execute_block(node.body)
                elif isinstance(iterable, InstanceObject):
                    # Check if it's a List-like object with get() and length() methods
                    try:
                        length_method = iterable.get("length")
                        get_method = iterable.get("get")

                        if length_method and get_method:
                            # Use public API to iterate - call the CorpLangFunction methods
                            length_result = length_method.call(self, [])
                            for i in range(length_result):
                                item_result = get_method.call(self, [i])
                                self.environment.define(
                                    node.variable, item_result, node.type_annotation
                                )
                                self.execute_block(node.body)
                        else:
                            raise RuntimeError(
                                f"Object is not iterable (no get/length methods): {type(iterable)}"
                            )
                    except Exception as e:
                        raise RuntimeError(
                            f"Object does not support iteration: {type(iterable)} - {e}"
                        )
                elif hasattr(iterable, "data") and hasattr(iterable.data, "__iter__"):
                    # List-like object with data property
                    for item in iterable.data:  # type: ignore
                        self.environment.define(
                            node.variable, item, node.type_annotation
                        )
                        self.execute_block(node.body)
                else:
                    raise RuntimeError(f"Object is not iterable: {type(iterable)}")
            finally:
                self.environment = previous_env

        elif isinstance(node, ForOfStatement):
            # for (var item of collection) - iterate over values
            iterable = self.evaluate(node.iterable)
            loop_env = Environment(self.environment)
            previous_env = self.environment
            self.environment = loop_env

            try:
                # Handle different iterable types
                if hasattr(iterable, "values") and callable(iterable.values):
                    # Dict-like object, iterate over values
                    values = iterable.values()
                    for value in values:  # type: ignore
                        self.environment.define(
                            node.variable, value, node.type_annotation
                        )
                        self.execute_block(node.body)
                elif hasattr(iterable, "__iter__"):
                    # Python iterable
                    for item in iterable:  # type: ignore
                        self.environment.define(
                            node.variable, item, node.type_annotation
                        )
                        self.execute_block(node.body)
                elif isinstance(iterable, InstanceObject):
                    # Check if it's a List-like object with get() and length() methods
                    try:
                        length_method = iterable.get("length")
                        get_method = iterable.get("get")

                        if length_method and get_method:
                            # Use public API to iterate - call the CorpLangFunction methods
                            length_result = length_method.call(self, [])
                            for i in range(length_result):
                                item_result = get_method.call(self, [i])
                                self.environment.define(
                                    node.variable, item_result, node.type_annotation
                                )
                                self.execute_block(node.body)
                        else:
                            raise RuntimeError(
                                f"Object is not iterable (no get/length methods): {type(iterable)}"
                            )
                    except Exception as e:
                        raise RuntimeError(
                            f"Object does not support iteration: {type(iterable)} - {e}"
                        )
                elif hasattr(iterable, "data") and hasattr(iterable.data, "__iter__"):
                    # List-like object with data property
                    for item in iterable.data:  # type: ignore
                        self.environment.define(
                            node.variable, item, node.type_annotation
                        )
                        self.execute_block(node.body)
                else:
                    raise RuntimeError(f"Object is not iterable: {type(iterable)}")
            finally:
                self.environment = previous_env

        elif isinstance(node, TryStatement):
            self._execute_try_statement(node)

        elif isinstance(node, ThrowStatement):
            if node.expression is None:
                if not self._active_exceptions:
                    raise RuntimeError(
                        "Cannot rethrow exception: no active exception in scope"
                    )
                raise self._active_exceptions[-1]
            value = self.evaluate(node.expression)
            self._raise_runtime_exception(value, node)

        elif isinstance(node, ReturnStatement):
            value = None
            if node.value:
                value = self.evaluate(node.value)
            raise ReturnException(value)

        elif isinstance(node, DatasetOperation):
            self.execute_dataset_operation(node)

        elif isinstance(node, ModelOperation):
            self.execute_model_operation(node)

        elif isinstance(node, ImportDeclaration):
            # Resolve dotted import to file path (a.b.c -> a/b/c.mp)
            rel_path = node.name.replace(".", os.sep) + ".mp"
            # Try relative to current file dir first
            candidate = os.path.join(self.current_file_dir, rel_path)
            if not os.path.exists(candidate):
                # Fallback to project root
                candidate = rel_path

            if os.path.exists(candidate):
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        src = f.read()
                        # If the file was pasted with Markdown fences (```), strip them.
                        # Accept variants like ```lang or ```
                        src_strip = src
                        if src_strip.lstrip().startswith("```"):
                            # remove first line starting with ``` and last line ending with ```
                            parts = src_strip.splitlines()
                            # find first fence line
                            start_idx = 0
                            while start_idx < len(parts) and not parts[
                                start_idx
                            ].lstrip().startswith("```"):
                                start_idx += 1
                            end_idx = len(parts) - 1
                            while end_idx >= 0 and not parts[
                                end_idx
                            ].lstrip().startswith("```"):
                                end_idx -= 1
                            if start_idx < end_idx:
                                parts = parts[start_idx + 1 : end_idx]
                                src = "\n".join(parts)
                    lexer = Lexer(src)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    ast = parser.parse()
                    # interpret imported file in the global environment
                    prev_path = getattr(self, "current_file_path", None)
                    prev_dir = getattr(self, "current_file_dir", None)
                    self.current_file_path = os.path.abspath(candidate)
                    self.current_file_dir = os.path.dirname(self.current_file_path)
                    try:
                        self.interpret(ast)
                    finally:
                        self.current_file_path = prev_path
                        self.current_file_dir = prev_dir or os.getcwd()
                except Exception as e:
                    # Propagate import-time exceptions to abort execution
                    raise ImportError(f"Erro importando '{node.name}': {e}")
            else:
                # suggest candidates
                rel_path = node.name.replace(".", os.sep) + ".mp"
                suggestions = self._suggest_import_candidates(rel_path)
                msg = f"Módulo '{node.name}' não encontrado no path '{candidate}'"
                if suggestions:
                    msg += "\nSugestões:"
                    for s in suggestions:
                        msg += f"\n  - {s}"
                raise ImportError(msg)

        else:
            return self.evaluate(node)

    def execute_block(
        self, statements: List[Any], environment: Optional[Environment] = None
    ):
        if environment is not None:
            previous = self.environment
            self.environment = environment
        else:
            previous = None

        try:
            for stmt in statements:
                self.execute(stmt)
        finally:
            if environment is not None:
                # previous is guaranteed to be Environment when environment is not None
                self.environment = previous  # type: ignore[assignment]

    def execute_dataset_operation(self, node: DatasetOperation):
        """Executa operações específicas de dataset"""
        if node.operation == "load":
            # Simula carregamento de dataset
            source = node.params.get("source", "")
            if source.endswith(".csv"):
                # Simula dados CSV
                data = [
                    {"id": 1, "name": "João", "age": 30, "salary": 5000},
                    {"id": 2, "name": "Maria", "age": 25, "salary": 4500},
                    {"id": 3, "name": "Pedro", "age": 35, "salary": 6000},
                ]
            else:
                data = []

            self.datasets[node.target] = data
            print(f"Dataset '{node.target}' carregado com {len(data)} registros")

        elif node.operation == "save":
            if node.target in self.datasets:
                print(f"Dataset '{node.target}' salvo")
            else:
                print(f"Dataset '{node.target}' não encontrado")

        elif node.operation == "filter":
            # Implementação básica de filtro
            if node.target in self.datasets:
                print(f"Filtro aplicado ao dataset '{node.target}'")
            else:
                print(f"Dataset '{node.target}' não encontrado")

        elif node.operation == "analyze":
            if node.target in self.datasets:
                data = self.datasets[node.target]
                print(f"Análise do dataset '{node.target}':")
                print(f"- Registros: {len(data)}")
                if data:
                    print(f"- Colunas: {list(data[0].keys())}")
            else:
                print(f"Dataset '{node.target}' não encontrado")

    def execute_model_operation(self, node: ModelOperation):
        """Executa operações específicas de modelo de ML"""
        if node.operation == "create":
            model_type = node.params.get("type", "linear_regression")
            self.models[node.model_name] = {
                "type": model_type,
                "trained": False,
                "accuracy": 0.0,
            }
            print(f"Modelo '{node.model_name}' criado (tipo: {model_type})")

        elif node.operation == "train":
            if node.model_name in self.models:
                dataset = node.params.get("dataset", "")
                if dataset in self.datasets:
                    # Simula treinamento
                    self.models[node.model_name]["trained"] = True
                    self.models[node.model_name]["accuracy"] = 0.85  # Simulado
                    print(
                        f"Modelo '{node.model_name}' treinado com dataset '{dataset}'"
                    )
                    print(f"Acurácia: {self.models[node.model_name]['accuracy']:.2f}")
                else:
                    print(f"Dataset '{dataset}' não encontrado")
            else:
                print(f"Modelo '{node.model_name}' não encontrado")

        elif node.operation == "predict":
            if node.model_name in self.models:
                if self.models[node.model_name]["trained"]:
                    # Simula predição
                    input_data = node.params.get("input", {})
                    result = {"prediction": "high_value", "confidence": 0.78}
                    print(f"Predição do modelo '{node.model_name}': {result}")
                else:
                    print(f"Modelo '{node.model_name}' não foi treinado")
            else:
                print(f"Modelo '{node.model_name}' não encontrado")

    def evaluate_with_generic_context(
        self, node: Any, type_annotation: Optional[str] = None
    ) -> Any:
        """Evaluates a node with knowledge of generic type context for constructor calls."""

        alias_map = {"HashMap": "Map"}
        default_generics = {
            "List": ["any"],
            "EmbedList": ["any"],
            "Set": ["any"],
            "Map": ["any", "any"],
            "Matrix": ["any"],
        }

        def resolve_class(name: str) -> str:
            return alias_map.get(name, name)

        def has_explicit_type_args(args: List[Any], expected: int) -> bool:
            if expected == 0 or len(args) < expected:
                return False
            for index in range(expected):
                arg = args[index]
                if not isinstance(arg, Literal):
                    return False
                if not isinstance(arg.value, str):
                    return False
            return True

        if isinstance(node, NewExpression):
            resolved_class_name = resolve_class(node.class_name)

            if type_annotation and "<" in type_annotation:
                base_type = type_annotation.split("<", 1)[0].strip()
                base_type_resolved = resolve_class(base_type)

                if resolved_class_name == base_type_resolved:
                    params_part = type_annotation[
                        type_annotation.index("<") + 1 : type_annotation.rindex(">")
                    ]
                    raw_params = [
                        param.strip()
                        for param in params_part.split(",")
                        if param.strip()
                    ]

                    defaults = default_generics.get(resolved_class_name, [])
                    expected_count = len(defaults) if defaults else len(raw_params)

                    if expected_count and not has_explicit_type_args(
                        node.args, expected_count
                    ):
                        type_params = raw_params[:expected_count]
                        while len(type_params) < expected_count:
                            fallback = (
                                defaults[len(type_params)]
                                if len(defaults) > len(type_params)
                                else "any"
                            )
                            type_params.append(fallback)

                        type_args = [Literal(param) for param in type_params]
                        modified_args = type_args + node.args
                        modified_node = NewExpression(
                            node.class_name, modified_args, node.line, node.column
                        )
                        return self.evaluate(modified_node)

            defaults = default_generics.get(resolved_class_name)
            if defaults and not has_explicit_type_args(node.args, len(defaults)):
                type_args = [Literal(param) for param in defaults]
                modified_node = NewExpression(
                    node.class_name, type_args + node.args, node.line, node.column
                )
                return self.evaluate(modified_node)

        return self.evaluate(node)

    def evaluate(self, node: Any) -> Any:
        if isinstance(node, Literal):
            value = node.value
            if isinstance(value, str):
                # Replace any {expr} by parsing and evaluating the expression inside
                def replace_expr(match):
                    expr_text = match.group(1).strip()
                    try:
                        res = self._eval_interpolated_expression(expr_text)
                        return str(res)
                    except Exception:
                        # On failure keep the original placeholder
                        return match.group(0)

                value = re.sub(r"\{([^}]+)\}", replace_expr, value)  # noqa

            return value

        elif isinstance(node, Identifier):
            return self.environment.get(node.name)

        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if node.operator == "+":
                return left + right
            elif node.operator == "-":
                return left - right
            elif node.operator == "*":
                return left * right
            elif node.operator == "/":
                if right == 0:
                    raise ZeroDivisionError("Divisão por zero")
                return left / right
            elif node.operator == "%":
                return left % right
            elif node.operator == "==":
                return left == right
            elif node.operator == "!=":
                return left != right
            elif node.operator == "<":
                return left < right
            elif node.operator == ">":
                return left > right
            elif node.operator == "<=":
                return left <= right
            elif node.operator == ">=":
                return left >= right
            elif node.operator == "and":
                return self.is_truthy(left) and self.is_truthy(right)
            elif node.operator == "or":
                return self.is_truthy(left) or self.is_truthy(right)

        elif isinstance(node, UnaryOp):
            operand = self.evaluate(node.operand)

            if node.operator == "-":
                return -operand
            elif node.operator == "not":
                return not self.is_truthy(operand)

        elif isinstance(node, FunctionCall):
            # callee can be an expression (Identifier, PropertyAccess, etc.)
            # Evaluate callee to get the callable
            # Special-case: super(...) -> invoke parent constructor
            if isinstance(node.callee, SuperExpression):
                # resolve 'this'
                try:
                    this_obj = self.environment.get("this")
                except Exception:
                    raise RuntimeError("'super' used outside of method")
                if not isinstance(this_obj, InstanceObject):
                    raise RuntimeError("'super' used outside of instance context")
                cls = this_obj.class_obj
                parent = cls.parent
                if not parent:
                    raise RuntimeError("No parent class for 'super'")
                # find constructor on parent
                pmdecl = parent.get_instance_method("constructor")
                if pmdecl is None:
                    return None
                func = CorpLangFunction(
                    pmdecl,
                    self.globals,
                    bound_this=this_obj,
                    bound_name=f"{parent.name}.constructor",
                )
                args = [self.evaluate(arg) for arg in node.args]
                return func.call(self, args)

            if isinstance(node.callee, Identifier):
                try:
                    intent = self.environment.get(node.callee.name)
                except Exception:
                    intent = self.globals.variables.get(node.callee.name)
            else:
                intent = self.evaluate(node.callee)

            args = [self.evaluate(arg) for arg in node.args]

            if callable(intent):
                return intent(*args)
            elif isinstance(intent, CorpLangFunction):
                return intent.call(self, args)
            elif (
                intent is not None
                and hasattr(intent, "call")
                and callable(getattr(intent, "call"))
            ):
                # Handle BoundPrototypeMethod and other objects with call method
                return intent.call(self, args)
            else:
                raise TypeError(
                    f"'{getattr(node.callee,'name',str(node.callee))}' não é uma função"
                )
        elif isinstance(node, DatasetOperation):
            # Execute dataset operation and return dataset object if available
            self.execute_dataset_operation(node)
            return self.datasets.get(node.target)

        elif isinstance(node, ModelOperation):
            self.execute_model_operation(node)
            return self.models.get(node.model_name)
        elif isinstance(node, JsonObject):
            # Evaluate object literal values which may be expressions (AST nodes)
            result: Dict[str, Any] = {}
            for k, v in node.value.items():
                # If value is an AST node, evaluate it; otherwise keep raw
                try:
                    val = self.evaluate(v)
                except Exception:
                    val = v
                result[k] = val
            return result

        elif isinstance(node, PropertyAccess):
            obj = self.evaluate(node.obj)
            # support super.method -> if node.obj is a SuperExpression, resolve on parent
            if isinstance(node.obj, SuperExpression):
                # get current this
                try:
                    this_obj = self.environment.get("this")
                except Exception:
                    raise RuntimeError("'super' used outside of method")
                if not isinstance(this_obj, InstanceObject):
                    raise RuntimeError("'super' used outside of instance context")
                cls = this_obj.class_obj
                parent = cls.parent
                if not parent:
                    raise RuntimeError("No parent class for 'super'")
                # look for instance method on parent
                mdecl = parent.get_instance_method(node.prop)
                if mdecl is None:
                    raise AttributeError(f"Parent has no method '{node.prop}'")
                return CorpLangFunction(
                    mdecl,
                    self.globals,
                    bound_this=this_obj,
                    bound_name=f"{parent.name}.{mdecl.name}",
                )
            # If LHS is a ClassObject, allow static access
            if isinstance(obj, ClassObject):
                # static field value
                val = obj.get_static_field_value(node.prop)
                if val is not None:
                    return val
                # static method
                mdecl = obj.get_static_method(node.prop)
                if mdecl is not None:
                    return CorpLangFunction(
                        mdecl,
                        self.globals,
                        bound_this=None,
                        bound_name=f"{obj.name}.{mdecl.name}",
                    )
            # If our InstanceObject, use its get
            if isinstance(obj, InstanceObject):
                return obj.get(node.prop)
            if isinstance(obj, dict):
                return obj.get(node.prop)

            # Check for prototype methods/properties on primitive types
            obj_type = _literal_type_name(obj)
            if (
                obj_type in self.prototype_methods
                and node.prop in self.prototype_methods[obj_type]
            ):
                method_or_value = self.prototype_methods[obj_type][node.prop]

                # Special handling for properties (functions that take only the object)
                if node.prop == "length":
                    return method_or_value(obj)

                # Return a bound method that includes the object as first argument
                class BoundPrototypeMethod:
                    def __init__(self, method, bound_obj):
                        self.method = method
                        self.bound_obj = bound_obj

                    def __call__(self, *args):
                        return self.method(self.bound_obj, *args)

                    # Make it work with CorpLangFunction.call interface
                    def call(self, interpreter, args):
                        return self.method(self.bound_obj, *args)

                return BoundPrototypeMethod(method_or_value, obj)

            # fallback: try attribute access on Python objects
            try:
                return getattr(obj, node.prop)
            except Exception:
                return None

        elif isinstance(node, IndexAccess):
            obj = self.evaluate(node.obj)
            idx = self.evaluate(node.index)
            # list-like
            if isinstance(obj, list) and isinstance(idx, int):
                try:
                    return obj[idx]
                except Exception:
                    return None
            # dict-like
            if isinstance(obj, dict):
                return obj.get(idx)
            # fallback: try __getitem__
            try:
                return obj[idx]
            except Exception:
                return None

        elif isinstance(node, JsonArray):
            # Evaluate each element if it's an AST node
            out: List[Any] = []
            for el in node.value:
                try:
                    out.append(self.evaluate(el))
                except Exception:
                    out.append(el)
            return out

        elif isinstance(node, NewExpression):
            # create a new instance of a class
            class_obj = self.environment.get(node.class_name)
            # If the name points to a runtime ClassObject (MF07 class), handle as before
            if isinstance(class_obj, ClassObject):
                if getattr(class_obj, "is_abstract", False):
                    raise RuntimeError(
                        f"Cannot instantiate abstract class '{class_obj.name}'"
                    )
                inst = InstanceObject(class_obj, self)
            # If it's a native callable (Python class/factory), call it and return result
            elif callable(class_obj):
                args_native = [self.evaluate(a) for a in node.args]
                try:
                    return class_obj(*args_native)
                except TypeError:
                    # fallback: call without args
                    return class_obj()
            else:
                raise RuntimeError(f"'{node.class_name}' is not a class")

            # initialize fields with defaults if any (include inherited fields)
            cur_cls = class_obj
            # walk inheritance chain from root to current so parent defaults apply first
            chain: List[ClassObject] = []
            while cur_cls:
                chain.append(cur_cls)
                cur_cls = cur_cls.parent
            # chain currently is [class_obj, parent, grandparent,...]; reverse to init parents first
            for c in reversed(chain):
                for fname, fdecl in c.instance_fields.items():
                    if fdecl.value is not None:
                        try:
                            inst._fields[fname] = self.evaluate(fdecl.value)
                        except Exception:
                            inst._fields[fname] = None
                    else:
                        inst._fields[fname] = None

            # If constructor method exists, call it
            if "constructor" in class_obj.instance_methods:
                ctor = inst.get("constructor")
                args = [self.evaluate(a) for a in node.args]
                # ctor is a bound CorpLangFunction; call it
                if isinstance(ctor, CorpLangFunction):
                    ctor.call(self, args)
                else:
                    # fallback: callable
                    ctor(*args)
                # return the created instance
                return inst

        elif isinstance(node, SuperExpression):
            # bare 'super' used as expression (e.g., super() or super.method)
            return node

        elif isinstance(node, ThisExpression):
            # 'this' is stored in current environment (bound by method invocation)
            try:
                return self.environment.get("this")
            except Exception:
                return None

        elif isinstance(node, NullLiteral):
            return None
        elif isinstance(node, Await):
            # Evaluate expression and wait if AsyncTask
            value = self.evaluate(node.expression)
            # If it's an AsyncTask, wait for result
            if hasattr(value, "wait"):
                return value.wait()
            return value

        elif isinstance(node, LambdaExpression):
            # Convert lambda to a CorpLangFunction
            # Create a temporary FunctionDeclaration with a unique name
            temp_name = f"<lambda_{id(node)}>"
            temp_func_decl = FunctionDeclaration(
                name=temp_name,
                params=node.params,
                body=node.body,
                is_async=False,
                param_types=node.param_types,
                param_defaults=getattr(node, "param_defaults", None),
                return_type=node.return_type,
                line=node.line,
                column=node.column,
            )
            return CorpLangFunction(temp_func_decl, self.environment)

        else:
            raise RuntimeError(f"Tipo de nó não suportado: {type(node)}")

    def is_truthy(self, value: Any) -> bool:
        """Determina se um valor é verdadeiro"""
        if value is None or value is False:
            return False
        elif value == 0 or value == "":
            return False
        return True


__all__ = [
    "Interpreter",
    "Environment",
    "AsyncTask",
    "CorpLangFunction",
    "ReturnException",
]
