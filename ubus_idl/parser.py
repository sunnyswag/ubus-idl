"""Lark parser for ubus IDL"""

from lark import Lark, Transformer, Token
from typing import List, Union
from .ast import (
    Annotation, FieldDef, TypeDef, InlineTypeDef, Parameter, MethodDef, ObjectDef, Document
)


# Lark grammar definition
GRAMMAR = r"""
start: (type_def | object)*

object: "object" CNAME "{" (type_def | method_def | subscriber_def)* "}"

type_def: CNAME ":" "{" field_def_block "}"

field_def_block: field_def*

field_def: CNAME OPTIONAL? ":" type_name ","? INLINE_COMMENT?
OPTIONAL: "?"
INLINE_COMMENT: /\/\/[^\n]*/

method_def: annotation* "method" CNAME "(" (param_list | type_ref)? ")" (":" return_type)?

subscriber_def: "subscriber" CNAME ":" return_type

return_type: CNAME
           | inline_type

inline_type: "{" inline_field_list "}"

inline_field_list: field_def*

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

annotation: "@" CNAME "(" annotation_args ")"
          | "@" CNAME

annotation_args: annotation_kv ("," annotation_kv)*
               | annotation_value

annotation_kv: CNAME ":" annotation_value

annotation_value: STRING | HEX_NUMBER | NUMBER

%import common.CNAME
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
%ignore LINE_COMMENT

LINE_COMMENT: /\/\/[^\n]*/
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
        """type_def: CNAME ":" "{" field_def_block "}" """
        name = str(items[0])
        fields = []
        for item in items[1:]:
            if isinstance(item, list):
                fields = item
            elif isinstance(item, FieldDef):
                fields.append(item)
        return TypeDef(name=name, fields=fields)
    
    def field_def_block(self, items):
        """field_def_block: field_def*"""
        return [item for item in items if isinstance(item, FieldDef)]
    
    def inline_field_list(self, items):
        """inline_field_list: field_def*"""
        return [item for item in items if isinstance(item, FieldDef)]
    
    def field_def(self, items):
        """field_def: CNAME OPTIONAL? ":" type_name INLINE_COMMENT?"""
        field_name = str(items[0])
        optional = False
        type_name = ""
        comment = None
        
        idx = 1
        # Check for OPTIONAL
        if idx < len(items) and str(items[idx]) == "?":
            optional = True
            idx += 1
        
        # Get type_name
        if idx < len(items):
            type_name_item = items[idx]
            if isinstance(type_name_item, str):
                type_name = type_name_item
            elif hasattr(type_name_item, 'value'):
                type_name = str(type_name_item.value)
            else:
                type_name = str(type_name_item)
            idx += 1
        
        # Check for inline comment
        if idx < len(items):
            comment_item = items[idx]
            if isinstance(comment_item, Token) and comment_item.type == "INLINE_COMMENT":
                comment = str(comment_item.value).lstrip('/').strip()
        
        return FieldDef(name=field_name, type_name=type_name, optional=optional, comment=comment)
    
    def OPTIONAL(self, token):
        """OPTIONAL: "?" """
        return "?"
    
    def INLINE_COMMENT(self, token):
        r"""INLINE_COMMENT: /\/\/[^\n]*/"""
        return token
    
    def method_def(self, items):
        """method_def: annotation* "method" CNAME "(" ... ")" (":" return_type)?"""
        annotations = []
        method_name = None
        parameters = []
        return_type = None
        custom_handler = None
        
        for item in items:
            if isinstance(item, Annotation):
                annotations.append(item)
                # Check for @handler annotation
                if item.name == "handler" and item.params:
                    custom_handler = item.params.get("path")
            elif isinstance(item, str) and method_name is None:
                method_name = item
            elif isinstance(item, list):
                parameters = item
            elif isinstance(item, str) and method_name is not None:
                # This could be type_ref (parameter) or return type
                if not parameters and item != method_name:
                    # It's a type_ref for parameter
                    parameters = [Parameter(name=None, type_name=item)]
                else:
                    return_type = item
            elif isinstance(item, InlineTypeDef):
                return_type = item
        
        return MethodDef(
            name=method_name,
            kind="method",
            parameters=parameters,
            annotations=annotations,
            return_type=return_type,
            custom_handler=custom_handler
        )
    
    def subscriber_def(self, items):
        """subscriber_def: "subscriber" CNAME ":" return_type"""
        name = str(items[0])
        return_type = None
        
        for item in items[1:]:
            if isinstance(item, str):
                return_type = item
            elif isinstance(item, InlineTypeDef):
                return_type = item
        
        return MethodDef(
            name=name,
            kind="subscriber",
            parameters=[],
            annotations=[],
            return_type=return_type,
            custom_handler=None
        )
    
    def return_type(self, items):
        """return_type: CNAME | inline_type"""
        if len(items) == 1:
            item = items[0]
            if isinstance(item, InlineTypeDef):
                return item
            return str(item)
        return items[0]
    
    def inline_type(self, items):
        """inline_type: "{" inline_field_list "}" """
        fields = []
        for item in items:
            if isinstance(item, list):
                fields = item
            elif isinstance(item, FieldDef):
                fields.append(item)
        return InlineTypeDef(fields=fields)
    
    def param_list(self, items):
        """param_list: param ("," param)*"""
        return list(items)
    
    def param(self, items):
        """param: CNAME OPTIONAL? ":" type_name"""
        param_name = str(items[0])
        optional = False
        type_name = ""
        
        idx = 1
        if idx < len(items) and str(items[idx]) == "?":
            optional = True
            idx += 1
        
        if idx < len(items):
            type_name_item = items[idx]
            if isinstance(type_name_item, str):
                type_name = type_name_item
            elif isinstance(type_name_item, Token):
                type_name = str(type_name_item.value)
            else:
                type_name = str(type_name_item)
        
        return Parameter(name=param_name, type_name=type_name, optional=optional)
    
    def type_ref(self, items):
        """type_ref: CNAME"""
        return str(items[0])
    
    def type_name(self, items):
        """type_name: INT32 | INT64 | STRING | ..."""
        if not items:
            return ""
        item = items[0]
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
        """annotation: "@" CNAME "(" annotation_args ")" | "@" CNAME"""
        name = str(items[0])
        value = None
        params = {}
        
        if len(items) > 1:
            args = items[1]
            if isinstance(args, dict):
                params = args
            elif isinstance(args, tuple):
                # Single key-value pair
                params = {args[0]: args[1]}
            else:
                # Simple value
                value = self._process_annotation_value(args)
        
        return Annotation(name=name, value=value, params=params)
    
    def annotation_args(self, items):
        """annotation_args: annotation_kv ("," annotation_kv)* | annotation_value"""
        if len(items) == 1:
            item = items[0]
            if isinstance(item, tuple):
                # Single key-value pair
                return {item[0]: item[1]}
            else:
                # Simple value
                return item
        else:
            # Multiple key-value pairs
            result = {}
            for item in items:
                if isinstance(item, tuple):
                    result[item[0]] = item[1]
            return result
    
    def annotation_kv(self, items):
        """annotation_kv: CNAME ":" annotation_value"""
        key = str(items[0])
        value = self._process_annotation_value(items[1])
        return (key, value)
    
    def _process_annotation_value(self, value):
        """Process annotation value"""
        if isinstance(value, Token):
            if value.type == "STRING":
                val = value.value
                if val.startswith('"') and val.endswith('"'):
                    return val[1:-1]
                return val
            elif value.type == "HEX_NUMBER":
                return int(value.value, 16)
            else:
                return int(value.value)
        elif isinstance(value, str):
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            return value
        return value
    
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
