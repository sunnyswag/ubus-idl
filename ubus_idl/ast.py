"""AST nodes for ubus IDL"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict


@dataclass
class Annotation:
    """Annotation, e.g., @name("value"), @mask(0x1), @handler(path: "xxx")"""
    name: str
    value: Union[str, int, None] = None  # Simple value
    params: Dict[str, Union[str, int]] = field(default_factory=dict)  # Key-value pairs


@dataclass
class FieldDef:
    """Field definition, e.g., id: int32 or msg?: string"""
    name: str
    type_name: str
    optional: bool = False
    comment: Optional[str] = None  # For TypeScript generation


@dataclass
class TypeDef:
    """Type definition, e.g., hello1: { id: int32, msg?: string }"""
    name: str
    fields: List[FieldDef]


@dataclass
class InlineTypeDef:
    """Inline type definition for return types, e.g., { res1: int32, res2: string }"""
    fields: List[FieldDef]


@dataclass
class Parameter:
    """Method parameter, e.g., id: int32 or hello1 (using defined type)"""
    name: Optional[str]  # None means using defined type
    type_name: str
    optional: bool = False


@dataclass
class MethodDef:
    """Method definition (method or subscriber)"""
    name: str
    kind: str  # "method" or "subscriber"
    parameters: List[Parameter]
    annotations: List[Annotation]
    return_type: Optional[Union[str, InlineTypeDef]] = None  # Return type name or inline definition
    custom_handler: Optional[str] = None  # For @handler annotation


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

