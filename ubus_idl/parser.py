"""Lark parser for ubus IDL"""

from lark import Lark, Transformer, Token
from typing import List, Union
from .ast import (
    Annotation, FieldDef, TypeDef, Parameter, MethodDef, ObjectDef, Document
)


# Lark grammar definition
GRAMMAR = r"""
start: (type_def | object)*

object: "object" CNAME "{" (type_def | method_def)* "}"

type_def: CNAME ":" "{" field_def* "}"

field_def: CNAME OPTIONAL? ":" type_name
OPTIONAL: "?"

method_def: annotation* method_decl

method_decl: CNAME "(" (param_list | type_ref)? ")" (":" CNAME)?

param_list: param ("," param)*

param: CNAME OPTIONAL? ":" type_name

type_ref: CNAME

type_name: INT8 | INT16 | INT32 | INT64 | STRING_TYPE | BOOL | DOUBLE | ARRAY | UNSPEC | CNAME
INT8: "int8"
INT16: "int16"
INT32: "int32"
INT64: "int64"
STRING_TYPE: "string"
BOOL: "bool"
DOUBLE: "double"
ARRAY: "array"
UNSPEC: "unspec"

annotation: "@" CNAME "(" annotation_value ")"

annotation_value: STRING | HEX_NUMBER | NUMBER

%import common.CNAME
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
%ignore /\/\/.*/

HEX_NUMBER: /0[xX][0-9a-fA-F]+/
NUMBER: /-?[0-9]+/
"""


