"""C code generator for ubus IDL using Jinja2 templates"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .ast import (
    Document, ObjectDef, TypeDef, MethodDef, FieldDef, Parameter, Annotation
)


@dataclass
class TypeInfo:
    """Type information for code generation"""
    c_type: str  # C type name (e.g., "int32_t", "const char *")
    blob_type: str  # BLOBMSG_TYPE constant
    get_func: str  # blobmsg_get function name (e.g., "u32", "string")
    add_func: str  # blobmsg_add function name (e.g., "u32", "string")
    is_pointer: bool = False  # Whether the type is a pointer
    use_field_api: bool = False  # Whether to use blobmsg_add_field instead of blobmsg_add_xxx


class TypeFactory:
    """Factory for type information"""
    
    _type_info: Dict[str, TypeInfo] = {
        "string": TypeInfo(
            c_type="const char *",
            blob_type="BLOBMSG_TYPE_STRING",
            get_func="string",
            add_func="string",
            is_pointer=True,
        ),
        "int8": TypeInfo(
            c_type="int8_t",
            blob_type="BLOBMSG_TYPE_INT8",
            get_func="u8",
            add_func="u8",
        ),
        "int16": TypeInfo(
            c_type="int16_t",
            blob_type="BLOBMSG_TYPE_INT16",
            get_func="u16",
            add_func="u16",
        ),
        "int32": TypeInfo(
            c_type="int32_t",
            blob_type="BLOBMSG_TYPE_INT32",
            get_func="u32",
            add_func="u32",
        ),
        "int64": TypeInfo(
            c_type="int64_t",
            blob_type="BLOBMSG_TYPE_INT64",
            get_func="u64",
            add_func="u64",
        ),
        "bool": TypeInfo(
            c_type="bool",
            blob_type="BLOBMSG_TYPE_BOOL",
            get_func="u8",
            add_func="u8",
        ),
        "double": TypeInfo(
            c_type="double",
            blob_type="BLOBMSG_TYPE_DOUBLE",
            get_func="double",
            add_func="double",
        ),
        "array": TypeInfo(
            c_type="struct blob_attr *",
            blob_type="BLOBMSG_TYPE_ARRAY",
            get_func="",  # Direct assignment
            add_func="",  # Use blobmsg_add_field
            is_pointer=True,
            use_field_api=True,
        ),
        "unspec": TypeInfo(
            c_type="struct blob_attr *",
            blob_type="BLOBMSG_TYPE_UNSPEC",
            get_func="",  # Direct assignment
            add_func="",  # Use blobmsg_add_field
            is_pointer=True,
            use_field_api=True,
        ),
    }
    
    @classmethod
    def get_type_info(cls, type_name: str) -> Optional[TypeInfo]:
        """Get type information for a given type name"""
        return cls._type_info.get(type_name)
    
    @classmethod
    def get_blob_type(cls, type_name: str) -> str:
        """Get BLOBMSG_TYPE constant for a type"""
        type_info = cls.get_type_info(type_name)
        if type_info:
            return type_info.blob_type
        # Custom type uses TABLE
        return "BLOBMSG_TYPE_TABLE"
    
    @classmethod
    def get_struct_field_type(cls, type_name: str) -> str:
        """Get C type for struct field"""
        type_info = cls.get_type_info(type_name)
        if type_info:
            return type_info.c_type
        # Custom type - use pointer to struct
        return f"struct {type_name} *"
    
    @classmethod
    def get_c_type_decl(cls, type_name: str, var_name: str, optional: bool = False) -> str:
        """Get C type declaration for parameter"""
        type_info = cls.get_type_info(type_name)
        if type_info:
            if optional and not type_info.is_pointer:
                # For optional non-pointer types, use pointer
                return f"{type_info.c_type} *{var_name}"
            elif type_info.is_pointer:
                # Pointer types don't need * for optional
                return f"{type_info.c_type}{var_name}"
            else:
                return f"{type_info.c_type} {var_name}"
        # Custom type
        return f"struct blob_attr *{var_name}_attr"


class CodeGenerator:
    """C code generator using Jinja2 templates"""
    
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
    
    def generate(self) -> Dict[str, str]:
        """Generate all code files"""
        result = {}
        
        for obj in self.document.objects:
            header_name = f"{obj.name.lower()}_object.h"
            source_name = f"{obj.name.lower()}_object.c"
            
            # Prepare template context
            context = self._prepare_context(obj)
            
            # Render templates
            header_template = self.env.get_template('object.h.j2')
            source_template = self.env.get_template('object.c.j2')
            
            result[header_name] = header_template.render(**context)
            result[source_name] = source_template.render(**context)
        
        return result
    
    def _prepare_context(self, obj: ObjectDef) -> Dict:
        """Prepare template context data"""
        obj_name_lower = obj.name.lower()
        obj_name_upper = obj.name.upper().replace("-", "_")
        header_guard = f"__{obj_name_upper}_OBJECT_H__"
        
        # Collect global types used by this object
        used_global_types = set()
        for method in obj.methods:
            if method.parameters:
                param = method.parameters[0]
                if not param.name:  # Using defined type
                    type_name = param.type_name
                    if type_name in self.type_owners and self.type_owners[type_name] is None:
                        used_global_types.add(type_name)
        
        global_types = []
        for type_name in used_global_types:
            type_def = self.type_defs.get(type_name)
            if type_def:
                global_types.append(self._type_to_dict(None, type_def))
        
        # Object types
        object_types = [self._type_to_dict(obj, t) for t in obj.types]
        
        # Method parameters structs
        method_params = []
        for method in obj.methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:  # Direct parameters
                    method_name = self._get_method_name(method)
                    method_params_dict = self._method_params_to_dict(obj, method_name, method.parameters)
                    # 统一字段名，使用 fields 而不是 params
                    method_params_dict['fields'] = method_params_dict.pop('params')
                    method_params_dict['has_optional_fields'] = method_params_dict.pop('has_optional_params')
                    method_params.append(method_params_dict)
        
        # All methods info
        all_methods = []
        for method in obj.methods:
            all_methods.append(self._method_to_dict(obj, method))
        
        # Serialize/deserialize types
        serialize_types = []
        declared_types = set()
        for method in obj.methods:
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
        
        # Policy types for source file
        policy_types = []
        policy_type_keys = {}
        for method in obj.methods:
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
        
        # Custom handlers
        custom_handlers = []
        for method in obj.methods:
            if method.custom_handler:
                custom_handlers.append(self._custom_handler_to_dict(obj, method))
        
        # 合并所有结构体定义为一个统一列表
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
            'all_structs': all_structs,  # 统一的结构体列表
            'all_methods': all_methods,
            'serialize_types': serialize_types,
            'policy_types': policy_types,
            'custom_handlers': custom_handlers,
        }
    
    def _type_to_dict(self, obj: Optional[ObjectDef], type_def: TypeDef) -> Dict:
        """Convert type definition to dictionary for template"""
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
                field_dict['macro_name'] = f"{prefix.upper()}_HAS_{field.name.upper()}"
            fields.append(field_dict)
        
        return {
            'name': type_def.name,
            'struct_name': prefix,
            'prefix': prefix,
            'enum_prefix': enum_prefix,
            'fields': fields,
            'optional_fields': [f for f in fields if f['optional']],
            'has_optional_fields': bool(optional_fields),
        }
    
    def _method_params_to_dict(self, obj: ObjectDef, method_name: str, parameters: List[Parameter]) -> Dict:
        """Convert method parameters to dictionary for template"""
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
                params.append(param_dict)
        
        return {
            'struct_name': f"{prefix}_params",
            'prefix': prefix,
            'prefix_upper': prefix.upper(),
            'params': params,
            'optional_params': [p for p in params if p['optional']],
            'has_optional_params': bool(optional_params),
        }
    
    def _method_to_dict(self, obj: ObjectDef, method: MethodDef) -> Dict:
        """Convert method to dictionary for template"""
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
                        field_dict['macro_name'] = f"{prefix.upper()}_HAS_{param.name.upper()}"
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
                return None
            
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
                    field_dict['macro_name'] = f"{prefix.upper()}_HAS_{field.name.upper()}"
                    optional_fields.append(field_dict)
                else:
                    required_fields.append(field_dict)
                fields.append(field_dict)
        
        enum_items = [f['enum_item'] for f in fields]
        enum_max = f"__{prefix.upper()}_MAX"
        policy_name = f"{prefix}_policy"
        tb_name = f"tb_{prefix}"
        
        # Check if needs ret variable
        needs_ret = any(f['type_name'] in ['array', 'unspec'] for f in fields)
        
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
        
        # Determine policy name
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
        
        # Get mask and tags
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
