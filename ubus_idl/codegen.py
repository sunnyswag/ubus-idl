"""C code generator for ubus IDL"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from .ast import (
    Document, ObjectDef, TypeDef, MethodDef, FieldDef, Parameter, Annotation
)
from . import templates


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
    """C code generator"""
    
    def __init__(self, document: Document):
        self.document = document
        self.type_defs: Dict[str, TypeDef] = {}
        self.type_owners: Dict[str, str] = {}  # type_name -> object_name (None for global)
        # Collect all type definitions
        # Global types (outside objects)
        for type_def in document.global_types:
            self.type_defs[type_def.name] = type_def
            self.type_owners[type_def.name] = None
        # Object types
        for obj in document.objects:
            for type_def in obj.types:
                self.type_defs[type_def.name] = type_def
                self.type_owners[type_def.name] = obj.name
    
    def generate(self) -> Dict[str, str]:
        """Generate all code files"""
        result = {}
        
        for obj in self.document.objects:
            header_name = f"{obj.name.lower()}_object.h"
            source_name = f"{obj.name.lower()}_object.c"
            
            result[header_name] = self._generate_header(obj)
            result[source_name] = self._generate_source(obj)
        
        return result
    
    def _generate_header(self, obj: ObjectDef) -> str:
        """Generate header file"""
        # Generate unique header guard based on object name
        obj_name_upper = obj.name.upper().replace("-", "_")
        header_guard = f"__{obj_name_upper}_OBJECT_H__"
        
        lines = [
            templates.HEADER_FILE_HEADER.format(obj_name=obj.name),
            "",
            templates.HEADER_GUARD_START.format(header_guard=header_guard),
            templates.HEADER_GUARD_DEFINE.format(header_guard=header_guard),
            "",
        ]
        lines.extend(templates.HEADER_INCLUDES)
        lines.append(templates.HELPER_MACROS_HEADER)
        lines.extend(templates.HELPER_MACROS)
        
        # Generate struct definitions for global types used by this object
        used_global_types = set()
        for method in obj.methods:
            if method.parameters:
                param = method.parameters[0]
                if not param.name:  # Using defined type
                    type_name = param.type_name
                    if type_name in self.type_owners and self.type_owners[type_name] is None:
                        used_global_types.add(type_name)
        
        for type_name in used_global_types:
            type_def = self.type_defs.get(type_name)
            if type_def:
                struct_code = self._generate_type_struct(None, type_def)
                if struct_code:
                    lines.extend(struct_code)
                    # Generate bit mask macros for optional fields
                    macro_code = self._generate_bitmask_macros(None, type_def)
                    if macro_code:
                        lines.extend(macro_code)
                    lines.append("")
        
        # Generate struct definitions for types in this object
        for type_def in obj.types:
            struct_code = self._generate_type_struct(obj, type_def)
            if struct_code:
                lines.extend(struct_code)
                # Generate bit mask macros for optional fields
                macro_code = self._generate_bitmask_macros(obj, type_def)
                if macro_code:
                    lines.extend(macro_code)
                lines.append("")
        
        # Generate struct definitions for methods with direct parameters
        for method in obj.methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:  # Direct parameters, not using defined type
                    method_name = method.name
                    for ann in method.annotations:
                        if ann.name == "name":
                            method_name = ann.value
                    struct_code = self._generate_method_params_struct(obj, method_name, method.parameters)
                    if struct_code:
                        lines.extend(struct_code)
                        # Generate bit mask macros for optional fields in method parameters
                        optional_params = [p for p in method.parameters if p.name and p.optional]
                        if optional_params:
                            # Determine prefix for macros
                            obj_prefix = obj.name.lower()
                            if method_name.startswith(obj_prefix + "_"):
                                prefix = method_name
                            else:
                                prefix = f"{obj_prefix}_{method_name}"
                            enum_prefix = f"{prefix.upper()}_"
                            for p in optional_params:
                                enum_item = f"{enum_prefix}{p.name.upper()}"
                                macro_name = f"{prefix.upper()}_HAS_{p.name.upper()}"
                                lines.append(f"#define {macro_name} (1U << {enum_item})")
                        lines.append("")
        
        # Function declarations for all handlers (users implement them in other files)
        for method in obj.methods:
            handler_name = self._get_handler_name(obj, method)
            lines.append(
                f"int {handler_name}(struct ubus_context *ctx, "
                f"struct ubus_object *obj, "
                f"struct ubus_request_data *req, "
                f"const char *method, "
                f"struct blob_attr *msg);"
            )
        
        # Serialize/deserialize function declarations (for external use)
        # Collect unique types
        declared_types = set()
        for method in obj.methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:
                    # Direct parameters - use method name
                    method_name = method.name
                    for ann in method.annotations:
                        if ann.name == "name":
                            method_name = ann.value
                            break
                    # Avoid duplicate prefix if method_name already starts with object name
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
                        lines.append(f"int {func_prefix}_deserialize(struct blob_attr *msg, struct {struct_type_name} *params);")
                        lines.append(f"int {func_prefix}_serialize(struct blob_buf *b, const struct {struct_type_name} *params);")
                else:
                    # Using defined type
                    type_name = param.type_name
                    if type_name not in declared_types:
                        declared_types.add(type_name)
                        # Check if type is in object or global
                        owner = self.type_owners.get(type_name)
                        if owner:  # Type is in an object
                            struct_type_name = f"{owner.lower()}_{type_name}"
                            func_prefix = f"{owner.lower()}_{type_name}"
                        else:  # Global type
                            struct_type_name = type_name
                            func_prefix = type_name
                        lines.append(f"int {func_prefix}_deserialize(struct blob_attr *msg, struct {struct_type_name} *params);")
                        lines.append(f"int {func_prefix}_serialize(struct blob_buf *b, const struct {struct_type_name} *params);")
        
        # Object declaration
        lines.extend([
            "",
            f"extern struct ubus_object {obj.name.lower()}_object;",
            "",
            f"#endif /* {header_guard} */",
        ])
        
        return "\n".join(lines)
    
    def _generate_type_struct(self, obj: Optional[ObjectDef], type_def: TypeDef) -> List[str]:
        """Generate C struct for type definition"""
        lines = []
        if obj:
            struct_name = f"{obj.name.lower()}_{type_def.name}"
        else:
            # Global type, no prefix
            struct_name = type_def.name
        
        lines.append(templates.STRUCT_START.format(struct_name=struct_name))
        # Count optional fields
        optional_fields = [f for f in type_def.fields if f.optional]
        for field in type_def.fields:
            c_type = self._get_struct_field_type(field.type_name, field.optional)
            lines.append(templates.STRUCT_FIELD.format(c_type=c_type, field_name=field.name))
        # Add single flag field for all optional fields (bitmask)
        if optional_fields:
            lines.append(templates.STRUCT_HAS_FIELDS)
        lines.append(templates.STRUCT_END)
        
        return lines
    
    def _generate_bitmask_macros(self, obj: Optional[ObjectDef], type_def: TypeDef) -> List[str]:
        """Generate bit mask macros for optional fields"""
        lines = []
        optional_fields = [f for f in type_def.fields if f.optional]
        if not optional_fields:
            return lines
        
        # Determine prefix
        if obj:
            prefix = f"{obj.name.lower()}_{type_def.name}"
        else:
            prefix = type_def.name
        
        enum_prefix = f"{prefix.upper()}_"
        
        # Generate macros for each optional field
        for field in optional_fields:
            enum_item = f"{enum_prefix}{field.name.upper()}"
            macro_name = f"{prefix.upper()}_HAS_{field.name.upper()}"
            lines.append(templates.BITMASK_MACRO.format(macro_name=macro_name, enum_item=enum_item))
        
        return lines
    
    def _generate_helper_macros(self) -> List[str]:
        """Generate helper macros for optional field operations"""
        lines = [
            templates.HELPER_MACROS_HEADER,
        ]
        lines.extend(templates.HELPER_MACROS)
        lines.extend([
            templates.HELPER_MACROS_DESERIALIZE_HEADER,
        ])
        lines.extend(templates.HELPER_MACROS_DESERIALIZE)
        lines.extend([
            templates.HELPER_MACROS_SERIALIZE_HEADER,
        ])
        lines.extend(templates.HELPER_MACROS_SERIALIZE)
        return lines
    
    def _generate_method_params_struct(self, obj: ObjectDef, method_name: str, parameters: List[Parameter]) -> List[str]:
        """Generate C struct for method parameters"""
        lines = []
        # Avoid duplicate prefix if method_name already starts with object name
        obj_prefix = obj.name.lower()
        if method_name.startswith(obj_prefix + "_"):
            # Method name already has object prefix, don't add it again
            struct_name = f"{method_name}_params"
        else:
            struct_name = f"{obj_prefix}_{method_name}_params"
        
        lines.append(templates.STRUCT_START.format(struct_name=struct_name))
        # Count optional fields
        optional_fields = [p for p in parameters if p.name and p.optional]
        for param in parameters:
            if param.name:
                c_type = self._get_struct_field_type(param.type_name, param.optional)
                lines.append(templates.STRUCT_FIELD.format(c_type=c_type, field_name=param.name))
        # Add single flag field for all optional fields (bitmask)
        if optional_fields:
            lines.append(templates.STRUCT_HAS_FIELDS)
        lines.append(templates.STRUCT_END)
        
        return lines
    
    def _get_struct_field_type(self, type_name: str, optional: bool) -> str:
        """Get C type for struct field"""
        return TypeFactory.get_struct_field_type(type_name)
    
    def _generate_source(self, obj: ObjectDef) -> str:
        """Generate source file"""
        lines = [
            templates.SOURCE_FILE_HEADER.format(obj_name=obj.name),
            "",
        ]
        # Add includes
        for include_line in templates.SOURCE_INCLUDES:
            if '{header_file}' in include_line:
                lines.append(include_line.format(header_file=f"{obj.name.lower()}_object.h"))
            else:
                lines.append(include_line)
        
        # Add helper macros for optional field operations (only once per source file)
        helper_macros = self._generate_helper_macros()
        lines.extend(helper_macros)
        
        lines.append(templates.SERIALIZE_MACRO_HEADER)
        lines.extend(templates.SERIALIZE_MACRO)
        
        # Collect all unique types that need policies
        # 1. Direct parameter methods (use method name from @name annotation or method.name)
        # 2. Type-based methods (use type name)
        policy_types = {}  # type_name -> (is_method_params, name)
        for method in obj.methods:
            if method.parameters:
                param = method.parameters[0]
                if param.name:
                    # Direct parameters - use method name
                    method_name = method.name
                    for ann in method.annotations:
                        if ann.name == "name":
                            method_name = ann.value
                            break
                    # Avoid duplicate prefix if method_name already starts with object name
                    obj_prefix = obj.name.lower()
                    if method_name.startswith(obj_prefix + "_"):
                        type_key = f"{method_name}_params"
                    else:
                        type_key = f"{obj_prefix}_{method_name}_params"
                    policy_types[type_key] = (True, method_name)
                else:
                    # Using defined type
                    type_name = param.type_name
                    if type_name not in policy_types:
                        policy_types[type_name] = (False, type_name)
        
        # Generate policies and serialize/deserialize functions for each unique type
        for type_key, (is_method_params, name) in policy_types.items():
            if is_method_params:
                # Generate policy for direct parameters method
                method = None
                for m in obj.methods:
                    if m.parameters and m.parameters[0].name:
                        method_name = m.name
                        for ann in m.annotations:
                            if ann.name == "name":
                                method_name = ann.value
                                break
                        if method_name == name:
                            method = m
                            break
                if method:
                    policy_code = self._generate_policy_for_type(obj, method, name, True)
                    lines.extend(policy_code)
                    lines.append("")
                    serialize_code = self._generate_serialize_deserialize_for_type(obj, method, name, True)
                    if serialize_code:
                        lines.extend(serialize_code)
                        lines.append("")
            else:
                # Generate policy for defined type
                type_def = self.type_defs.get(name)
                if type_def:
                    policy_code = self._generate_policy_for_type(obj, None, name, False)
                    lines.extend(policy_code)
                    lines.append("")
                    serialize_code = self._generate_serialize_deserialize_for_type(obj, None, name, False)
                    if serialize_code:
                        lines.extend(serialize_code)
                        lines.append("")
        
        # Generate handler function only if custom handler is specified
        method_defs = []
        for method in obj.methods:
            if method.custom_handler:
                handler_code = self._generate_handler(obj, method)
                lines.extend(handler_code)
                lines.append("")
            
            # Collect method definitions
            method_defs.append(self._generate_method_def(obj, method))
        
        # Generate method array
        obj_name_lower = obj.name.lower()
        lines.append(templates.METHOD_ARRAY_START.format(obj_name=obj_name_lower))
        for i, method_def in enumerate(method_defs):
            if i == len(method_defs) - 1:
                # Last item, no comma
                lines.append(templates.METHOD_ARRAY_ITEM.format(method_def=method_def))
            else:
                lines.append(templates.METHOD_ARRAY_ITEM_WITH_COMMA.format(method_def=method_def))
        lines.append(templates.METHOD_ARRAY_END)
        lines.append("")
        
        # Generate object_type
        lines.append(
            templates.OBJECT_TYPE_DECL.format(obj_name=obj_name_lower) + "\n" +
            templates.OBJECT_TYPE_DEF.format(obj_name=obj_name_lower) + "\n"
        )
        
        # Generate object
        lines.append(
            templates.OBJECT_START.format(obj_name=obj_name_lower) + "\n" +
            templates.OBJECT_NAME.format(obj_name=obj_name_lower) + "\n" +
            templates.OBJECT_TYPE.format(obj_name=obj_name_lower) + "\n" +
            templates.OBJECT_METHODS.format(obj_name=obj_name_lower) + "\n" +
            templates.OBJECT_N_METHODS.format(obj_name=obj_name_lower) + "\n" +
            templates.OBJECT_END
        )
        
        return "\n".join(lines)
    
    def _generate_policy_for_type(self, obj: ObjectDef, method: MethodDef, type_name: str, is_method_params: bool) -> List[str]:
        """Generate policy enum and array for a type"""
        lines = []
        
        # Determine prefix for enum and policy names
        if is_method_params:
            # Method parameters - avoid duplicate prefix if type_name already starts with object name
            obj_prefix = obj.name.lower()
            if type_name.startswith(obj_prefix + "_"):
                # type_name already has object prefix, don't add it again
                prefix = type_name
            else:
                prefix = f"{obj_prefix}_{type_name}"
        else:
            # Check if type is in object or global
            owner = self.type_owners.get(type_name)
            if owner:  # Type is in an object
                prefix = f"{owner.lower()}_{type_name}"
            else:  # Global type
                prefix = type_name
        
        # Generate enum with prefix
        enum_name = f"__{prefix.upper()}_MAX"
        enum_prefix = f"{prefix.upper()}_"
        
        lines.append(templates.ENUM_START)
        
        # Process parameters
        param_names = []
        if is_method_params and method:
            # Direct parameters
            for param in method.parameters:
                if param.name:
                    enum_item = f"{enum_prefix}{param.name.upper()}"
                    param_names.append((enum_item, param.name, param.type_name))
                    lines.append(templates.ENUM_ITEM.format(enum_item=enum_item))
        else:
            # Using defined type
            type_def = self.type_defs.get(type_name)
            if type_def:
                for field in type_def.fields:
                    enum_item = f"{enum_prefix}{field.name.upper()}"
                    param_names.append((enum_item, field.name, field.type_name))
                    lines.append(templates.ENUM_ITEM.format(enum_item=enum_item))
        
        lines.append(
            templates.ENUM_MAX.format(enum_max=enum_name) + "\n" +
            templates.ENUM_END + "\n"
        )
        
        # Generate policy array with prefix
        policy_name = f"{prefix}_policy"
        lines.append(templates.POLICY_START.format(policy_name=policy_name))
        
        for i, (enum_item, field_name, type_name) in enumerate(param_names):
            blob_type = self._get_blob_type(type_name)
            if i == len(param_names) - 1:
                # Last item, no comma
                lines.append(templates.POLICY_ITEM.format(
                    enum_item=enum_item, field_name=field_name, blob_type=blob_type
                ))
            else:
                lines.append(templates.POLICY_ITEM_WITH_COMMA.format(
                    enum_item=enum_item, field_name=field_name, blob_type=blob_type
                ))
        
        lines.append(templates.POLICY_END)
        
        return lines
    
    def _generate_serialize_deserialize_for_type(self, obj: ObjectDef, method: MethodDef, type_name: str, is_method_params: bool) -> List[str]:
        """Generate serialize/deserialize functions for a type"""
        lines = []
        
        # Determine prefix for enum, policy, and tb names
        if is_method_params:
            # Method parameters - avoid duplicate prefix if type_name already starts with object name
            obj_prefix = obj.name.lower()
            if type_name.startswith(obj_prefix + "_"):
                # type_name already has object prefix, don't add it again
                prefix = type_name
                struct_type_name = f"{type_name}_params"
                func_prefix = type_name
            else:
                prefix = f"{obj_prefix}_{type_name}"
                struct_type_name = f"{obj_prefix}_{type_name}_params"
                func_prefix = f"{obj_prefix}_{type_name}"
        else:
            # Check if type is in object or global
            owner = self.type_owners.get(type_name)
            if owner:  # Type is in an object
                prefix = f"{owner.lower()}_{type_name}"
                struct_type_name = f"{owner.lower()}_{type_name}"
                func_prefix = f"{owner.lower()}_{type_name}"
            else:  # Global type
                prefix = type_name
                struct_type_name = type_name
                func_prefix = type_name
        
        enum_name = f"__{prefix.upper()}_MAX"
        policy_name = f"{prefix}_policy"
        tb_name = f"tb_{prefix}"
        
        # Generate deserialize function (not static, for external use)
        deserialize_func = f"{func_prefix}_deserialize"
        lines.append(
            templates.DESERIALIZE_FUNC_SIGNATURE.format(
                func_name=deserialize_func, struct_type=struct_type_name
            ) + "\n" +
            templates.DESERIALIZE_FUNC_BODY_START + "\n" +
            templates.DESERIALIZE_TB_DECL.format(tb_name=tb_name, enum_max=enum_name) + "\n" +
            templates.DESERIALIZE_PARSE_CHECK.format(
                policy_name=policy_name, tb_name=tb_name
            ) + "\n" +
            templates.DESERIALIZE_PARSE_ERROR + "\n" +
            templates.DESERIALIZE_PARSE_END + "\n"
        )
        
        # Collect required fields first
        required_fields = []
        optional_fields = []
        
        if is_method_params and method:
            # Direct parameters - collect optional fields with their enum name (for bit mask)
            enum_prefix = f"{prefix.upper()}_"
            for p in method.parameters:
                if p.name:
                    enum_item = f"{enum_prefix}{p.name.upper()}"
                    if p.optional:
                        optional_fields.append((p.name, p.type_name, f"params->{p.name}", enum_item))
                    else:
                        required_fields.append((p.name, p.type_name, f"params->{p.name}"))
        else:
            # Using defined type
            type_def = self.type_defs.get(type_name)
            if type_def:
                # Collect optional fields with their enum name (for bit mask)
                enum_prefix = f"{prefix.upper()}_"
                for field in type_def.fields:
                    enum_item = f"{enum_prefix}{field.name.upper()}"
                    if field.optional:
                        optional_fields.append((field.name, field.type_name, f"params->{field.name}", enum_item))
                    else:
                        required_fields.append((field.name, field.type_name, f"params->{field.name}"))
        
        # Check all required fields in one if statement
        if required_fields:
            enum_prefix = f"{prefix.upper()}_"
            check_conditions = []
            for field_name, _, _ in required_fields:
                enum_item = f"{enum_prefix}{field_name.upper()}"
                check_conditions.append(f"!{tb_name}[{enum_item}]")
            
            if len(check_conditions) == 1:
                check_line = templates.REQUIRED_FIELD_CHECK_SINGLE.format(condition=check_conditions[0])
            else:
                # Combine all checks with ||
                combined_check = " || ".join(check_conditions)
                check_line = templates.REQUIRED_FIELD_CHECK_MULTIPLE.format(conditions=combined_check)
            lines.append(
                check_line + "\n" +
                templates.REQUIRED_FIELD_CHECK_ERROR + "\n" +
                templates.REQUIRED_FIELD_CHECK_END + "\n"
            )
        
        # Initialize has_fields to 0 if there are optional fields
        if optional_fields:
            lines.append(templates.DESERIALIZE_INIT_HAS_FIELDS + "\n")
        
        # Fill struct fields - all required fields first, then optional fields
        for field_name, field_type, target in required_fields:
            self._generate_deserialize_field_assignment(lines, tb_name, prefix, field_name, field_type, target)
        
        for field_info in optional_fields:
            if len(field_info) == 4:
                field_name, field_type, target, enum_item = field_info
            else:
                # Backward compatibility
                field_name, field_type, target = field_info[:3]
                enum_prefix = f"{prefix.upper()}_"
                enum_item = f"{enum_prefix}{field_name.upper()}"
            self._generate_deserialize_field_assignment(lines, tb_name, prefix, field_name, field_type, target, optional=True, enum_item=enum_item)
        
        lines.append(
            templates.DESERIALIZE_RETURN_OK + "\n" +
            templates.DESERIALIZE_FUNC_END + "\n"
        )
        
        # Generate serialize function (not static, returns int)
        # Note: Serialize doesn't validate required fields as it's for output
        serialize_func = f"{func_prefix}_serialize"
        lines.append(
            templates.SERIALIZE_FUNC_SIGNATURE.format(
                func_name=serialize_func, struct_type=struct_type_name
            ) + "\n" +
            templates.SERIALIZE_FUNC_BODY_START
        )
        # Only declare ret if we need it (for array/unspec/custom types)
        needs_ret = False
        if is_method_params and method:
            for p in method.parameters:
                if p.name and p.type_name in ["array", "unspec"]:
                    needs_ret = True
                    break
        else:
            type_def = self.type_defs.get(type_name)
            if type_def:
                for field in type_def.fields:
                    if field.type_name in ["array", "unspec"]:
                        needs_ret = True
                        break
        if needs_ret:
            lines.append(templates.SERIALIZE_RET_DECL + "\n")
        
        # Generate serialize code from struct
        if is_method_params and method:
            # Direct parameters - track enum item and prefix for optional fields
            enum_prefix = f"{prefix.upper()}_"
            for p in method.parameters:
                if p.name:
                    enum_item = f"{enum_prefix}{p.name.upper()}"
                    if p.optional:
                        self._generate_serialize_field_from_struct_with_check(lines, f"params->{p.name}", p.name, p.type_name, p.optional, enum_item=enum_item, prefix=prefix)
                    else:
                        self._generate_serialize_field_from_struct_with_check(lines, f"params->{p.name}", p.name, p.type_name, False)
        else:
            # Using defined type
            type_def = self.type_defs.get(type_name)
            if type_def:
                # Track enum item and prefix for optional fields
                enum_prefix = f"{prefix.upper()}_"
                for field in type_def.fields:
                    enum_item = f"{enum_prefix}{field.name.upper()}"
                    if field.optional:
                        self._generate_serialize_field_from_struct_with_check(lines, f"params->{field.name}", field.name, field.type_name, field.optional, enum_item=enum_item, prefix=prefix)
                    else:
                        self._generate_serialize_field_from_struct_with_check(lines, f"params->{field.name}", field.name, field.type_name, field.optional)
        
        lines.append(
            templates.SERIALIZE_RETURN_OK + "\n" +
            templates.SERIALIZE_FUNC_END + "\n"
        )
        
        # No need to generate has_* functions - users can use UBUS_IDL_HAS_FIELD macro directly
        
        return lines
    
    def _generate_deserialize_field_assignment(self, lines: List[str], tb_name: str, prefix: str,
                                              field_name: str, field_type: str, target: str, optional: bool = False, enum_item: str = None):
        """Generate code to assign a field from blob_attr to struct (without checking)"""
        enum_prefix = f"{prefix.upper()}_"
        if enum_item is None:
            enum_item = f"{enum_prefix}{field_name.upper()}"
        
        if optional:
            # Optional fields - use macro with bitmask flag
            # Extract struct name from target (e.g., "params->field" -> "params")
            struct_var = target.split("->")[0]
            # Use macro for bit mask (will be defined in header)
            macro_name = f"{prefix.upper()}_HAS_{field_name.upper()}"
            code = templates.get_optional_field_assign_code(
                field_type, target, tb_name, enum_item, struct_var, macro_name
            )
            lines.extend(code.split('\n'))
        else:
            # Required fields - direct assignment
            code = templates.get_field_assign_code(field_type, target, tb_name, enum_item)
            lines.append(code)
    
    def _generate_deserialize_field(self, lines: List[str], tb_name: str, prefix: str, 
                                    field_name: str, field_type: str, optional: bool, target: str):
        """Generate code to deserialize a field from blob_attr to struct (deprecated - use _generate_deserialize_field_assignment)"""
        # This function is kept for backward compatibility but should not be used
        # Use _generate_deserialize_field_assignment instead
        self._generate_deserialize_field_assignment(lines, tb_name, prefix, field_name, field_type, target, optional)
    
    def _generate_serialize_field_from_struct_with_check(self, lines: List[str], field_access: str, 
                                             field_name: str, type_name: str, optional: bool, enum_item: str = None, prefix: str = None):
        """Generate code to serialize a struct field to blob_buf with error checking"""
        if optional:
            # Optional fields: use macro for serialization
            # Extract struct variable name from field_access (e.g., "params->field" -> "params")
            struct_var = field_access.split("->")[0]
            # Generate macro name from prefix
            if prefix:
                macro_name = f"{prefix.upper()}_HAS_{field_name.upper()}"
            elif enum_item:
                # Fallback: extract prefix from enum_item
                prefix = "_".join(enum_item.split("_")[:-1])  # Remove last part (field name)
                macro_name = f"{prefix}_HAS_{field_name.upper()}"
            else:
                # Fallback if neither provided
                macro_name = f"(1U << 0)"
            
            code = templates.get_serialize_add_optional_code(
                type_name, field_name, field_access, struct_var, macro_name
            )
            lines.extend(code.split('\n'))
        else:
            # Required fields - use macros for error checking
            code = templates.get_serialize_add_code(type_name, field_name, field_access)
            lines.extend(code.split('\n'))
    
    def _get_c_type(self, type_name: str, var_name: str, optional: bool = False) -> str:
        """Get C type declaration for parameter"""
        return TypeFactory.get_c_type_decl(type_name, var_name, optional)
    
    def _generate_serialize_field(self, lines: List[str], field_name: str, type_name: str, optional: bool):
        """Generate code to serialize a field to blob_buf"""
        type_info = TypeFactory.get_type_info(type_name)
        
        if optional:
            # For optional string, check if not NULL
            if type_name == "string":
                lines.append(f"    if ({field_name} && {field_name}[0] != '\\0') {{")
            else:
                lines.append(f"    if ({field_name}) {{")
        
        if type_info:
            if type_info.use_field_api:
                # Use blobmsg_add_field for array/unspec
                blob_type = type_info.blob_type
                if optional:
                    lines.append(f'        if ({field_name}) {{')
                    lines.append(f'            blobmsg_add_field(b, {blob_type}, "{field_name}", blob_data({field_name}), blob_len({field_name}));')
                    lines.append(f'        }}')
                else:
                    lines.append(f'        blobmsg_add_field(b, {blob_type}, "{field_name}", blob_data({field_name}), blob_len({field_name}));')
            else:
                # Use blobmsg_add_xxx
                add_func = type_info.add_func
                if type_name == "bool":
                    # Special handling for bool
                    if optional:
                        lines.append(f'        blobmsg_add_{add_func}(b, "{field_name}", *{field_name} ? 1 : 0);')
                    else:
                        lines.append(f'        blobmsg_add_{add_func}(b, "{field_name}", {field_name} ? 1 : 0);')
                else:
                    if optional:
                        lines.append(f'        blobmsg_add_{add_func}(b, "{field_name}", *{field_name});')
                    else:
                        lines.append(f'        blobmsg_add_{add_func}(b, "{field_name}", {field_name});')
        else:
            # Custom type
            lines.append(f'        blobmsg_add_field(b, BLOBMSG_TYPE_TABLE, "{field_name}", '
                       f'blob_data({field_name}_attr), blob_len({field_name}_attr));')
        
        if optional:
            lines.append("    }")
    
    def _generate_handler(self, obj: ObjectDef, method: MethodDef) -> List[str]:
        """Generate handler function"""
        lines = []
        
        handler_name = self._get_handler_name(obj, method)
        method_name = method.name
        
        # Determine actual method name (might be overridden by @name annotation)
        for ann in method.annotations:
            if ann.name == "name":
                method_name = ann.value
        
        # Generate enum name
        enum_name = f"__{method_name.upper()}_MAX"
        policy_name = f"{method_name}_policy"
        tb_name = f"tb_{method_name}"
        
        # Only generate handler implementation if custom_handler is specified
        # Otherwise, user implements it in other files
        if not method.custom_handler:
            return []  # Don't generate handler implementation
        
        lines.append(
            templates.HANDLER_FUNC_SIGNATURE.format(handler_name=handler_name) + "\n" +
            templates.HANDLER_FUNC_BODY_START
        )
        
        # Determine struct type name and deserialize function name
        struct_type_name = None
        deserialize_func = None
        if method.parameters:
            param = method.parameters[0]
            if param.name:
                # Avoid duplicate prefix if method_name already starts with object name
                obj_prefix = obj.name.lower()
                if method_name.startswith(obj_prefix + "_"):
                    struct_type_name = f"{method_name}_params"
                    deserialize_func = f"{method_name}_deserialize"
                else:
                    struct_type_name = f"{obj_prefix}_{method_name}_params"
                    deserialize_func = f"{obj_prefix}_{method_name}_deserialize"
            else:
                # Check if type is in object or global
                owner = self.type_owners.get(param.type_name)
                if owner:  # Type is in an object
                    struct_type_name = f"{owner.lower()}_{param.type_name}"
                    deserialize_func = f"{owner.lower()}_{param.type_name}_deserialize"
                else:  # Global type
                    struct_type_name = param.type_name
                    deserialize_func = f"{param.type_name}_deserialize"
        
        # Only generate deserialize code if method has parameters
        if method.parameters:
            lines.append(
                templates.HANDLER_PARAMS_DECL.format(struct_type=struct_type_name) + "\n" +
                "\n" +
                templates.HANDLER_DESERIALIZE_CHECK.format(deserialize_func=deserialize_func) + "\n" +
                templates.HANDLER_DESERIALIZE_ERROR + "\n" +
                templates.HANDLER_DESERIALIZE_END + "\n" +
                "\n" +
                templates.HANDLER_TODO_PARAMS + "\n" +
                templates.HANDLER_EXAMPLE_PARAMS + "\n"
            )
        
        # Check if custom handler is specified
        if method.custom_handler:
            # Include custom handler file
            handler_file = method.custom_handler
            if not handler_file.endswith('.c') and not handler_file.endswith('.h'):
                handler_file = f"{handler_file}.c"
            lines.append(
                templates.HANDLER_CUSTOM_COMMENT.format(handler_file=handler_file) + "\n" +
                templates.HANDLER_CUSTOM_INCLUDE + "\n" +
                templates.HANDLER_CUSTOM_INCLUDE_FILE.format(handler_file=handler_file) + "\n" +
                "\n" +
                templates.HANDLER_CUSTOM_CALL + "\n" +
                templates.HANDLER_CUSTOM_CALL_FUNC.format(handler_name=method.custom_handler)
            )
        else:
            lines.append(
                templates.HANDLER_TODO_IMPLEMENT + "\n" +
                templates.HANDLER_TODO_REPLY + "\n" +
                templates.HANDLER_TODO_EXAMPLE + "\n" +
                templates.HANDLER_TODO_BLOB_BUF + "\n" +
                templates.HANDLER_TODO_INIT + "\n" +
                templates.HANDLER_TODO_SERIALIZE.format(serialize_func=f"{method_name}_serialize") + "\n" +
                templates.HANDLER_TODO_SEND
            )
        
        lines.append(
            "\n" +
            templates.HANDLER_RETURN_OK + "\n" +
            templates.HANDLER_FUNC_END
        )
        
        return lines
    
    def _generate_param_extraction(
        self, lines: List[str], method_name: str, 
        field_name: str, type_name: str, var_name: str, optional: bool
    ):
        """Generate parameter extraction code"""
        enum_item = f"{method_name.upper()}_{field_name.upper()}"
        tb_name = f"tb_{method_name}"
        
        # Avoid name conflict with function parameter 'msg'
        if var_name == "msg":
            var_name = "msg_param"
        
        if optional:
            lines.append(f"    // Optional parameter: {field_name}")
            lines.append(f"    if ({tb_name}[{enum_item}]) {{")
        
        type_info = TypeFactory.get_type_info(type_name)
        if type_info:
            if type_info.use_field_api:
                # Direct assignment for array/unspec
                lines.append(f"        {type_info.c_type}{var_name} = {tb_name}[{enum_item}];")
            else:
                # Use blobmsg_get_xxx
                get_func = type_info.get_func
                c_type = type_info.c_type
                if type_name == "bool":
                    # Special handling for bool
                    lines.append(
                        f"        {c_type} {var_name} = "
                        f"blobmsg_get_{get_func}({tb_name}[{enum_item}]) != 0;"
                    )
                else:
                    lines.append(
                        f"        {c_type} {var_name} = "
                        f"blobmsg_get_{get_func}({tb_name}[{enum_item}]);"
                    )
        else:
            # Custom type, needs nested parsing
            lines.append(
                f"        // TODO: Parse custom type {type_name}"
            )
            lines.append(
                f"        // struct blob_attr *{var_name}_attr = {tb_name}[{enum_item}];"
            )
        
        if optional:
            lines.append("    }")
        
        lines.append("")
    
    def _generate_method_def(self, obj: ObjectDef, method: MethodDef) -> str:
        """Generate method definition string"""
        # Determine method name (might be overridden by @name annotation)
        method_name = method.name
        for ann in method.annotations:
            if ann.name == "name":
                method_name = ann.value
        
        handler_name = self._get_handler_name(obj, method)
        
        # Determine policy name based on parameter type
        if method.parameters:
            param = method.parameters[0]
            if param.name:
                # Direct parameters - use object prefix + method name
                # But avoid duplicate prefix if method_name already starts with object name
                obj_prefix = obj.name.lower()
                if method_name.startswith(obj_prefix + "_"):
                    # Method name already has object prefix, don't add it again
                    policy_name = f"{method_name}_policy"
                else:
                    policy_name = f"{obj_prefix}_{method_name}_policy"
            else:
                # Using defined type - check if type is in object or global
                owner = self.type_owners.get(param.type_name)
                if owner:  # Type is in an object
                    policy_name = f"{owner.lower()}_{param.type_name}_policy"
                else:  # Global type
                    policy_name = f"{param.type_name}_policy"
        else:
            policy_name = None
        
        # Get mask and tags
        mask = 0
        tags = 0
        for ann in method.annotations:
            if ann.name == "mask":
                if isinstance(ann.value, int):
                    mask = ann.value
                elif isinstance(ann.value, str):
                    # Might be "0x1" format
                    mask = int(ann.value, 16) if ann.value.startswith("0x") or ann.value.startswith("0X") else int(ann.value)
            elif ann.name == "tag":
                if isinstance(ann.value, int):
                    tags = ann.value
                elif isinstance(ann.value, str):
                    # Might be "0x1" format
                    tags = int(ann.value, 16) if ann.value.startswith("0x") or ann.value.startswith("0X") else int(ann.value)
        
        # Check if has parameters
        has_params = bool(method.parameters)
        
        if has_params:
            if mask > 0 and tags > 0:
                # Both mask and tags, need manual construction (ubus has no ready macro)
                # __UBUS_METHOD(_name, _handler, _mask, _policy, _tags)
                return f'{{ __UBUS_METHOD("{method_name}", {handler_name}, {mask}, {policy_name}, {tags}) }}'
            elif tags > 0:
                return f'UBUS_METHOD_TAG("{method_name}", {handler_name}, {policy_name}, {tags})'
            elif mask > 0:
                return f'UBUS_METHOD_MASK("{method_name}", {handler_name}, {policy_name}, {mask})'
            else:
                return f'UBUS_METHOD("{method_name}", {handler_name}, {policy_name})'
        else:
            if mask > 0 and tags > 0:
                # Both mask and tags, need manual construction
                # __UBUS_METHOD_NOARG(_name, _handler, _mask, _tags)
                return f'{{ __UBUS_METHOD_NOARG("{method_name}", {handler_name}, {mask}, {tags}) }}'
            elif tags > 0:
                return f'UBUS_METHOD_TAG_NOARG("{method_name}", {handler_name}, {tags})'
            elif mask > 0:
                # UBUS_METHOD_MASK_NOARG doesn't exist, use __UBUS_METHOD_NOARG
                return f'{{ __UBUS_METHOD_NOARG("{method_name}", {handler_name}, {mask}, 0) }}'
            else:
                return f'UBUS_METHOD_NOARG("{method_name}", {handler_name})'
    
    def _get_handler_name(self, obj: ObjectDef, method: MethodDef) -> str:
        """Get handler function name"""
        if method.custom_handler:
            return method.custom_handler
        
        # Auto-generate: {object_name}_{actual_method_name}_handler
        # Use actual method name (might be overridden by @name annotation)
        # If @name is used, use that; otherwise use method.name
        method_name = method.name
        for ann in method.annotations:
            if ann.name == "name":
                method_name = ann.value
                break
        
        # If method_name already starts with object name, don't duplicate it
        obj_prefix = f"{obj.name.lower()}_"
        if method_name.startswith(obj_prefix):
            return f"{method_name}_handler"
        else:
            return f"{obj.name.lower()}_{method_name}_handler"
    
    def _get_blob_type(self, type_name: str) -> str:
        """Get BLOBMSG_TYPE constant"""
        return TypeFactory.get_blob_type(type_name)