class UbusIDLTransformer(Transformer):
    """Transform Lark parse tree to AST"""
    
    def start(self, items):
        """start: (type_def | object)*"""
        objects = []
        global_types = []
        for item in items:
            if isinstance(item, ObjectDef):
                objects.append(item)
            elif isinstance(item, TypeDef):
                global_types.append(item)
        return Document(objects=objects, global_types=global_types)
    
    def object(self, items):
        """object: "object" CNAME "{" ... "}" """
        name = str(items[0])
        types = []
        methods = []
        
        for item in items[1:]:
            if isinstance(item, TypeDef):
                types.append(item)
            elif isinstance(item, MethodDef):
                methods.append(item)
        
        return ObjectDef(name=name, types=types, methods=methods)
    
    def type_def(self, items):
        """type_def: CNAME ":" "{" field_def* "}" """
        name = str(items[0])
        fields = [item for item in items[1:] if isinstance(item, FieldDef)]
        return TypeDef(name=name, fields=fields)
    
    def field_def(self, items):
        """field_def: CNAME OPTIONAL? ":" type_name"""
        field_name = str(items[0])
        # items structure (after transformer processes OPTIONAL):
        # If OPTIONAL is present: [CNAME, "?", type_name] -> items[1] is "?", items[2] is type_name
        # If OPTIONAL is not present: [CNAME, type_name] -> items[1] is type_name
        optional = False
        type_idx = 1  # Default: no OPTIONAL, type_name is at index 1
        
        if len(items) >= 3:
            # Check if items[1] is "?" (the OPTIONAL token)
            if str(items[1]) == "?":
                optional = True
                type_idx = 2  # type_name is at index 2 (after CNAME, "?")
            else:
                # No OPTIONAL, type_name is at items[1]
                type_idx = 1
        elif len(items) == 2:
            # No OPTIONAL, type_name is at items[1]
            type_idx = 1
        
        if type_idx < len(items):
            type_name_item = items[type_idx]
            if hasattr(type_name_item, 'value'):
                type_name = str(type_name_item.value)
            else:
                type_name = str(type_name_item)
        else:
            type_name = ""
        
        return FieldDef(name=field_name, type_name=type_name, optional=optional)
    
    def OPTIONAL(self, token):
        """OPTIONAL: "?" """
        return "?"
    
    def method_def(self, items):
        """method_def: annotation* method_decl"""
        annotations = []
        method_decl = None
        
        for item in items:
            if isinstance(item, Annotation):
                annotations.append(item)
            elif isinstance(item, MethodDef):
                method_decl = item
        
        if method_decl:
            method_decl.annotations = annotations
        return method_decl
    
    def method_decl(self, items):
        """method_decl: CNAME "(" ... ")" (":" CNAME)?"""
        method_name = str(items[0])
        parameters = []
        custom_handler = None
        
        # Process parameters and custom handler
        # items[0] is method name
        # items[1] might be parameter (list, str, or None)
        # items[2] might be custom handler (if present)
        
        if len(items) == 1:
            # Only method name, no parameters, no custom handler
            pass
        elif len(items) == 2:
            # Might be parameter or custom handler
            item = items[1]
            if isinstance(item, str):
                # Might be type_ref or custom handler
                # If syntax is correct, should be type_ref (parameter)
                parameters = [Parameter(name=None, type_name=item)]
            elif isinstance(item, list):
                # param_list
                parameters = item
            # If None, means empty parameter list
        elif len(items) == 3:
            # method_name, param_item, handler_name
            param_item = items[1]
            custom_handler = str(items[2])
            
            if param_item is not None:
                if isinstance(param_item, list):
                    # param_list
                    parameters = param_item
                elif isinstance(param_item, str):
                    # type_ref (using defined type)
                    parameters = [Parameter(name=None, type_name=param_item)]
        
        return MethodDef(
            name=method_name,
            parameters=parameters,
            annotations=[],
            custom_handler=custom_handler
        )
    
    def param_list(self, items):
        """param_list: param ("," param)*"""
        return list(items)
    
    def param(self, items):
        """param: CNAME OPTIONAL? ":" type_name"""
        param_name = str(items[0])
        # Check if OPTIONAL is present
        optional = False
        type_idx = 1  # Default: no OPTIONAL, type_name is at index 1
        
        if len(items) >= 3:
            # Check if items[1] is "?" (the OPTIONAL token)
            if str(items[1]) == "?":
                optional = True
                type_idx = 2  # type_name is at index 2 (after CNAME, "?")
            else:
                # No OPTIONAL, type_name is at items[1]
                type_idx = 1
        elif len(items) == 2:
            # No OPTIONAL, type_name is at items[1]
            type_idx = 1
        
        if type_idx < len(items):
            type_name_item = items[type_idx]
            # Check if it's the result of type_name transformer (string)
            if isinstance(type_name_item, str):
                type_name = type_name_item
            elif isinstance(type_name_item, Token):
                type_name = str(type_name_item.value)
            else:
                type_name = str(type_name_item)
        else:
            # Fallback: if type_name transformer returned empty, check the parse tree
            # This shouldn't happen, but handle it gracefully
            type_name = ""
        return Parameter(name=param_name, type_name=type_name, optional=optional)
    
    def type_ref(self, items):
        """type_ref: CNAME"""
        return str(items[0])
    
    def type_name(self, items):
        """type_name: INT32 | INT64 | STRING | ..."""
        if not items:
            return ""
        item = items[0]
        # Handle Token objects (from terminals like INT32, CNAME)
        if hasattr(item, 'value'):
            return str(item.value)
        return str(item)
    
    def INT8(self, token):
        return "int8"
    
    def INT16(self, token):
        return "int16"
    
    def INT32(self, token):
        return "int32"
    
    def INT64(self, token):
        return "int64"
    
    def STRING_TYPE(self, token):
        return "string"
    
    def BOOL(self, token):
        return "bool"
    
    def DOUBLE(self, token):
        return "double"
    
    def ARRAY(self, token):
        return "array"
    
    def UNSPEC(self, token):
        return "unspec"
    
    def annotation(self, items):
        """annotation: "@" CNAME "(" annotation_value ")" """
        name = str(items[0])
        value = items[1]
        
        # Process value
        if isinstance(value, Token):
            if value.type == "STRING":
                # Remove quotes - Token's value attribute is already unquoted string
                val = value.value[1:-1] if value.value.startswith('"') else value.value
            elif value.type == "HEX_NUMBER":
                val = int(value.value, 16)
            else:
                val = int(value.value)
        elif isinstance(value, str):
            # String value (already processed)
            if value.startswith('"') and value.endswith('"'):
                val = value[1:-1]
            else:
                val = value
        else:
            val = value
        
        return Annotation(name=name, value=val)
    
    def annotation_value(self, items):
        """annotation_value: STRING | NUMBER | HEX_NUMBER"""
        return items[0]
    
    def CNAME(self, token):
        """Identifier"""
        return str(token)
    
    def STRING(self, token):
        """String"""
        return token
    
    def NUMBER(self, token):
        """Number"""
        return token
    
    def HEX_NUMBER(self, token):
        """Hexadecimal number"""
        return token


class Parser:
    """Ubus IDL parser"""
    
    def __init__(self):
        self.lark = Lark(GRAMMAR, start='start', parser='lalr', transformer=UbusIDLTransformer())
    
    def parse(self, text: str) -> Document:
        """Parse IDL text and return AST"""
        return self.lark.parse(text)

