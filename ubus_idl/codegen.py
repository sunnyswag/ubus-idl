"""C code generator for ubus IDL"""

from typing import Dict, List, Optional
from .ast import (
    Document, ObjectDef, TypeDef, MethodDef, FieldDef, Parameter, Annotation
)


# Type mapping: IDL type -> BLOBMSG_TYPE
TYPE_MAP = {
    "int8": "BLOBMSG_TYPE_INT8",
    "int16": "BLOBMSG_TYPE_INT16",
    "int32": "BLOBMSG_TYPE_INT32",
    "int64": "BLOBMSG_TYPE_INT64",
    "string": "BLOBMSG_TYPE_STRING",
    "bool": "BLOBMSG_TYPE_BOOL",
    "double": "BLOBMSG_TYPE_DOUBLE",
    "array": "BLOBMSG_TYPE_ARRAY",
    "unspec": "BLOBMSG_TYPE_UNSPEC",
    # "table" is used for custom types automatically
}


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
            f"/* Generated from ubus IDL - {obj.name} */",
            "",
            f"#ifndef {header_guard}",
            f"#define {header_guard}",
            "",
            "#include <libubus.h>",
            "#include <stdint.h>",
            "",
            "/* Helper macros for optional field operations */",
            "#define UBUS_IDL_HAS_FIELD(params, mask) ((params)->has_fields & (mask))",
            "#define UBUS_IDL_SET_FIELD(params, mask) ((params)->has_fields |= (mask))",
            "#define UBUS_IDL_CLEAR_FIELD(params, mask) ((params)->has_fields &= ~(mask))",
            "",
        ]
        
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
        
        lines.append(f"struct {struct_name} {{")
        # Count optional fields
        optional_fields = [f for f in type_def.fields if f.optional]
        for field in type_def.fields:
            c_type = self._get_struct_field_type(field.type_name, field.optional)
            lines.append(f"    {c_type} {field.name};")
        # Add single flag field for all optional fields (bitmask)
        if optional_fields:
            lines.append(f"    unsigned int has_fields;")
        lines.append("};")
        
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
            lines.append(f"#define {macro_name} (1U << {enum_item})")
        
        return lines
    
    def _generate_helper_macros(self) -> List[str]:
        """Generate helper macros for optional field operations"""
        lines = [
            "/* Helper macros for optional field operations */",
            "#define UBUS_IDL_HAS_FIELD(params, mask) ((params)->has_fields & (mask))",
            "#define UBUS_IDL_SET_FIELD(params, mask) ((params)->has_fields |= (mask))",
            "#define UBUS_IDL_CLEAR_FIELD(params, mask) ((params)->has_fields &= ~(mask))",
            "",
            "/* Helper macros for optional field deserialization */",
            "#define UBUS_IDL_GET_OPTIONAL(type, tb, enum, field, params, mask) \\",
            "    do { \\",
            "        if ((tb)[(enum)]) { \\",
            "            (field) = blobmsg_get_##type((tb)[(enum)]); \\",
            "            UBUS_IDL_SET_FIELD((params), (mask)); \\",
            "        } \\",
            "    } while (0)",
            "",
            "/* Helper macros for optional field serialization */",
            "#define UBUS_IDL_ADD_OPTIONAL(type, b, name, field, params, mask) \\",
            "    do { \\",
            "        if (UBUS_IDL_HAS_FIELD((params), (mask))) { \\",
            "            blobmsg_add_##type((b), (name), (field)); \\",
            "        } \\",
            "    } while (0)",
            "",
        ]
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
        
        lines.append(f"struct {struct_name} {{")
        # Count optional fields
        optional_fields = [p for p in parameters if p.name and p.optional]
        for param in parameters:
            if param.name:
                c_type = self._get_struct_field_type(param.type_name, param.optional)
                lines.append(f"    {c_type} {param.name};")
        # Add single flag field for all optional fields (bitmask)
        if optional_fields:
            lines.append(f"    unsigned int has_fields;")
        lines.append("};")
        
        return lines
    
    def _get_struct_field_type(self, type_name: str, optional: bool) -> str:
        """Get C type for struct field"""
        if type_name == "string":
            return "const char *"
        elif type_name == "int8":
            return "int8_t"
        elif type_name == "int16":
            return "int16_t"
        elif type_name == "int32":
            return "int32_t"
        elif type_name == "int64":
            return "int64_t"
        elif type_name == "bool":
            return "bool"
        elif type_name == "double":
            return "double"
        elif type_name == "array":
            # Array type - use blob_attr pointer
            return "struct blob_attr *"
        elif type_name == "unspec":
            # Unspec type - use blob_attr pointer
            return "struct blob_attr *"
        else:
            # Custom type - use pointer to struct
            return f"struct {type_name} *"
    
    def _generate_source(self, obj: ObjectDef) -> str:
        """Generate source file"""
        lines = [
            f"/* Generated from ubus IDL - {obj.name} */",
            "",
            "#include <libubox/blobmsg_json.h>",
            "#include <libubus.h>",
            f'#include "{obj.name.lower()}_object.h"',
            "",
        ]
        
        # Add helper macros for optional field operations (only once per source file)
        helper_macros = self._generate_helper_macros()
        lines.extend(helper_macros)
        
        lines.append("/* Helper macros for field serialization with error checking */")
        lines.append("#define UBUS_IDL_ADD(type, b, name, val) \\")
        lines.append("    do { \\")
        lines.append("        int _ret = blobmsg_add_##type((b), (name), (val)); \\")
        lines.append("        if (_ret < 0) { \\")
        lines.append("            return UBUS_STATUS_INVALID_ARGUMENT; \\")
        lines.append("        } \\")
        lines.append("    } while (0)")
        lines.append("")
        
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
        lines.append("static const struct ubus_method {}_methods[] = {{".format(
            obj.name.lower()
        ))
        for i, method_def in enumerate(method_defs):
            if i == len(method_defs) - 1:
                # Last item, no comma
                lines.append(f"    {method_def}")
            else:
                lines.append(f"    {method_def},")
        lines.append("};")
        lines.append("")
        
        # Generate object_type
        lines.append(
            f"static struct ubus_object_type {obj.name.lower()}_object_type ="
        )
        lines.append(
            f'    UBUS_OBJECT_TYPE("{obj.name.lower()}", {obj.name.lower()}_methods);'
        )
        lines.append("")
        
        # Generate object
        lines.append(f"struct ubus_object {obj.name.lower()}_object = {{")
        lines.append(f'    .name = "{obj.name.lower()}",')
        lines.append(f"    .type = &{obj.name.lower()}_object_type,")
        lines.append(f"    .methods = {obj.name.lower()}_methods,")
        lines.append(f"    .n_methods = ARRAY_SIZE({obj.name.lower()}_methods),")
        lines.append("};")
        
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
        
        lines.append(f"enum {{")
        
        # Process parameters
        param_names = []
        if is_method_params and method:
            # Direct parameters
            for param in method.parameters:
                if param.name:
                    enum_item = f"{enum_prefix}{param.name.upper()}"
                    param_names.append((enum_item, param.name, param.type_name))
                    lines.append(f"    {enum_item},")
        else:
            # Using defined type
            type_def = self.type_defs.get(type_name)
            if type_def:
                for field in type_def.fields:
                    enum_item = f"{enum_prefix}{field.name.upper()}"
                    param_names.append((enum_item, field.name, field.type_name))
                    lines.append(f"    {enum_item},")
        
        lines.append(f"    {enum_name}")
        lines.append("};")
        lines.append("")
        
        # Generate policy array with prefix
        policy_name = f"{prefix}_policy"
        lines.append(f"static const struct blobmsg_policy {policy_name}[] = {{")
        
        for i, (enum_item, field_name, type_name) in enumerate(param_names):
            blob_type = self._get_blob_type(type_name)
            if i == len(param_names) - 1:
                # Last item, no comma
                lines.append(
                    f'    [{enum_item}] = {{ .name = "{field_name}", .type = {blob_type} }}'
                )
            else:
                lines.append(
                    f'    [{enum_item}] = {{ .name = "{field_name}", .type = {blob_type} }},'
                )
        
        lines.append("};")
        
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
        lines.append(f"int {deserialize_func}(struct blob_attr *msg, struct {struct_type_name} *params)")
        lines.append("{")
        lines.append(f"    struct blob_attr *{tb_name}[{enum_name}];")
        lines.append(f"    if (blobmsg_parse({policy_name}, ARRAY_SIZE({policy_name}), "
                    f"{tb_name}, blob_data(msg), blob_len(msg)) < 0) {{")
        lines.append("        return UBUS_STATUS_INVALID_ARGUMENT;")
        lines.append("    }")
        lines.append("")
        
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
                lines.append(f"    if ({check_conditions[0]}) {{")
            else:
                # Combine all checks with ||
                combined_check = " || ".join(check_conditions)
                lines.append(f"    if ({combined_check}) {{")
            lines.append("        return UBUS_STATUS_INVALID_ARGUMENT;")
            lines.append("    }")
            lines.append("")
        
        # Initialize has_fields to 0 if there are optional fields
        if optional_fields:
            lines.append("    params->has_fields = 0;")
            lines.append("")
        
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
        
        lines.append("    return UBUS_STATUS_OK;")
        lines.append("}")
        lines.append("")
        
        # Generate serialize function (not static, returns int)
        # Note: Serialize doesn't validate required fields as it's for output
        serialize_func = f"{func_prefix}_serialize"
        lines.append(f"int {serialize_func}(struct blob_buf *b, const struct {struct_type_name} *params)")
        lines.append("{")
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
            lines.append("    int ret;")
            lines.append("")
        
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
        
        lines.append("    return UBUS_STATUS_OK;")
        lines.append("}")
        lines.append("")
        
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
            # Extract struct variable name from target (e.g., "params->field" -> "params")
            struct_var = target.split("->")[0]
            if field_type == "string":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(string, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "int8":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(u8, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "int16":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(u16, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "int32":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(u32, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "int64":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(u64, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "bool":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(u8, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "double":
                lines.append(f"    UBUS_IDL_GET_OPTIONAL(double, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});")
            elif field_type == "array":
                # Array type - store as blob_attr pointer
                lines.append(f"    if ({tb_name}[{enum_item}]) {{")
                lines.append(f"        {target} = {tb_name}[{enum_item}];")
                lines.append(f"        UBUS_IDL_SET_FIELD({struct_var}, {macro_name});")
                lines.append("    }")
            elif field_type == "unspec":
                # Unspec type - store as blob_attr pointer
                lines.append(f"    if ({tb_name}[{enum_item}]) {{")
                lines.append(f"        {target} = {tb_name}[{enum_item}];")
                lines.append(f"        UBUS_IDL_SET_FIELD({struct_var}, {macro_name});")
                lines.append("    }")
            else:
                # Custom type - store as blob_attr pointer
                lines.append(f"    // TODO: Handle custom type {field_type}")
        else:
            # Required fields - direct assignment
            if field_type == "string":
                lines.append(f"    {target} = blobmsg_get_string({tb_name}[{enum_item}]);")
            elif field_type == "int8":
                lines.append(f"    {target} = blobmsg_get_u8({tb_name}[{enum_item}]);")
            elif field_type == "int16":
                lines.append(f"    {target} = blobmsg_get_u16({tb_name}[{enum_item}]);")
            elif field_type == "int32":
                lines.append(f"    {target} = blobmsg_get_u32({tb_name}[{enum_item}]);")
            elif field_type == "int64":
                lines.append(f"    {target} = blobmsg_get_u64({tb_name}[{enum_item}]);")
            elif field_type == "bool":
                lines.append(f"    {target} = blobmsg_get_u8({tb_name}[{enum_item}]);")
            elif field_type == "double":
                lines.append(f"    {target} = blobmsg_get_double({tb_name}[{enum_item}]);")
            elif field_type == "array":
                # Array type - store as blob_attr pointer
                lines.append(f"    {target} = {tb_name}[{enum_item}];")
            elif field_type == "unspec":
                # Unspec type - store as blob_attr pointer
                lines.append(f"    {target} = {tb_name}[{enum_item}];")
            else:
                # Custom type - store as blob_attr pointer
                lines.append(f"    // TODO: Handle custom type {field_type}")
    
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
            
            if type_name == "string":
                lines.append(f'    UBUS_IDL_ADD_OPTIONAL(string, b, "{field_name}", {field_access}, {struct_var}, {macro_name});')
            elif type_name == "int8":
                lines.append(f'    UBUS_IDL_ADD_OPTIONAL(u8, b, "{field_name}", {field_access}, {struct_var}, {macro_name});')
            elif type_name == "int16":
                lines.append(f'    UBUS_IDL_ADD_OPTIONAL(u16, b, "{field_name}", {field_access}, {struct_var}, {macro_name});')
            elif type_name == "int32":
                lines.append(f'    UBUS_IDL_ADD_OPTIONAL(u32, b, "{field_name}", {field_access}, {struct_var}, {macro_name});')
            elif type_name == "int64":
                lines.append(f'    UBUS_IDL_ADD_OPTIONAL(u64, b, "{field_name}", {field_access}, {struct_var}, {macro_name});')
            elif type_name == "bool":
                lines.append(f'    if (UBUS_IDL_HAS_FIELD({struct_var}, {macro_name})) {{')
                lines.append(f'        blobmsg_add_u8(b, "{field_name}", {field_access} ? 1 : 0);')
                lines.append("    }")
            elif type_name == "double":
                lines.append(f'    UBUS_IDL_ADD_OPTIONAL(double, b, "{field_name}", {field_access}, {struct_var}, {macro_name});')
            elif type_name == "array":
                # Array type - use blobmsg_add_field
                lines.append(f'    if (UBUS_IDL_HAS_FIELD({struct_var}, {macro_name})) {{')
                lines.append(f'        blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "{field_name}", blob_data({field_access}), blob_len({field_access}));')
                lines.append("    }")
            elif type_name == "unspec":
                # Unspec type - use blobmsg_add_field
                lines.append(f'    if (UBUS_IDL_HAS_FIELD({struct_var}, {macro_name})) {{')
                lines.append(f'        blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "{field_name}", blob_data({field_access}), blob_len({field_access}));')
                lines.append("    }")
            else:
                # Custom type
                lines.append(f'    // TODO: Handle custom type {type_name}')
        else:
            # Required fields - use macros for error checking
            if type_name == "string":
                lines.append(f'    UBUS_IDL_ADD(string, b, "{field_name}", {field_access});')
            elif type_name == "int8":
                lines.append(f'    UBUS_IDL_ADD(u8, b, "{field_name}", {field_access});')
            elif type_name == "int16":
                lines.append(f'    UBUS_IDL_ADD(u16, b, "{field_name}", {field_access});')
            elif type_name == "int32":
                lines.append(f'    UBUS_IDL_ADD(u32, b, "{field_name}", {field_access});')
            elif type_name == "int64":
                lines.append(f'    UBUS_IDL_ADD(u64, b, "{field_name}", {field_access});')
            elif type_name == "bool":
                lines.append(f'    UBUS_IDL_ADD(u8, b, "{field_name}", {field_access} ? 1 : 0);')
            elif type_name == "double":
                lines.append(f'    UBUS_IDL_ADD(double, b, "{field_name}", {field_access});')
            elif type_name == "array":
                # Array type - use blobmsg_add_field
                lines.append(f'    if ({field_access}) {{')
                lines.append(f'        ret = blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "{field_name}", blob_data({field_access}), blob_len({field_access}));')
                lines.append(f'    }} else {{')
                lines.append(f'        ret = -1;  // Required field missing')
                lines.append(f'    }}')
                lines.append("    if (ret < 0) {")
                lines.append("        return UBUS_STATUS_INVALID_ARGUMENT;")
                lines.append("    }")
            elif type_name == "unspec":
                # Unspec type - use blobmsg_add_field
                lines.append(f'    if ({field_access}) {{')
                lines.append(f'        ret = blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "{field_name}", blob_data({field_access}), blob_len({field_access}));')
                lines.append(f'    }} else {{')
                lines.append(f'        ret = -1;  // Required field missing')
                lines.append(f'    }}')
                lines.append("    if (ret < 0) {")
                lines.append("        return UBUS_STATUS_INVALID_ARGUMENT;")
                lines.append("    }")
            else:
                # Custom type
                lines.append(f'    // TODO: Handle custom type {type_name}')
                lines.append(f'    ret = 0;  // Placeholder')
                lines.append("    if (ret < 0) {")
                lines.append("        return UBUS_STATUS_INVALID_ARGUMENT;")
                lines.append("    }")
    
    def _get_c_type(self, type_name: str, var_name: str, optional: bool = False) -> str:
        """Get C type declaration for parameter"""
        if type_name == "string":
            # String is already a pointer, optional means it can be NULL
            return f"const char *{var_name}"
        elif type_name == "int8":
            if optional:
                return f"int8_t *{var_name}"
            return f"int8_t {var_name}"
        elif type_name == "int16":
            if optional:
                return f"int16_t *{var_name}"
            return f"int16_t {var_name}"
        elif type_name == "int32":
            # For optional int32, use pointer (can be NULL)
            if optional:
                return f"int32_t *{var_name}"
            return f"int32_t {var_name}"
        elif type_name == "int64":
            if optional:
                return f"int64_t *{var_name}"
            return f"int64_t {var_name}"
        elif type_name == "bool":
            if optional:
                return f"bool *{var_name}"
            return f"bool {var_name}"
        elif type_name == "double":
            if optional:
                return f"double *{var_name}"
            return f"double {var_name}"
        elif type_name == "array":
            # Array type - always use blob_attr pointer
            return f"struct blob_attr *{var_name}"
        elif type_name == "unspec":
            # Unspec type - always use blob_attr pointer
            return f"struct blob_attr *{var_name}"
        else:
            # Custom type
            return f"struct blob_attr *{var_name}_attr"
    
    def _generate_serialize_field(self, lines: List[str], field_name: str, type_name: str, optional: bool):
        """Generate code to serialize a field to blob_buf"""
        if optional:
            # For optional string, check if not NULL
            if type_name == "string":
                lines.append(f"    if ({field_name} && {field_name}[0] != '\\0') {{")
            else:
                lines.append(f"    if ({field_name}) {{")
        
        if type_name == "string":
            lines.append(f'        blobmsg_add_string(b, "{field_name}", {field_name});')
        elif type_name == "int8":
            if optional:
                lines.append(f'        blobmsg_add_u8(b, "{field_name}", *{field_name});')
            else:
                lines.append(f'        blobmsg_add_u8(b, "{field_name}", {field_name});')
        elif type_name == "int16":
            if optional:
                lines.append(f'        blobmsg_add_u16(b, "{field_name}", *{field_name});')
            else:
                lines.append(f'        blobmsg_add_u16(b, "{field_name}", {field_name});')
        elif type_name == "int32":
            if optional:
                lines.append(f'        blobmsg_add_u32(b, "{field_name}", *{field_name});')
            else:
                lines.append(f'        blobmsg_add_u32(b, "{field_name}", {field_name});')
        elif type_name == "int64":
            if optional:
                lines.append(f'        blobmsg_add_u64(b, "{field_name}", *{field_name});')
            else:
                lines.append(f'        blobmsg_add_u64(b, "{field_name}", {field_name});')
        elif type_name == "bool":
            if optional:
                lines.append(f'        blobmsg_add_u8(b, "{field_name}", *{field_name} ? 1 : 0);')
            else:
                lines.append(f'        blobmsg_add_u8(b, "{field_name}", {field_name} ? 1 : 0);')
        elif type_name == "double":
            if optional:
                lines.append(f'        blobmsg_add_double(b, "{field_name}", *{field_name});')
            else:
                lines.append(f'        blobmsg_add_double(b, "{field_name}", {field_name});')
        elif type_name == "array":
            # Array type - use blobmsg_add_field
            if optional:
                lines.append(f'        if ({field_name}) {{')
                lines.append(f'            blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "{field_name}", blob_data({field_name}), blob_len({field_name}));')
                lines.append(f'        }}')
            else:
                lines.append(f'        blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "{field_name}", blob_data({field_name}), blob_len({field_name}));')
        elif type_name == "unspec":
            # Unspec type - use blobmsg_add_field
            if optional:
                lines.append(f'        if ({field_name}) {{')
                lines.append(f'            blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "{field_name}", blob_data({field_name}), blob_len({field_name}));')
                lines.append(f'        }}')
            else:
                lines.append(f'        blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "{field_name}", blob_data({field_name}), blob_len({field_name}));')
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
            f"int {handler_name}(struct ubus_context *ctx, "
            f"struct ubus_object *obj, "
            f"struct ubus_request_data *req, "
            f"const char *method, "
            f"struct blob_attr *msg)"
        )
        lines.append("{")
        
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
            lines.append(f"    struct {struct_type_name} params;")
            lines.append("")
            # Use deserialize function (returns UBUS_STATUS_OK on success)
            lines.append(f"    if ({deserialize_func}(msg, &params) != UBUS_STATUS_OK) {{")
            lines.append("        return UBUS_STATUS_INVALID_ARGUMENT;")
            lines.append("    }")
            lines.append("")
            lines.append("    // TODO: Use params struct here")
            lines.append("    // Example: int32_t id = params.id;")
            lines.append("")
        
        # Check if custom handler is specified
        if method.custom_handler:
            # Include custom handler file
            handler_file = method.custom_handler
            if not handler_file.endswith('.c') and not handler_file.endswith('.h'):
                handler_file = f"{handler_file}.c"
            lines.append(f"    // Custom handler from {handler_file}")
            lines.append(f"    // Include your custom handler implementation here")
            lines.append(f"    // #include \"{handler_file}\"")
            lines.append("")
            lines.append(f"    // Call custom handler function")
            lines.append(f"    // return {method.custom_handler}_impl(ctx, obj, req, method, msg, ...);")
        else:
            lines.append("    // TODO: Implement method logic")
            lines.append("    // Use ubus_send_reply(ctx, req, b.head) to send reply")
            lines.append("    // Example:")
            lines.append("    // struct blob_buf b;")
            lines.append("    // blob_buf_init(&b, 0);")
            lines.append("    // {serialize_func}(&b, ...);".format(serialize_func=f"{method_name}_serialize"))
            lines.append("    // ubus_send_reply(ctx, req, b.head);")
        
        lines.append("")
        lines.append("    return UBUS_STATUS_OK;")
        lines.append("}")
        
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
        
        if type_name in TYPE_MAP:
            if type_name == "string":
                lines.append(
                    f"        const char *{var_name} = "
                    f"blobmsg_get_string({tb_name}[{enum_item}]);"
                )
            elif type_name == "int8":
                lines.append(
                    f"        int8_t {var_name} = "
                    f"blobmsg_get_u8({tb_name}[{enum_item}]);"
                )
            elif type_name == "int16":
                lines.append(
                    f"        int16_t {var_name} = "
                    f"blobmsg_get_u16({tb_name}[{enum_item}]);"
                )
            elif type_name == "int32":
                lines.append(
                    f"        int32_t {var_name} = "
                    f"blobmsg_get_u32({tb_name}[{enum_item}]);"
                )
            elif type_name == "int64":
                lines.append(
                    f"        int64_t {var_name} = "
                    f"blobmsg_get_u64({tb_name}[{enum_item}]);"
                )
            elif type_name == "bool":
                lines.append(
                    f"        bool {var_name} = "
                    f"blobmsg_get_u8({tb_name}[{enum_item}]) != 0;"
                )
            elif type_name == "double":
                lines.append(
                    f"        double {var_name} = "
                    f"blobmsg_get_double({tb_name}[{enum_item}]);"
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
        if type_name in TYPE_MAP:
            return TYPE_MAP[type_name]
        else:
            # Custom type uses TABLE
            return "BLOBMSG_TYPE_TABLE"

