from typing import List, Optional, Any, Dict, cast
from .lexer import Token, TokenType
from .lang_ast import (
    Program,
    ASTNode,
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
    IndexAccess,
    IfStatement,
    WhileStatement,
    ForStatement,
    ForInStatement,
    ForOfStatement,
    CatchClause,
    TryStatement,
    ThrowStatement,
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
    SuperExpression,
    InterfaceDeclaration,
)
import json


class SyntaxException(Exception):
    def __init__(self, line, column, position, expected, found):
        message = (
            f"Syntax error at line {line}, column {column} (offset {position}): "
            f"expected token of type '{expected}', but found '{found}'."
        )
        super().__init__(message)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [
            t for t in tokens if t.type != TokenType.NEWLINE
        ]  # Ignore newlines for now
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def peek(self, offset: int = 1) -> Optional[Token]:
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def expect(self, token_type: TokenType) -> Token:
        if not self.current_token or self.current_token.type != token_type:
            raise SyntaxException(
                line=self.current_token.line if self.current_token else -1,
                column=self.current_token.column if self.current_token else -1,
                position=self.pos,
                expected=token_type.name,
                found=self.current_token.type.name if self.current_token else "EOF",
            )
        token = self.current_token
        self.advance()
        return token

    def parse(self) -> Program:
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self) -> Optional[Any]:
        if not self.current_token:
            return None
        # Support 'async intent' at statement start
        if self.current_token.type == TokenType.ASYNC:
            return self.parse_function_declaration()
        if self.current_token.type == TokenType.IMPORT:
            return self.parse_import_declaration()
        # handle 'abstract class' top-level
        if self.current_token.type == TokenType.ABSTRACT:
            return self.parse_class_declaration()
        # Support optional 'async' before intent
        if self.current_token.type == TokenType.ASYNC:
            # leave handling to parse_function_declaration which will check for ASYNC
            return self.parse_function_declaration()

        if self.current_token.type == TokenType.VAR:
            return self.parse_var_declaration()
        elif self.current_token.type == TokenType.CLASS:
            return self.parse_class_declaration()
        elif self.current_token.type == TokenType.INTERFACE:
            return self.parse_interface_declaration()
        elif self.current_token.type == TokenType.FUNCTION:
            return self.parse_function_declaration()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif self.current_token.type == TokenType.DATASET:
            return self.parse_dataset_operation()
        elif self.current_token.type == TokenType.MODEL:
            return self.parse_model_operation()
        elif self.current_token.type == TokenType.TRY:
            return self.parse_try_statement()
        elif self.current_token.type == TokenType.THROW:
            return self.parse_throw_statement()
        elif self.current_token.type == TokenType.IDENTIFIER:
            peek_token = self.peek()
            if peek_token and peek_token.type == TokenType.ASSIGN:
                return self.parse_assignment()
            else:
                expr = self.parse_expression()
                if (
                    self.current_token
                    and self.current_token.type == TokenType.SEMICOLON
                ):
                    self.advance()
                return expr
        elif self.current_token.type == TokenType.THIS:
            # Could be a property assignment like: this.x = y;
            # Peek ahead to see if after optional .prop chain there's an ASSIGN
            scan_pos = self.pos
            scan_tok = self.current_token
            advance_ok = True
            scan_depth = 0
            # consume THIS
            scan_pos += 1
            while (
                scan_pos < len(self.tokens)
                and self.tokens[scan_pos].type == TokenType.DOT
                and scan_depth < 10  # prevent infinite loop
            ):
                scan_pos += 1
                scan_depth += 1
                if (
                    scan_pos < len(self.tokens)
                    and self.tokens[scan_pos].type == TokenType.IDENTIFIER
                ):
                    scan_pos += 1
                else:
                    advance_ok = False
                    break
            if (
                advance_ok
                and scan_pos < len(self.tokens)
                and self.tokens[scan_pos].type == TokenType.ASSIGN
            ):
                return self.parse_assignment()
            else:
                # Se não é assignment, processa como expressão normal
                expr = self.parse_expression()
                if (
                    self.current_token
                    and self.current_token.type == TokenType.SEMICOLON
                ):
                    self.advance()
                return expr
        else:
            expr = self.parse_expression()
            if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                self.advance()
            return expr

    def parse_var_declaration(self) -> VarDeclaration:
        self.expect(TokenType.VAR)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        # optional type annotation: : Type
        type_ann = None
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
            type_ann = self.parse_type_annotation()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        # convert TypeAnnotation object to string to match VarDeclaration signature (str | None)
        type_str = self._format_type_annotation(type_ann)
        return VarDeclaration(
            name,
            value,
            type_annotation=type_str,
            line=name_token.line,
            column=name_token.column,
        )

    def parse_type_annotation(self):
        # parse base IDENTIFIER and optional generic args: IDENTIFIER ('<' Type (',' Type)* '>')?
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxException(
                self.current_token.line if self.current_token else -1,
                self.current_token.column if self.current_token else -1,
                self.pos,
                "IDENTIFIER",
                self.current_token.type.name if self.current_token else "EOF",
            )
        base = self.current_token.value
        self.advance()
        args = None
        if self.current_token and self.current_token.type in (
            TokenType.LESS_THAN,
            TokenType.LBRACKET,
        ):
            start_token = self.current_token.type
            closing = (
                TokenType.GREATER_THAN
                if start_token == TokenType.LESS_THAN
                else TokenType.RBRACKET
            )
            # consume start token
            self.advance()
            args = []
            while True:
                arg = self.parse_type_annotation()
                args.append(arg)
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    continue
                break
            self.expect(closing)
        from .lang_ast import TypeAnnotation

        return TypeAnnotation(base, args)

    def _format_type_annotation(self, ta) -> Optional[str]:
        """Convert a TypeAnnotation object (or nested ones) into a string representation,
        returning None if ta is None. This ensures type_annotation passed to AST nodes
        that expect a 'str | None' receives the correct type."""
        if ta is None:
            return None
        # Try to read .base and .args to build a textual representation
        base = getattr(ta, "base", None)
        args = getattr(ta, "args", None)
        if not args:
            return base
        parts = []
        for a in args:
            parts.append(self._format_type_annotation(a))
        return f"{base}<{', '.join(parts)}>"

    def parse_function_declaration(self) -> FunctionDeclaration:
        # intent ::= ('async')? 'intent' IDENT '(' parameters? ')' (':' Type)? '{' declaration* '}'
        is_async = False
        if self.current_token and self.current_token.type == TokenType.ASYNC:
            is_async = True
            self.advance()

        self.expect(TokenType.FUNCTION)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        self.expect(TokenType.LPAREN)

        params = []
        param_types: Dict[str, Optional[str]] = {}
        param_defaults: Dict[str, Any] = {}
        if not (self.current_token and self.current_token.type == TokenType.RPAREN):
            while True:
                pname = self.expect(TokenType.IDENTIFIER).value
                ptype = None
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
                    # accept a full TypeAnnotation (supports generics) and format it to string
                    ptype = self._format_type_annotation(self.parse_type_annotation())
                # optional default value: '=' expression
                pdefault = None
                if self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.advance()
                    pdefault = self.parse_expression()
                params.append(pname)
                param_types[pname] = ptype
                if pdefault is not None:
                    param_defaults[pname] = pdefault
                if not (
                    self.current_token and self.current_token.type == TokenType.COMMA
                ):
                    break
                self.advance()

        self.expect(TokenType.RPAREN)

        # optional return type before the body: ':' TypeAnnotation
        return_type = None
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
            return_type = self._format_type_annotation(self.parse_type_annotation())

        self.expect(TokenType.LBRACE)

        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        self.expect(TokenType.RBRACE)

        fd = FunctionDeclaration(
            name,
            params,
            body,
            is_async=is_async,
            line=name_token.line,
            column=name_token.column,
        )
        fd.param_types = param_types
        fd.param_defaults = param_defaults if param_defaults else None
        fd.return_type = return_type
        return fd

    def parse_import_declaration(self) -> ImportDeclaration:
        self.expect(TokenType.IMPORT)
        # Parse dotted name
        parts = [self.expect(TokenType.IDENTIFIER).value]
        while self.current_token and self.current_token.type == TokenType.DOT:
            self.advance()
            parts.append(self.expect(TokenType.IDENTIFIER).value)
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ImportDeclaration(".".join(parts))

    def parse_assignment(self) -> Assignment:
        # Support assignments to identifiers or property access (e.g., this.x = ...)
        # Parse left-hand side as primary expression (IDENTIFIER or THIS optionally with .prop)
        if not self.current_token:
            raise SyntaxException(-1, -1, self.pos, "IDENTIFIER or THIS", "EOF")

        if self.current_token.type == TokenType.IDENTIFIER:
            left_token = self.current_token
            self.advance()
            node_left = Identifier(
                left_token.value, line=left_token.line, column=left_token.column
            )
            # handle chained property access
            while self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()
                prop = self.expect(TokenType.IDENTIFIER)
                node_left = PropertyAccess(
                    node_left, prop.value, line=prop.line, column=prop.column
                )
        elif self.current_token.type == TokenType.THIS:
            t = self.current_token
            self.advance()
            node_left = ThisExpression(line=t.line, column=t.column)
            while self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()
                prop = self.expect(TokenType.IDENTIFIER)
                node_left = PropertyAccess(
                    node_left, prop.value, line=prop.line, column=prop.column
                )
        else:
            raise SyntaxException(
                self.current_token.line if self.current_token else -1,
                self.current_token.column if self.current_token else -1,
                self.pos,
                "IDENTIFIER or THIS",
                self.current_token.type.name if self.current_token else "EOF",
            )

        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return Assignment(node_left, value)

    def parse_class_declaration(self) -> Any:
        # class declaration: ('abstract')? 'class' IDENT (extends IDENT)? (implements IDENT(,IDENT)*)? '{' members '}'
        class_token = self.current_token
        is_abstract = False
        # optional abstract before class
        if self.current_token and self.current_token.type == TokenType.ABSTRACT:
            is_abstract = True
            self.advance()
        self.expect(TokenType.CLASS)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        # Parse generic type parameters: class Name<T, U, V>
        generic_params = None
        if self.current_token and self.current_token.type == TokenType.LESS_THAN:
            self.advance()  # consume '<'
            generic_params = []
            while True:
                if (
                    self.current_token
                    and self.current_token.type == TokenType.IDENTIFIER
                ):
                    generic_params.append(self.current_token.value)
                    self.advance()
                else:
                    raise SyntaxException(
                        self.current_token.line if self.current_token else -1,
                        self.current_token.column if self.current_token else -1,
                        self.pos,
                        "IDENTIFIER",
                        self.current_token.type.name if self.current_token else "EOF",
                    )

                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()  # consume ','
                    continue
                break
            self.expect(TokenType.GREATER_THAN)

        extends = None
        implements = None

        if self.current_token and self.current_token.type == TokenType.EXTENDS:
            self.advance()
            extends = self.expect(TokenType.IDENTIFIER).value

        if self.current_token and self.current_token.type == TokenType.IMPLEMENTS:
            self.advance()
            impls = []
            while True:
                impls.append(self.expect(TokenType.IDENTIFIER).value)
                if not (
                    self.current_token and self.current_token.type == TokenType.COMMA
                ):
                    break
                self.advance()
            implements = impls

        self.expect(TokenType.LBRACE)
        body: List[Any] = []
        loop_count = 0
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            loop_count += 1
            if loop_count > 50:  # Increased limit but still safe
                raise SyntaxException(
                    self.current_token.line if self.current_token else -1,
                    self.current_token.column if self.current_token else -1,
                    self.pos,
                    "RBRACE or valid class member",
                    f"infinite loop detected at token {self.current_token.type.name if self.current_token else 'EOF'}",
                )

            # modifiers
            modifiers = []
            while self.current_token and self.current_token.type in (
                TokenType.STATIC,
                TokenType.PRIVATE,
                TokenType.PUBLIC,
                TokenType.ABSTRACT,
                TokenType.ASYNC,
            ):
                modifiers.append(self.current_token.type)
                self.advance()

            if self.current_token and self.current_token.type == TokenType.FUNCTION:
                # parse method inside class
                self.expect(TokenType.FUNCTION)
                mname_token = self.expect(TokenType.IDENTIFIER)
                mname = mname_token.value
                self.expect(TokenType.LPAREN)
                params = []
                param_types: Dict[str, Optional[str]] = {}
                param_defaults: Dict[str, Any] = {}
                if not (
                    self.current_token and self.current_token.type == TokenType.RPAREN
                ):
                    while True:
                        pname = self.expect(TokenType.IDENTIFIER).value
                        ptype = None
                        if (
                            self.current_token
                            and self.current_token.type == TokenType.COLON
                        ):
                            self.advance()
                            ptype = self._format_type_annotation(
                                self.parse_type_annotation()
                            )
                        pdefault = None
                        if (
                            self.current_token
                            and self.current_token.type == TokenType.ASSIGN
                        ):
                            self.advance()
                            pdefault = self.parse_expression()
                        params.append(pname)
                        param_types[pname] = ptype
                        if pdefault is not None:
                            param_defaults[pname] = pdefault
                        if not (
                            self.current_token
                            and self.current_token.type == TokenType.COMMA
                        ):
                            break
                        self.advance()
                self.expect(TokenType.RPAREN)
                return_type = None
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
                    return_type = self._format_type_annotation(
                        self.parse_type_annotation()
                    )

                self.expect(TokenType.LBRACE)
                body_stmts: List[Any] = []
                method_stmt_count = 0
                while (
                    self.current_token and self.current_token.type != TokenType.RBRACE
                ):
                    method_stmt_count += 1
                    if method_stmt_count > 100:  # Safety limit
                        raise SyntaxException(
                            self.current_token.line if self.current_token else -1,
                            self.current_token.column if self.current_token else -1,
                            self.pos,
                            "RBRACE",
                            f"too many statements in method {mname}",
                        )
                    stmt = self.parse_statement()
                    if stmt:
                        body_stmts.append(stmt)
                self.expect(TokenType.RBRACE)

                method_node = MethodDeclaration(
                    mname,
                    params,
                    body_stmts,
                    is_static=TokenType.STATIC in modifiers,
                    is_private=TokenType.PRIVATE in modifiers,
                    is_abstract=TokenType.ABSTRACT in modifiers,
                    line=mname_token.line,
                    column=mname_token.column,
                )
                method_node.param_types = param_types
                method_node.param_defaults = param_defaults if param_defaults else None
                method_node.return_type = return_type
                body.append(method_node)
            else:
                # field: accept either `var name: Type = expr;` or `name: Type = expr;`
                if self.current_token and self.current_token.type == TokenType.VAR:
                    # var-style field declaration inside class
                    self.advance()
                    ftoken = self.expect(TokenType.IDENTIFIER)
                    fname = ftoken.value
                    ftype = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COLON
                    ):
                        self.advance()
                        ftype = self._format_type_annotation(
                            self.parse_type_annotation()
                        )
                    fvalue = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.ASSIGN
                    ):
                        self.advance()
                        fvalue = self.parse_expression()
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.SEMICOLON
                    ):
                        self.advance()

                    field_node = FieldDeclaration(
                        fname,
                        fvalue,
                        is_private=TokenType.PRIVATE in modifiers,
                        is_static=TokenType.STATIC in modifiers,
                        type_annotation=ftype,
                        line=ftoken.line,
                        column=ftoken.column,
                    )
                    body.append(field_node)
                elif (
                    self.current_token
                    and self.current_token.type == TokenType.IDENTIFIER
                ):
                    # identifier-style field declaration
                    ftoken = self.expect(TokenType.IDENTIFIER)
                    fname = ftoken.value
                    ftype = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COLON
                    ):
                        self.advance()
                        ftype = self._format_type_annotation(
                            self.parse_type_annotation()
                        )
                    fvalue = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.ASSIGN
                    ):
                        self.advance()
                        fvalue = self.parse_expression()
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.SEMICOLON
                    ):
                        self.advance()

                    field_node = FieldDeclaration(
                        fname,
                        fvalue,
                        is_private=TokenType.PRIVATE in modifiers,
                        is_static=TokenType.STATIC in modifiers,
                        type_annotation=ftype,
                        line=ftoken.line,
                        column=ftoken.column,
                    )
                    body.append(field_node)
                else:
                    # Token inesperado - pular para evitar loop infinito
                    raise SyntaxException(
                        self.current_token.line if self.current_token else -1,
                        self.current_token.column if self.current_token else -1,
                        self.pos,
                        "FUNCTION, VAR, or IDENTIFIER",
                        self.current_token.type.name if self.current_token else "EOF",
                    )

        self.expect(TokenType.RBRACE)
        token_for_pos = class_token if class_token is not None else name_token
        return ClassDeclaration(
            name,
            body,
            extends=extends,
            implements=implements,
            is_abstract=is_abstract,
            generic_params=generic_params,
            line=token_for_pos.line,
            column=token_for_pos.column,
        )

    def parse_interface_declaration(self) -> Any:
        token = self.current_token
        self.expect(TokenType.INTERFACE)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        self.expect(TokenType.LBRACE)
        methods: List[Any] = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            self.expect(TokenType.FUNCTION)
            mname_token = self.expect(TokenType.IDENTIFIER)
            mname = mname_token.value
            self.expect(TokenType.LPAREN)
            params = []
            param_types: Dict[str, Optional[str]] = {}
            if not (self.current_token and self.current_token.type == TokenType.RPAREN):
                while True:
                    pname = self.expect(TokenType.IDENTIFIER).value
                    ptype = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COLON
                    ):
                        self.advance()
                        ptype = self._format_type_annotation(
                            self.parse_type_annotation()
                        )
                    params.append(pname)
                    param_types[pname] = ptype
                    if not (
                        self.current_token
                        and self.current_token.type == TokenType.COMMA
                    ):
                        break
                    self.advance()
            self.expect(TokenType.RPAREN)
            return_type = None
            if self.current_token and self.current_token.type == TokenType.COLON:
                self.advance()
                return_type = self._format_type_annotation(self.parse_type_annotation())

            # optionally accept empty body braces for compatibility
            if self.current_token and self.current_token.type == TokenType.LBRACE:
                self.advance()
                while (
                    self.current_token and self.current_token.type != TokenType.RBRACE
                ):
                    self.advance()
                self.expect(TokenType.RBRACE)

            m = MethodDeclaration(
                mname,
                params,
                [],
                is_abstract=True,
                param_types=param_types,
                return_type=return_type,
                line=mname_token.line,
                column=mname_token.column,
            )
            methods.append(m)

        self.expect(TokenType.RBRACE)
        token_for_pos = token if token is not None else name_token
        return InterfaceDeclaration(
            name, methods, line=token_for_pos.line, column=token_for_pos.column
        )

    def parse_if_statement(self) -> IfStatement:
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        then_stmt: List[ASTNode] = []
        if self.current_token and self.current_token.type == TokenType.LBRACE:
            self.expect(TokenType.LBRACE)
            while self.current_token and self.current_token.type != TokenType.RBRACE:
                stmt = self.parse_statement()
                if stmt:
                    then_stmt.append(stmt)
            self.expect(TokenType.RBRACE)
        else:
            stmt = self.parse_statement()
            if stmt:
                then_stmt.append(stmt)

        else_stmt = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            if self.current_token and self.current_token.type == TokenType.IF:
                nested_if = self.parse_if_statement()
                else_stmt = [cast(ASTNode, nested_if)]
            else:
                else_stmt = []
                if self.current_token and self.current_token.type == TokenType.LBRACE:
                    self.expect(TokenType.LBRACE)
                    while (
                        self.current_token
                        and self.current_token.type != TokenType.RBRACE
                    ):
                        stmt = self.parse_statement()
                        if stmt:
                            else_stmt.append(stmt)
                    self.expect(TokenType.RBRACE)
                else:
                    stmt = self.parse_statement()
                    if stmt:
                        else_stmt.append(stmt)

        return IfStatement(condition, then_stmt, else_stmt)

    def parse_while_statement(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)

        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        self.expect(TokenType.RBRACE)
        return WhileStatement(condition, body)

    def parse_for_statement(self):
        """Parse various forms of for loops"""
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)

        # Check for different for loop patterns
        # Lookahead to determine loop type
        checkpoint_pos = self.pos
        checkpoint_token = self.current_token

        # Look for for-in: for (var item in iterable)
        # Look for for-of: for (var item of iterable)
        if (
            self.current_token
            and self.current_token.type == TokenType.VAR
            and self.peek(2)
            and self.peek(3)
        ):
            second = self.peek()  # identifier
            third = self.peek(2)  # should be IN or OF
            if (
                second
                and second.type == TokenType.IDENTIFIER
                and third
                and third.type in [TokenType.IN, TokenType.OF]
            ):
                # It's for-in or for-of
                if third.type == TokenType.IN:
                    return self.parse_for_in_statement()
                else:  # TokenType.OF
                    return self.parse_for_of_statement()

        # Reset position for traditional for loop parsing
        self.pos = checkpoint_pos
        self.current_token = checkpoint_token

        # Traditional for loop: for (init; condition; update)
        init = None
        if self.current_token and self.current_token.type != TokenType.SEMICOLON:
            if self.current_token.type == TokenType.VAR:
                # Parse var declaration without consuming semicolon
                self.expect(TokenType.VAR)
                name_token = self.expect(TokenType.IDENTIFIER)
                name = name_token.value
                # optional type annotation: : Type
                type_ann = None
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
                    type_ann = self.parse_type_annotation()
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                # convert TypeAnnotation object to string
                type_str = self._format_type_annotation(type_ann)
                init = VarDeclaration(name, value, type_annotation=type_str)
            else:
                init = self.parse_expression()

        self.expect(TokenType.SEMICOLON)

        condition = None
        if self.current_token and self.current_token.type != TokenType.SEMICOLON:
            condition = self.parse_expression()

        self.expect(TokenType.SEMICOLON)

        update = None
        if self.current_token and self.current_token.type != TokenType.RPAREN:
            # In the update part of for loop, we can have assignments or expressions
            # Try assignment first, then fallback to expression
            next_token = self.peek()
            if (
                self.current_token
                and self.current_token.type == TokenType.IDENTIFIER
                and next_token
                and next_token.type == TokenType.ASSIGN
            ):
                # It's an assignment: identifier = expression
                identifier_token = self.current_token
                target = Identifier(
                    identifier_token.value,
                    line=identifier_token.line,
                    column=identifier_token.column,
                )
                self.advance()  # consume identifier
                assign_token = self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                update = Assignment(
                    target, value, line=assign_token.line, column=assign_token.column
                )
            else:
                update = self.parse_expression()

        self.expect(TokenType.RPAREN)
        body = self.parse_block_body()

        return ForStatement(init, condition, update, body)

    def parse_for_in_statement(self):
        """Parse for-in statement: for (var item in iterable)"""
        # We're already after FOR and LPAREN
        self.expect(TokenType.VAR)
        name_token = self.expect(TokenType.IDENTIFIER)
        variable = name_token.value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.RPAREN)
        body = self.parse_block_body()

        return ForInStatement(variable, iterable, body)

    def parse_for_of_statement(self):
        """Parse for-of statement: for (var item of iterable)"""
        # We're already after FOR and LPAREN
        self.expect(TokenType.VAR)
        name_token = self.expect(TokenType.IDENTIFIER)
        variable = name_token.value
        self.expect(TokenType.OF)
        iterable = self.parse_expression()
        self.expect(TokenType.RPAREN)
        body = self.parse_block_body()

        return ForOfStatement(variable, iterable, body)

    def parse_try_statement(self) -> TryStatement:
        try_token = self.expect(TokenType.TRY)
        try_block = self.parse_block_body()

        catch_clauses: List[CatchClause] = []
        while self.current_token and self.current_token.type == TokenType.CATCH:
            catch_clauses.append(self.parse_catch_clause())

        finally_block = None
        if self.current_token and self.current_token.type == TokenType.FINALLY:
            finally_block = self.parse_finally_clause()

        if not catch_clauses and finally_block is None:
            found = self.current_token.type.name if self.current_token else "EOF"
            raise SyntaxException(
                try_token.line,
                try_token.column,
                self.pos,
                "CATCH or FINALLY",
                found,
            )

        return TryStatement(
            try_block,
            catch_clauses,
            finally_block,
            line=try_token.line,
            column=try_token.column,
        )

    def parse_catch_clause(self) -> CatchClause:
        catch_token = self.expect(TokenType.CATCH)
        self.expect(TokenType.LPAREN)

        exception_type: Optional[str] = None
        exception_var: Optional[str] = None

        if self.current_token and self.current_token.type != TokenType.RPAREN:
            first_token = self.expect(TokenType.IDENTIFIER)
            parts = [first_token.value]

            while self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()
                part_token = self.expect(TokenType.IDENTIFIER)
                parts.append(part_token.value)

            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                exception_type = ".".join(parts)
                exception_var = self.current_token.value
                self.advance()
            else:
                if len(parts) == 1:
                    exception_var = parts[0]
                else:
                    exception_type = ".".join(parts)

        self.expect(TokenType.RPAREN)
        body = self.parse_block_body()

        return CatchClause(
            exception_type,
            exception_var,
            body,
            line=catch_token.line,
            column=catch_token.column,
        )

    def parse_finally_clause(self) -> List[ASTNode]:
        self.expect(TokenType.FINALLY)
        return self.parse_block_body()

    def parse_throw_statement(self) -> ThrowStatement:
        throw_token = self.expect(TokenType.THROW)
        expression = None
        if self.current_token and self.current_token.type not in (
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.CATCH,
            TokenType.FINALLY,
        ):
            expression = self.parse_expression()
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ThrowStatement(
            expression, line=throw_token.line, column=throw_token.column
        )

    def parse_block_body(self):
        """Helper to parse { statements } block"""
        self.expect(TokenType.LBRACE)
        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        return body

    def parse_return_statement(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)
        value = None
        if self.current_token and self.current_token.type not in [
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.EOF,
        ]:
            value = self.parse_expression()
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ReturnStatement(value)

    def parse_dataset_operation(self) -> DatasetOperation:
        self.expect(TokenType.DATASET)
        operation = self.expect(TokenType.IDENTIFIER).value
        target = self.expect(TokenType.IDENTIFIER).value

        params = {}
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            # Parse parameters (simplified)
            while self.current_token and self.current_token.type != TokenType.RPAREN:
                if self.current_token.type == TokenType.STRING:
                    params["source"] = self.current_token.value
                    self.advance()
                elif self.current_token.type == TokenType.IDENTIFIER:
                    key = self.current_token.value
                    self.advance()
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.ASSIGN
                    ):
                        self.advance()
                        if self.current_token.type in (
                            TokenType.STRING,
                            TokenType.NUMBER,
                            TokenType.OBJECT,
                            TokenType.ARRAY,
                            TokenType.IDENTIFIER,
                        ):
                            params[key] = self.current_token.value
                            self.advance()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RPAREN)

        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return DatasetOperation(operation, target, params)

    def parse_model_operation(self) -> ModelOperation:
        self.expect(TokenType.MODEL)
        # operation may be an identifier or a keyword token like TRAIN/PREDICT/ANALYZE
        if self.current_token and self.current_token.type in (
            TokenType.IDENTIFIER,
            TokenType.TRAIN,
            TokenType.PREDICT,
            TokenType.ANALYZE,
        ):
            operation = self.current_token.value
            self.advance()
        else:
            raise SyntaxException(
                self.current_token.line if self.current_token else -1,
                self.current_token.column if self.current_token else -1,
                self.pos,
                "IDENTIFIER or model operation",
                self.current_token.type.name if self.current_token else "EOF",
            )
        model_name = ""
        params = {}
        # model create clf; or model train clf (dataset="users")
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            model_name = self.current_token.value
            self.advance()

        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            while self.current_token and self.current_token.type != TokenType.RPAREN:
                # Key could be IDENTIFIER or DATASET keyword etc.
                if self.current_token.type in (
                    TokenType.IDENTIFIER,
                    TokenType.DATASET,
                    TokenType.MODEL,
                ):
                    key = self.current_token.value
                    self.advance()
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.ASSIGN
                    ):
                        self.advance()
                        if self.current_token.type in (
                            TokenType.STRING,
                            TokenType.NUMBER,
                            TokenType.OBJECT,
                            TokenType.ARRAY,
                            TokenType.IDENTIFIER,
                        ):
                            params[key] = self.current_token.value
                            self.advance()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RPAREN)

        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ModelOperation(operation, model_name, params)

    def parse_expression(self) -> Any:
        return self.parse_or_expression()

    def parse_or_expression(self) -> Any:
        left = self.parse_and_expression()

        while self.current_token and self.current_token.type == TokenType.OR:
            op = self.current_token.value
            self.advance()
            right = self.parse_and_expression()
            left = BinaryOp(left, op, right)

        return left

    def parse_and_expression(self) -> Any:
        left = self.parse_equality_expression()

        while self.current_token and self.current_token.type == TokenType.AND:
            op = self.current_token.value
            self.advance()
            right = self.parse_equality_expression()
            left = BinaryOp(left, op, right)

        return left

    def parse_equality_expression(self) -> Any:
        left = self.parse_comparison_expression()

        while self.current_token and self.current_token.type in [
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
        ]:
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison_expression()
            left = BinaryOp(left, op, right)

        return left

    def parse_comparison_expression(self) -> Any:
        left = self.parse_additive_expression()

        while self.current_token and self.current_token.type in [
            TokenType.LESS_THAN,
            TokenType.GREATER_THAN,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        ]:
            op = self.current_token.value
            self.advance()
            right = self.parse_additive_expression()
            left = BinaryOp(left, op, right)

        return left

    def parse_additive_expression(self) -> Any:
        left = self.parse_multiplicative_expression()

        while self.current_token and self.current_token.type in [
            TokenType.PLUS,
            TokenType.MINUS,
        ]:
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplicative_expression()
            left = BinaryOp(left, op, right)

        return left

    def parse_multiplicative_expression(self) -> Any:
        left = self.parse_unary_expression()

        while self.current_token and self.current_token.type in [
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.MODULO,
        ]:
            op = self.current_token.value
            self.advance()
            right = self.parse_unary_expression()
            left = BinaryOp(left, op, right)

        return left

    def parse_unary_expression(self) -> Any:
        if self.current_token and self.current_token.type in [
            TokenType.NOT,
            TokenType.MINUS,
        ]:
            op = self.current_token.value
            self.advance()
            operand = self.parse_unary_expression()
            return UnaryOp(op, operand)

        return self.parse_primary_expression()

    def parse_primary_expression(self) -> Any:
        if not self.current_token:
            raise SyntaxError("Expressão inesperada")

        # Literals
        if self.current_token.type == TokenType.NUMBER:
            token = self.current_token
            value = token.value
            self.advance()
            if "." in value:
                node = Literal(float(value), line=token.line, column=token.column)
            else:
                node = Literal(int(value), line=token.line, column=token.column)

        elif self.current_token.type == TokenType.STRING:
            token = self.current_token
            node = Literal(token.value, line=token.line, column=token.column)
            self.advance()

        elif self.current_token.type == TokenType.BOOLEAN:
            token = self.current_token
            node = Literal(token.value == "true", line=token.line, column=token.column)
            self.advance()

        # Lambda expression: fn(params) { body }
        elif self.current_token.type == TokenType.FN:
            token = self.current_token
            self.advance()
            self.expect(TokenType.LPAREN)

            # Parse parameters with optional types and optional defaults
            params = []
            param_types: Dict[str, Optional[str]] = {}
            param_defaults: Dict[str, Any] = {}
            if not (self.current_token and self.current_token.type == TokenType.RPAREN):
                while True:
                    pname = self.expect(TokenType.IDENTIFIER).value
                    ptype = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COLON
                    ):
                        self.advance()
                        ptype = self._format_type_annotation(
                            self.parse_type_annotation()
                        )
                    # optional default value after '='
                    pdefault = None
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.ASSIGN
                    ):
                        self.advance()
                        pdefault = self.parse_expression()
                    params.append(pname)
                    param_types[pname] = ptype
                    if pdefault is not None:
                        param_defaults[pname] = pdefault
                    if not (
                        self.current_token
                        and self.current_token.type == TokenType.COMMA
                    ):
                        break
                    self.advance()

            self.expect(TokenType.RPAREN)

            # Optional return type
            return_type = None
            if self.current_token and self.current_token.type == TokenType.COLON:
                self.advance()
                return_type = self._format_type_annotation(self.parse_type_annotation())

            # Parse body
            self.expect(TokenType.LBRACE)
            body = []
            while self.current_token and self.current_token.type != TokenType.RBRACE:
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
            self.expect(TokenType.RBRACE)

            node = LambdaExpression(
                params,
                body,
                param_types=param_types,
                param_defaults=param_defaults if param_defaults else None,
                return_type=return_type,
                line=token.line,
                column=token.column,
            )

        # Identifier (may be intent call)
        elif self.current_token.type == TokenType.IDENTIFIER:
            name_token = self.current_token
            node = Identifier(
                name_token.value, line=name_token.line, column=name_token.column
            )
            self.advance()
            # If LPAREN follows, it's a call on the identifier
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                args = []
                while (
                    self.current_token and self.current_token.type != TokenType.RPAREN
                ):
                    args.append(self.parse_expression())
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COMMA
                    ):
                        self.advance()
                self.expect(TokenType.RPAREN)
                node = FunctionCall(
                    node, args, line=name_token.line, column=name_token.column
                )

        elif self.current_token.type == TokenType.NEW:
            token = self.current_token
            self.advance()
            class_name = self.expect(TokenType.IDENTIFIER).value
            args = []
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                while (
                    self.current_token and self.current_token.type != TokenType.RPAREN
                ):
                    args.append(self.parse_expression())
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COMMA
                    ):
                        self.advance()
                self.expect(TokenType.RPAREN)
            node = NewExpression(class_name, args, line=token.line, column=token.column)

        elif self.current_token.type == TokenType.THIS:
            token = self.current_token
            self.advance()
            node = ThisExpression(line=token.line, column=token.column)
        elif self.current_token.type == TokenType.SUPER:
            token = self.current_token
            self.advance()
            node = SuperExpression(line=token.line, column=token.column)

        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)

        elif self.current_token.type == TokenType.LBRACE:
            token = self.current_token
            self.advance()
            obj: Dict[str, Any] = {}
            while self.current_token and self.current_token.type != TokenType.RBRACE:
                if self.current_token.type == TokenType.STRING:
                    key = self.current_token.value
                    self.advance()
                elif self.current_token.type == TokenType.IDENTIFIER:
                    key = self.current_token.value
                    self.advance()
                else:
                    raise SyntaxException(
                        self.current_token.line,
                        self.current_token.column,
                        self.pos,
                        "STRING or IDENTIFIER",
                        self.current_token.type.name,
                    )

                self.expect(TokenType.COLON)
                value_expr = self.parse_expression()
                obj[key] = value_expr
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RBRACE)
            node = JsonObject(obj, line=token.line, column=token.column)

        elif self.current_token.type == TokenType.DATASET:
            return self.parse_dataset_operation()
        elif self.current_token.type == TokenType.MODEL:
            return self.parse_model_operation()
        elif self.current_token.type == TokenType.AWAIT:
            token = self.current_token
            self.advance()
            expr = self.parse_expression()
            return Await(expr, line=token.line, column=token.column)
        elif self.current_token.type == TokenType.OBJECT:
            token = self.current_token
            json_str = token.value
            self.advance()
            try:
                json_data = json.loads(json_str)
                return JsonObject(json_data, line=token.line, column=token.column)
            except json.JSONDecodeError:
                raise SyntaxError(f"JSON inválido: {json_str}")

        elif self.current_token.type == TokenType.ARRAY:
            token = self.current_token
            json_str = token.value
            self.advance()
            try:
                json_data = json.loads(json_str)
                node = JsonArray(json_data, line=token.line, column=token.column)
            except json.JSONDecodeError:
                raise SyntaxError(f"Array JSON inválido: {json_str}")

        elif self.current_token.type == TokenType.NULL:
            token = self.current_token
            self.advance()
            node = NullLiteral()

        elif (
            self.current_token.type == TokenType.IDENTIFIER
            and self.current_token.value in ["null", "None"]
        ):
            token = self.current_token
            self.advance()
            node = NullLiteral()

        else:
            raise SyntaxError(
                f"Unexpected token encountered: '{self.current_token.type}' "
                f"at line {self.current_token.line}, column {self.current_token.column} (offset {self.pos}). "
                f"This token does not match the expected grammar at this point in the input."
            )

        # Postfix operations: intent calls and property access chaining
        while True:
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                # intent call on current node
                self.advance()
                args = []
                while (
                    self.current_token and self.current_token.type != TokenType.RPAREN
                ):
                    args.append(self.parse_expression())
                    if (
                        self.current_token
                        and self.current_token.type == TokenType.COMMA
                    ):
                        self.advance()
                self.expect(TokenType.RPAREN)
                node = FunctionCall(
                    node,
                    args,
                    line=getattr(node, "line", None),
                    column=getattr(node, "column", None),
                )
                continue
            if self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()
                prop_token = self.expect(TokenType.IDENTIFIER)
                prop = prop_token.value
                node = PropertyAccess(
                    node, prop, line=prop_token.line, column=prop_token.column
                )
                continue
            if self.current_token and self.current_token.type == TokenType.LBRACKET:
                # index access
                self.advance()
                idx = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = IndexAccess(
                    node,
                    idx,
                    line=getattr(node, "line", None),
                    column=getattr(node, "column", None),
                )
                continue
            break

        return node


__all__ = ["Parser"]
