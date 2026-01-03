"""AST nodes for ubus IDL"""

from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Annotation:
    """Annotation, e.g., @name("value"), @mask(0x1), @tag(0x1)"""
    name: str
    value: Union[str, int]


@dataclass
class FieldDef:
    """Field definition, e.g., id: int32 or msg?: string"""
    name: str
    type_name: str
    optional: bool = False


@dataclass
class TypeDef:
    """Type definition, e.g., hello1: { id: int32, msg?: string }"""
    name: str
    fields: List[FieldDef]


@dataclass
class Parameter:
    """Method parameter, e.g., id: int32 or hello1 (using defined type)"""
    name: Optional[str]  # None means using defined type
    type_name: str
    optional: bool = False


@dataclass
class MethodDef:
    """Method definition"""
    name: str
    parameters: List[Parameter]
    annotations: List[Annotation]
    custom_handler: Optional[str] = None  # For -> handler2 syntax (future support)


@dataclass
class ObjectDef:
    """Object definition"""
    name: str
    types: List[TypeDef]
    methods: List[MethodDef]


@dataclass
class Document:
    """Complete IDL document"""
    objects: List[ObjectDef]
    global_types: List[TypeDef] = None  # Types defined outside objects
    
    def __post_init__(self):
        if self.global_types is None:
            self.global_types = []

