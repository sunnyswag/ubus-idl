"""Code generator for ubus IDL using Jinja2 templates"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .ast import (
    Document, ObjectDef, TypeDef, MethodDef, FieldDef, Parameter, Annotation, InlineTypeDef
)


# ============================================================================
# Type Information for C Code Generation
# ============================================================================

@dataclass
class TypeInfo:
    """Type information for code generation"""
    c_type: str  # C type name (e.g., "int32_t", "const char *")
    blob_type: str  # BLOBMSG_TYPE constant
    ts_type: str  # TypeScript type
    get_func: str  # blobmsg_get function name (e.g., "u32", "string")
    add_func: str  # blobmsg_add function name (e.g., "u32", "string")
    is_pointer: bool = False
    use_field_api: bool = False


def get_bitfield_type(optional_count: int) -> Optional[str]:
    """Get the appropriate bitfield type based on optional field count"""
    if optional_count == 0:
        return None
    elif optional_count <= 8:
        return "uint8_t"
    elif optional_count <= 16:
        return "uint16_t"
    else:
        return "uint32_t"


# ============================================================================
# Naming Utilities
# ============================================================================

def to_pascal_case(name: str) -> str:
    """Convert snake_case or kebab-case to PascalCase"""
    parts = name.replace('-', '_').split('_')
    return ''.join(part.capitalize() for part in parts)


def to_camel_case(name: str) -> str:
    """Convert snake_case or kebab-case to camelCase"""
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""


# ============================================================================
# Type Factory
# ============================================================================

class TypeFactory:
    """Factory for type information"""
    
    _type_info: Dict[str, TypeInfo] = {
        "string": TypeInfo(
            c_type="const char *",
            blob_type="BLOBMSG_TYPE_STRING",
            ts_type="string",
            get_func="string",
            add_func="string",
            is_pointer=True,
        ),
        "int8": TypeInfo(
            c_type="int8_t",
            blob_type="BLOBMSG_TYPE_INT8",
            ts_type="number",
            get_func="u8",
            add_func="u8",
        ),
        "int16": TypeInfo(
            c_type="int16_t",
            blob_type="BLOBMSG_TYPE_INT16",
            ts_type="number",
            get_func="u16",
            add_func="u16",
        ),
        "int32": TypeInfo(
            c_type="int32_t",
            blob_type="BLOBMSG_TYPE_INT32",
            ts_type="number",
            get_func="u32",
            add_func="u32",
        ),
        "int64": TypeInfo(
            c_type="int64_t",
            blob_type="BLOBMSG_TYPE_INT64",
            ts_type="number",
            get_func="u64",
            add_func="u64",
        ),
        "bool": TypeInfo(
            c_type="bool",
            blob_type="BLOBMSG_TYPE_BOOL",
            ts_type="boolean",
            get_func="u8",
            add_func="u8",
        ),
        "double": TypeInfo(
            c_type="double",
            blob_type="BLOBMSG_TYPE_DOUBLE",
            ts_type="number",
            get_func="double",
            add_func="double",
        ),
        "array": TypeInfo(
            c_type="struct blob_attr *",
            blob_type="BLOBMSG_TYPE_ARRAY",
            ts_type="any[]",
            get_func="",
            add_func="",
            is_pointer=True,
            use_field_api=True,
        ),
        "unspec": TypeInfo(
            c_type="struct blob_attr *",
            blob_type="BLOBMSG_TYPE_UNSPEC",
            ts_type="any",
            get_func="",
            add_func="",
            is_pointer=True,
            use_field_api=True,
        ),
    }
    
    @classmethod
    def get_type_info(cls, type_name: str) -> Optional[TypeInfo]:
        return cls._type_info.get(type_name)
    
    @classmethod
    def get_blob_type(cls, type_name: str) -> str:
        type_info = cls.get_type_info(type_name)
        if type_info:
            return type_info.blob_type
        return "BLOBMSG_TYPE_TABLE"
    
    @classmethod
    def get_struct_field_type(cls, type_name: str) -> str:
        type_info = cls.get_type_info(type_name)
        if type_info:
            return type_info.c_type
        return f"struct {type_name} *"
    
    @classmethod
    def get_ts_type(cls, type_name: str) -> str:
        type_info = cls.get_type_info(type_name)
        if type_info:
            return type_info.ts_type
        # Custom type - return PascalCase
        return to_pascal_case(type_name)


# ============================================================================
# Code Generator
# ============================================================================

class CodeGenerator:
    """Unified code generator using Jinja2 templates"""
    
    def __init__(self, document: Document):
        self.document = document
        self.type_defs: Dict[str, TypeDef] = {}
        self.type_owners: Dict[str, str] = {}  # type_name -> object_name (None for global)
        
        # Collect all type definitions
        for type_def in document.global_types:
            self.type_defs[type_def.name] = type_def
            self.type_owners[type_def.name] = None
        for obj in document.objects:
            for type_def in obj.types:
                self.type_defs[type_def.name] = type_def
                self.type_owners[type_def.name] = obj.name
        
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate(self, target: str = "c") -> Dict[str, str]:
        """Generate code files for specified target (c, ts, or all)"""
        result = {}
        
        for obj in self.document.objects:
            if target in ["c", "all"]:
                result.update(self._generate_c(obj))
            
            if target in ["ts", "all"]:
                result.update(self._generate_ts(obj))
        
        return result
    
    # ========================================================================
    # C Code Generation
    # ========================================================================
    
    def _generate_c(self, obj: ObjectDef) -> Dict[str, str]:
        """Generate C code for an object"""
        header_name = f"{obj.name.lower()}_object.h"
        source_name = f"{obj.name.lower()}_object.c"
        
        context = self._prepare_c_context(obj)
        
        header_template = self.env.get_template('object.h.j2')
        source_template = self.env.get_template('object.c.j2')
        
        return {
            header_name: header_template.render(**context),
            source_name: source_template.render(**context),
        }
    
    def _prepare_c_context(self, obj: ObjectDef) -> Dict:
        """Prepare template context data for C generation"""
        obj_name_lower = obj.name.lower()
        obj_name_upper = obj.name.upper().replace("-", "_")
        header_guard = f"__{obj_name_upper}_OBJECT_H__"
        
        # Filter only methods (not subscribers) for C code generation
        methods = [m for m in obj.methods if m.kind == "method"]
        
        # Collect global types used by this object
        used_global_types = set()
        for method in methods:
            if method.parameters:
                param = method.parameters[0]
                if not param.name:
                    type_name = param.type_name
                    if type_name in self.type_owners and self.type_owners[type_name] is None:
                        used_global_types.add(type_name)
        
        global_types = []
        for type_name in used_global_types:
            type_def = self.type_defs.get(type_name)
            if type_def:
                global_types.append(self._type_to_c_dict(None, type_def))
        
        object_types = [self._type_to_c_dict(obj, t) for t in obj.types]
        
        method_params = []
        for method in methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:
                    method_name = self._get_method_name(method)
                    method_params_dict = self._method_params_to_c_dict(obj, method_name, method.parameters)
                    method_params_dict['fields'] = method_params_dict.pop('params')
                    method_params_dict['has_optional_fields'] = method_params_dict.pop('has_optional_params')
                    method_params_dict['optional_fields'] = method_params_dict.pop('optional_params')
                    method_params.append(method_params_dict)
        
        all_methods = [self._method_to_c_dict(obj, m) for m in methods]
        
        serialize_types = self._get_serialize_types(obj, methods)
        policy_types = self._get_policy_types(obj, methods)
        custom_handlers = [self._custom_handler_to_dict(obj, m) for m in methods if m.custom_handler]
        
        all_structs = []
        all_structs.extend(global_types)
        all_structs.extend(object_types)
        all_structs.extend(method_params)
        
        return {
            'obj': obj,
            'obj_name': obj.name,
            'obj_name_lower': obj_name_lower,
            'obj_name_upper': obj_name_upper,
            'header_guard': header_guard,
            'global_types': global_types,
            'object_types': object_types,
            'method_params': method_params,
            'all_structs': all_structs,
            'all_methods': all_methods,
            'serialize_types': serialize_types,
            'policy_types': policy_types,
            'custom_handlers': custom_handlers,
        }
    
    # ========================================================================
    # TypeScript Code Generation
    # ========================================================================
    
    def _generate_ts(self, obj: ObjectDef) -> Dict[str, str]:
        """Generate TypeScript code for an object"""
        ts_name = f"{obj.name.lower()}.ts"
        
        context = self._prepare_ts_context(obj)
        
        ts_template = self.env.get_template('object.ts.j2')
        
        return {
            ts_name: ts_template.render(**context),
        }
    
    def _prepare_ts_context(self, obj: ObjectDef) -> Dict:
        """Prepare template context data for TypeScript generation"""
        obj_name_pascal = to_pascal_case(obj.name)
        obj_name_camel = to_camel_case(obj.name)
        obj_name_lower = obj.name.lower().replace('-', '_')
        
        # Collect global types used by this object
        used_global_types = self._collect_used_global_types(obj)
        global_types = []
        for type_name in used_global_types:
            type_def = self.type_defs.get(type_name)
            if type_def:
                global_types.append(self._type_to_ts_dict(type_def, to_pascal_case(type_name), obj))
        
        # Object types
        object_types = []
        for type_def in obj.types:
            interface_name = f"{obj_name_pascal}{to_pascal_case(type_def.name)}"
            object_types.append(self._type_to_ts_dict(type_def, interface_name, obj))
        
        # Inline return types
        inline_return_types = []
        generated_interfaces = set()
        
        for method in obj.methods:
            if method.return_type and isinstance(method.return_type, InlineTypeDef):
                if method.kind == "subscriber":
                    interface_name = f"{obj_name_pascal}{to_pascal_case(method.name)}Data"
                else:
                    interface_name = f"{obj_name_pascal}{to_pascal_case(method.name)}Response"
                
                if interface_name not in generated_interfaces:
                    inline_return_types.append({
                        'ts_interface_name': interface_name,
                        'fields': [self._field_to_ts_dict(f, obj) for f in method.return_type.fields],
                    })
                    generated_interfaces.add(interface_name)
        
        # Methods
        methods = []
        for method in obj.methods:
            if method.kind == "method":
                methods.append(self._method_to_ts_dict(obj, method))
        
        # Subscribers
        subscribers = []
        for method in obj.methods:
            if method.kind == "subscriber":
                subscribers.append(self._subscriber_to_ts_dict(obj, method))
        
        return {
            'obj_name': obj.name,
            'obj_name_pascal': obj_name_pascal,
            'obj_name_camel': obj_name_camel,
            'obj_name_lower': obj_name_lower,
            'global_types': global_types,
            'object_types': object_types,
            'inline_return_types': inline_return_types,
            'methods': methods,
            'subscribers': subscribers,
        }
    
    def _collect_used_global_types(self, obj: ObjectDef) -> Set[str]:
        """Collect all global types used by this object"""
        used_types = set()
        for method in obj.methods:
            for param in method.parameters:
                # Only generate TS interfaces for global types that are referenced as
                # a named parameter type (e.g. foo(x: some_global_type)).
                # For type_ref parameters (name is None), we expand fields into params
                # and do not need the interface emitted.
                if param.name and param.type_name in self.type_defs and self.type_owners.get(param.type_name) is None:
                    used_types.add(param.type_name)
            # Also include global types referenced as return types (method/subscriber)
            if isinstance(method.return_type, str):
                rt = method.return_type
                if rt in self.type_defs and self.type_owners.get(rt) is None:
                    used_types.add(rt)
        return used_types
    
    def _type_to_ts_dict(self, type_def: TypeDef, interface_name: str, obj: ObjectDef) -> Dict:
        """Convert type definition to dictionary for TypeScript template"""
        return {
            'ts_interface_name': interface_name,
            'fields': [self._field_to_ts_dict(f, obj) for f in type_def.fields],
        }
    
    def _field_to_ts_dict(self, field: FieldDef, obj: ObjectDef) -> Dict:
        """Convert field to dictionary for TypeScript template"""
        return {
            'name': field.name,
            'ts_type': self._get_ts_type(field.type_name, obj),
            'optional': field.optional,
            'comment': getattr(field, 'comment', None),
        }
    
    def _get_ts_type(self, type_name: str, obj: ObjectDef) -> str:
        """Get TypeScript type for a given IDL type"""
        ts_type = TypeFactory.get_ts_type(type_name)
        if ts_type != to_pascal_case(type_name):
            return ts_type
        
        # Check if it's a global type
        if type_name in self.type_defs and self.type_owners.get(type_name) is None:
            return to_pascal_case(type_name)
        
        # Check if it's an object type
        for t in obj.types:
            if t.name == type_name:
                return f"{to_pascal_case(obj.name)}{to_pascal_case(type_name)}"
        
        return to_pascal_case(type_name)
    
    def _method_to_ts_dict(self, obj: ObjectDef, method: MethodDef) -> Dict:
        """Convert method to dictionary for TypeScript template"""
        obj_name_pascal = to_pascal_case(obj.name)
        
        native_method_name = self._get_method_name(method)

        # Build parameters
        ts_params = []
        call_args = []
        
        for param in method.parameters:
            if param.name:
                ts_type = self._get_ts_type(param.type_name, obj)
                optional_mark = "?" if param.optional else ""
                ts_param_name = to_camel_case(param.name)
                ts_params.append(f"{ts_param_name}{optional_mark}: {ts_type}")
                call_args.append(ts_param_name)
            else:
                # Type reference - expand fields
                type_def = self.type_defs.get(param.type_name)
                if type_def is None:
                    for t in obj.types:
                        if t.name == param.type_name:
                            type_def = t
                            break
                if type_def:
                    for field in type_def.fields:
                        ts_type = self._get_ts_type(field.type_name, obj)
                        optional_mark = "?" if field.optional else ""
                        ts_field_name = to_camel_case(field.name)
                        ts_params.append(f"{ts_field_name}{optional_mark}: {ts_type}")
                        call_args.append(ts_field_name)
        
        # Build return type
        return_type = self._get_ts_return_type(obj, method)
        
        return {
            # TS wrapper method name should follow TS idioms (camelCase),
            # while native method name may be overridden via @name.
            'ts_name': to_camel_case(method.name),
            'native_name': native_method_name,
            'ts_params': ", ".join(ts_params),
            'ts_call_args': ", ".join(call_args),
            'ts_return_type': return_type,
        }
    
    def _subscriber_to_ts_dict(self, obj: ObjectDef, subscriber: MethodDef) -> Dict:
        """Convert subscriber to dictionary for TypeScript template"""
        obj_name_pascal = to_pascal_case(obj.name)
        
        # Build data type
        data_type = "any"
        if subscriber.return_type:
            if isinstance(subscriber.return_type, InlineTypeDef):
                data_type = f"{obj_name_pascal}{to_pascal_case(subscriber.name)}Data"
            elif isinstance(subscriber.return_type, str):
                type_def = self.type_defs.get(subscriber.return_type)
                if type_def is None:
                    for t in obj.types:
                        if t.name == subscriber.return_type:
                            type_def = t
                            break
                if type_def:
                    if self.type_owners.get(subscriber.return_type) is None:
                        data_type = to_pascal_case(subscriber.return_type)
                    else:
                        data_type = f"{obj_name_pascal}{to_pascal_case(subscriber.return_type)}"
        
        return {
            'ts_name': to_camel_case(subscriber.name),
            'native_name': subscriber.name,
            'ts_data_type': data_type,
        }
    
    def _get_ts_return_type(self, obj: ObjectDef, method: MethodDef) -> str:
        """Get TypeScript return type for a method"""
        obj_name_pascal = to_pascal_case(obj.name)
        
        if method.return_type is None:
            return "Promise<void>"
        
        if isinstance(method.return_type, InlineTypeDef):
            return f"Promise<{obj_name_pascal}{to_pascal_case(method.name)}Response>"
        elif isinstance(method.return_type, str):
            type_def = self.type_defs.get(method.return_type)
            if type_def is None:
                for t in obj.types:
                    if t.name == method.return_type:
                        type_def = t
                        break
            if type_def:
                if self.type_owners.get(method.return_type) is None:
                    return f"Promise<{to_pascal_case(method.return_type)}>"
                return f"Promise<{obj_name_pascal}{to_pascal_case(method.return_type)}>"
        
        return "Promise<void>"
    
    # ========================================================================
    # C Code Helper Methods (kept from original)
    # ========================================================================
    
    def _type_to_c_dict(self, obj: Optional[ObjectDef], type_def: TypeDef) -> Dict:
        """Convert type definition to dictionary for C template"""
        if obj:
            prefix = f"{obj.name.lower()}_{type_def.name}"
        else:
            prefix = type_def.name
        
        enum_prefix = f"{prefix.upper()}_"
        optional_fields = [f for f in type_def.fields if f.optional]
        
        fields = []
        for field in type_def.fields:
            enum_item = f"{enum_prefix}{field.name.upper()}"
            field_dict = {
                'name': field.name,
                'type_name': field.type_name,
                'optional': field.optional,
                'c_type': TypeFactory.get_struct_field_type(field.type_name),
                'enum_item': enum_item,
            }
            if field.optional:
                field_dict['bitfield_name'] = f"has_{field.name}"
            fields.append(field_dict)
        
        bitfield_type = get_bitfield_type(len(optional_fields))
        
        return {
            'name': type_def.name,
            'struct_name': prefix,
            'prefix': prefix,
            'enum_prefix': enum_prefix,
            'fields': fields,
            'optional_fields': [f for f in fields if f['optional']],
            'has_optional_fields': bool(optional_fields),
            'bitfield_type': bitfield_type,
        }
    
    def _method_params_to_c_dict(self, obj: ObjectDef, method_name: str, parameters: List[Parameter]) -> Dict:
        """Convert method parameters to dictionary for C template"""
        obj_prefix = obj.name.lower()
        if method_name.startswith(obj_prefix + "_"):
            prefix = method_name
        else:
            prefix = f"{obj_prefix}_{method_name}"
        
        enum_prefix = f"{prefix.upper()}_"
        optional_params = [p for p in parameters if p.name and p.optional]
        
        params = []
        for param in parameters:
            if param.name:
                enum_item = f"{enum_prefix}{param.name.upper()}"
                param_dict = {
                    'name': param.name,
                    'type_name': param.type_name,
                    'optional': param.optional,
                    'c_type': TypeFactory.get_struct_field_type(param.type_name),
                    'enum_item': enum_item,
                }
                if param.optional:
                    param_dict['name_upper'] = param.name.upper()
                    param_dict['bitfield_name'] = f"has_{param.name}"
                params.append(param_dict)
        
        bitfield_type = get_bitfield_type(len(optional_params))
        
        return {
            'struct_name': f"{prefix}_params",
            'prefix': prefix,
            'prefix_upper': prefix.upper(),
            'params': params,
            'optional_params': [p for p in params if p['optional']],
            'has_optional_params': bool(optional_params),
            'bitfield_type': bitfield_type,
        }
    
    def _method_to_c_dict(self, obj: ObjectDef, method: MethodDef) -> Dict:
        """Convert method to dictionary for C template"""
        method_name = self._get_method_name(method)
        handler_name = self._get_handler_name(obj, method)
        method_def = self._generate_method_def(obj, method)
        
        return {
            'name': method.name,
            'method_name': method_name,
            'handler_name': handler_name,
            'method_def': method_def,
            'has_parameters': bool(method.parameters),
            'custom_handler': method.custom_handler,
        }
    
    def _get_serialize_types(self, obj: ObjectDef, methods: List[MethodDef]) -> List[Dict]:
        """Get serialize types for C template"""
        serialize_types = []
        declared_types = set()
        
        for method in methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:
                    method_name = self._get_method_name(method)
                    obj_prefix = obj.name.lower()
                    if method_name.startswith(obj_prefix + "_"):
                        type_key = f"{method_name}_params"
                        struct_type_name = f"{method_name}_params"
                        func_prefix = method_name
                    else:
                        type_key = f"{obj_prefix}_{method_name}_params"
                        struct_type_name = f"{obj_prefix}_{method_name}_params"
                        func_prefix = f"{obj_prefix}_{method_name}"
                    if type_key not in declared_types:
                        declared_types.add(type_key)
                        serialize_types.append({
                            'deserialize_func': f"{func_prefix}_deserialize",
                            'serialize_func': f"{func_prefix}_serialize",
                            'struct_type': struct_type_name,
                        })
                else:
                    type_name = param.type_name
                    if type_name not in declared_types:
                        declared_types.add(type_name)
                        owner = self.type_owners.get(type_name)
                        if owner:
                            struct_type_name = f"{owner.lower()}_{type_name}"
                            func_prefix = f"{owner.lower()}_{type_name}"
                        else:
                            struct_type_name = type_name
                            func_prefix = type_name
                        serialize_types.append({
                            'deserialize_func': f"{func_prefix}_deserialize",
                            'serialize_func': f"{func_prefix}_serialize",
                            'struct_type': struct_type_name,
                        })
        
        return serialize_types
    
    def _get_policy_types(self, obj: ObjectDef, methods: List[MethodDef]) -> List[Dict]:
        """Get policy types for C template"""
        policy_types = []
        policy_type_keys = {}
        
        for method in methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:
                    method_name = self._get_method_name(method)
                    obj_prefix = obj.name.lower()
                    if method_name.startswith(obj_prefix + "_"):
                        type_key = f"{method_name}_params"
                    else:
                        type_key = f"{obj_prefix}_{method_name}_params"
                    if type_key not in policy_type_keys:
                        policy_type_keys[type_key] = (True, method_name, method)
                else:
                    type_name = param.type_name
                    if type_name not in policy_type_keys:
                        policy_type_keys[type_name] = (False, type_name, None)
        
        for type_key, (is_method_params, name, method) in policy_type_keys.items():
            policy_types.append(self._policy_type_to_dict(obj, method, name, is_method_params))
        
        return policy_types
    
    def _policy_type_to_dict(self, obj: ObjectDef, method: Optional[MethodDef], type_name: str, is_method_params: bool) -> Dict:
        """Convert policy type to dictionary for template"""
        if is_method_params and method:
            obj_prefix = obj.name.lower()
            if type_name.startswith(obj_prefix + "_"):
                prefix = type_name
                struct_type_name = f"{type_name}_params"
                func_prefix = type_name
            else:
                prefix = f"{obj_prefix}_{type_name}"
                struct_type_name = f"{obj_prefix}_{type_name}_params"
                func_prefix = f"{obj_prefix}_{type_name}"
            
            enum_prefix = f"{prefix.upper()}_"
            fields = []
            required_fields = []
            optional_fields = []
            
            for param in method.parameters:
                if param.name:
                    enum_item = f"{enum_prefix}{param.name.upper()}"
                    field_dict = {
                        'name': param.name,
                        'type_name': param.type_name,
                        'optional': param.optional,
                        'enum_item': enum_item,
                        'blob_type': TypeFactory.get_blob_type(param.type_name),
                    }
                    if param.optional:
                        field_dict['bitfield_name'] = f"has_{param.name}"
                        optional_fields.append(field_dict)
                    else:
                        required_fields.append(field_dict)
                    fields.append(field_dict)
        else:
            owner = self.type_owners.get(type_name)
            if owner:
                prefix = f"{owner.lower()}_{type_name}"
                struct_type_name = f"{owner.lower()}_{type_name}"
                func_prefix = f"{owner.lower()}_{type_name}"
            else:
                prefix = type_name
                struct_type_name = type_name
                func_prefix = type_name
            
            type_def = self.type_defs.get(type_name)
            if not type_def:
                return {}
            
            enum_prefix = f"{prefix.upper()}_"
            fields = []
            required_fields = []
            optional_fields = []
            
            for field in type_def.fields:
                enum_item = f"{enum_prefix}{field.name.upper()}"
                field_dict = {
                    'name': field.name,
                    'type_name': field.type_name,
                    'optional': field.optional,
                    'enum_item': enum_item,
                    'blob_type': TypeFactory.get_blob_type(field.type_name),
                }
                if field.optional:
                    field_dict['bitfield_name'] = f"has_{field.name}"
                    optional_fields.append(field_dict)
                else:
                    required_fields.append(field_dict)
                fields.append(field_dict)
        
        enum_items = [f['enum_item'] for f in fields]
        enum_max = f"__{prefix.upper()}_MAX"
        policy_name = f"{prefix}_policy"
        tb_name = f"tb_{prefix}"
        
        needs_ret = any(f['type_name'] in ['array', 'unspec'] for f in fields)
        bitfield_type = get_bitfield_type(len(optional_fields))
        
        return {
            'prefix': prefix,
            'enum_items': enum_items,
            'enum_max': enum_max,
            'policy_name': policy_name,
            'tb_name': tb_name,
            'struct_type': struct_type_name,
            'deserialize_func': f"{func_prefix}_deserialize",
            'serialize_func': f"{func_prefix}_serialize",
            'fields': fields,
            'required_fields': required_fields,
            'optional_fields': optional_fields,
            'all_fields': fields,
            'needs_ret': needs_ret,
            'bitfield_type': bitfield_type,
        }
    
    def _custom_handler_to_dict(self, obj: ObjectDef, method: MethodDef) -> Dict:
        """Convert custom handler to dictionary for template"""
        handler_name = self._get_handler_name(obj, method)
        has_params = bool(method.parameters)
        
        params_struct_type = None
        deserialize_func = None
        
        if has_params:
            param = method.parameters[0]
            if param.name:
                method_name = self._get_method_name(method)
                obj_prefix = obj.name.lower()
                if method_name.startswith(obj_prefix + "_"):
                    params_struct_type = f"{method_name}_params"
                    deserialize_func = f"{method_name}_deserialize"
                else:
                    params_struct_type = f"{obj_prefix}_{method_name}_params"
                    deserialize_func = f"{obj_prefix}_{method_name}_deserialize"
            else:
                type_name = param.type_name
                owner = self.type_owners.get(type_name)
                if owner:
                    params_struct_type = f"{owner.lower()}_{type_name}"
                    deserialize_func = f"{owner.lower()}_{type_name}_deserialize"
                else:
                    params_struct_type = type_name
                    deserialize_func = f"{type_name}_deserialize"
        
        return {
            'handler_name': handler_name,
            'has_params': has_params,
            'params_struct_type': params_struct_type,
            'deserialize_func': deserialize_func,
            'custom_handler': method.custom_handler,
        }
    
    def _get_method_name(self, method: MethodDef) -> str:
        """Get actual method name (might be overridden by @name annotation)"""
        method_name = method.name
        for ann in method.annotations:
            if ann.name == "name":
                method_name = ann.value
                break
        return method_name
    
    def _get_handler_name(self, obj: ObjectDef, method: MethodDef) -> str:
        """Get handler function name"""
        if method.custom_handler:
            return method.custom_handler
        
        method_name = self._get_method_name(method)
        obj_prefix = f"{obj.name.lower()}_"
        if method_name.startswith(obj_prefix):
            return f"{method_name}_handler"
        else:
            return f"{obj.name.lower()}_{method_name}_handler"
    
    def _generate_method_def(self, obj: ObjectDef, method: MethodDef) -> str:
        """Generate method definition string"""
        method_name = self._get_method_name(method)
        handler_name = self._get_handler_name(obj, method)
        
        policy_name = None
        if method.parameters:
            param = method.parameters[0]
            if param.name:
                obj_prefix = obj.name.lower()
                if method_name.startswith(obj_prefix + "_"):
                    policy_name = f"{method_name}_policy"
                else:
                    policy_name = f"{obj_prefix}_{method_name}_policy"
            else:
                owner = self.type_owners.get(param.type_name)
                if owner:
                    policy_name = f"{owner.lower()}_{param.type_name}_policy"
                else:
                    policy_name = f"{param.type_name}_policy"
        
        mask = 0
        tags = 0
        for ann in method.annotations:
            if ann.name == "mask":
                if isinstance(ann.value, int):
                    mask = ann.value
                elif isinstance(ann.value, str):
                    mask = int(ann.value, 16) if ann.value.startswith("0x") or ann.value.startswith("0X") else int(ann.value)
            elif ann.name == "tag":
                if isinstance(ann.value, int):
                    tags = ann.value
                elif isinstance(ann.value, str):
                    tags = int(ann.value, 16) if ann.value.startswith("0x") or ann.value.startswith("0X") else int(ann.value)
        
        has_params = bool(method.parameters)
        
        if has_params:
            if mask > 0 and tags > 0:
                return f'{{ __UBUS_METHOD("{method_name}", {handler_name}, {mask}, {policy_name}, {tags}) }}'
            elif tags > 0:
                return f'UBUS_METHOD_TAG("{method_name}", {handler_name}, {policy_name}, {tags})'
            elif mask > 0:
                return f'UBUS_METHOD_MASK("{method_name}", {handler_name}, {policy_name}, {mask})'
            else:
                return f'UBUS_METHOD("{method_name}", {handler_name}, {policy_name})'
        else:
            if mask > 0 and tags > 0:
                return f'{{ __UBUS_METHOD_NOARG("{method_name}", {handler_name}, {mask}, {tags}) }}'
            elif tags > 0:
                return f'UBUS_METHOD_TAG_NOARG("{method_name}", {handler_name}, {tags})'
            elif mask > 0:
                return f'{{ __UBUS_METHOD_NOARG("{method_name}", {handler_name}, {mask}, 0) }}'
            else:
                return f'UBUS_METHOD_NOARG("{method_name}", {handler_name})'
