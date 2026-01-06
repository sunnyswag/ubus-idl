"""Code generation templates for ubus IDL"""

# Header file templates
HEADER_FILE_HEADER = "/* Generated from ubus IDL - {obj_name} */"
HEADER_GUARD_START = "#ifndef {header_guard}"
HEADER_GUARD_DEFINE = "#define {header_guard}"
HEADER_INCLUDES = [
    "#include <libubus.h>",
    "#include <stdint.h>",
    "",
]

# Source file templates
SOURCE_FILE_HEADER = "/* Generated from ubus IDL - {obj_name} */"
SOURCE_INCLUDES = [
    "#include <libubox/blobmsg_json.h>",
    "#include <libubus.h>",
    '#include "{header_file}"',
    "",
]

# Helper macros templates
HELPER_MACROS_HEADER = "/* Helper macros for optional field operations */"
HELPER_MACROS = [
    "#define UBUS_IDL_HAS_FIELD(params, mask) ((params)->has_fields & (mask))",
    "#define UBUS_IDL_SET_FIELD(params, mask) ((params)->has_fields |= (mask))",
    "#define UBUS_IDL_CLEAR_FIELD(params, mask) ((params)->has_fields &= ~(mask))",
    "",
]

HELPER_MACROS_DESERIALIZE_HEADER = "/* Helper macros for optional field deserialization */"
HELPER_MACROS_DESERIALIZE = [
    "#define UBUS_IDL_GET_OPTIONAL(type, tb, enum, field, params, mask) \\",
    "    do { \\",
    "        if ((tb)[(enum)]) { \\",
    "            (field) = blobmsg_get_##type((tb)[(enum)]); \\",
    "            UBUS_IDL_SET_FIELD((params), (mask)); \\",
    "        } \\",
    "    } while (0)",
    "",
]

HELPER_MACROS_SERIALIZE_HEADER = "/* Helper macros for optional field serialization */"
HELPER_MACROS_SERIALIZE = [
    "#define UBUS_IDL_ADD_OPTIONAL(type, b, name, field, params, mask) \\",
    "    do { \\",
    "        if (UBUS_IDL_HAS_FIELD((params), (mask))) { \\",
    "            blobmsg_add_##type((b), (name), (field)); \\",
    "        } \\",
    "    } while (0)",
    "",
]

SERIALIZE_MACRO_HEADER = "/* Helper macros for field serialization with error checking */"
SERIALIZE_MACRO = [
    "#define UBUS_IDL_ADD(type, b, name, val) \\",
    "    do { \\",
    "        int _ret = blobmsg_add_##type((b), (name), (val)); \\",
    "        if (_ret < 0) { \\",
    "            return UBUS_STATUS_INVALID_ARGUMENT; \\",
    "        } \\",
    "    } while (0)",
    "",
]

# Struct templates
STRUCT_START = "struct {struct_name} {{"
STRUCT_FIELD = "    {c_type} {field_name};"
STRUCT_HAS_FIELDS = "    unsigned int has_fields;"
STRUCT_END = "};"

# Enum templates
ENUM_START = "enum {"
ENUM_ITEM = "    {enum_item},"
ENUM_MAX = "    {enum_max}"
ENUM_END = "};"

# Policy templates
POLICY_START = "static const struct blobmsg_policy {policy_name}[] = {{"
POLICY_ITEM = '    [{enum_item}] = {{ .name = "{field_name}", .type = {blob_type} }}'
POLICY_ITEM_WITH_COMMA = '    [{enum_item}] = {{ .name = "{field_name}", .type = {blob_type} }},'
POLICY_END = "};"

# Function templates
DESERIALIZE_FUNC_SIGNATURE = "int {func_name}(struct blob_attr *msg, struct {struct_type} *params)"
DESERIALIZE_FUNC_BODY_START = "{"
DESERIALIZE_TB_DECL = "    struct blob_attr *{tb_name}[{enum_max}];"
DESERIALIZE_PARSE_CHECK = (
    "    if (blobmsg_parse({policy_name}, ARRAY_SIZE({policy_name}), "
    "{tb_name}, blob_data(msg), blob_len(msg)) < 0) {{"
)
DESERIALIZE_PARSE_ERROR = "        return UBUS_STATUS_INVALID_ARGUMENT;"
DESERIALIZE_PARSE_END = "    }"
DESERIALIZE_INIT_HAS_FIELDS = "    params->has_fields = 0;"
DESERIALIZE_RETURN_OK = "    return UBUS_STATUS_OK;"
DESERIALIZE_FUNC_END = "}"

SERIALIZE_FUNC_SIGNATURE = "int {func_name}(struct blob_buf *b, const struct {struct_type} *params)"
SERIALIZE_FUNC_BODY_START = "{"
SERIALIZE_RET_DECL = "    int ret;"
SERIALIZE_RETURN_OK = "    return UBUS_STATUS_OK;"
SERIALIZE_FUNC_END = "}"

HANDLER_FUNC_SIGNATURE = (
    "int {handler_name}(struct ubus_context *ctx, "
    "struct ubus_object *obj, "
    "struct ubus_request_data *req, "
    "const char *method, "
    "struct blob_attr *msg)"
)
HANDLER_FUNC_BODY_START = "{"
HANDLER_PARAMS_DECL = "    struct {struct_type} params;"
HANDLER_DESERIALIZE_CHECK = "    if ({deserialize_func}(msg, &params) != UBUS_STATUS_OK) {{"
HANDLER_DESERIALIZE_ERROR = "        return UBUS_STATUS_INVALID_ARGUMENT;"
HANDLER_DESERIALIZE_END = "    }"
HANDLER_TODO_PARAMS = "    // TODO: Use params struct here"
HANDLER_EXAMPLE_PARAMS = "    // Example: int32_t id = params.id;"
HANDLER_CUSTOM_COMMENT = "    // Custom handler from {handler_file}"
HANDLER_CUSTOM_INCLUDE = "    // Include your custom handler implementation here"
HANDLER_CUSTOM_INCLUDE_FILE = '    // #include "{handler_file}"'
HANDLER_CUSTOM_CALL = "    // Call custom handler function"
HANDLER_CUSTOM_CALL_FUNC = "    // return {handler_name}_impl(ctx, obj, req, method, msg, ...);"
HANDLER_TODO_IMPLEMENT = "    // TODO: Implement method logic"
HANDLER_TODO_REPLY = "    // Use ubus_send_reply(ctx, req, b.head) to send reply"
HANDLER_TODO_EXAMPLE = "    // Example:"
HANDLER_TODO_BLOB_BUF = "    // struct blob_buf b;"
HANDLER_TODO_INIT = "    // blob_buf_init(&b, 0);"
HANDLER_TODO_SERIALIZE = "    // {serialize_func}(&b, ...);"
HANDLER_TODO_SEND = "    // ubus_send_reply(ctx, req, b.head);"
HANDLER_RETURN_OK = "    return UBUS_STATUS_OK;"
HANDLER_FUNC_END = "}"

# Method array templates
METHOD_ARRAY_START = "static const struct ubus_method {obj_name}_methods[] = {{"
METHOD_ARRAY_ITEM = "    {method_def}"
METHOD_ARRAY_ITEM_WITH_COMMA = "    {method_def},"
METHOD_ARRAY_END = "};"

# Object type templates
OBJECT_TYPE_DECL = "static struct ubus_object_type {obj_name}_object_type ="
OBJECT_TYPE_DEF = '    UBUS_OBJECT_TYPE("{obj_name}", {obj_name}_methods);'

# Object templates
OBJECT_START = "struct ubus_object {obj_name}_object = {{"
OBJECT_NAME = '    .name = "{obj_name}",'
OBJECT_TYPE = "    .type = &{obj_name}_object_type,"
OBJECT_METHODS = "    .methods = {obj_name}_methods,"
OBJECT_N_METHODS = "    .n_methods = ARRAY_SIZE({obj_name}_methods),"
OBJECT_END = "};"

# Required field check templates
REQUIRED_FIELD_CHECK_SINGLE = "    if ({condition}) {{"
REQUIRED_FIELD_CHECK_MULTIPLE = "    if ({conditions}) {{"
REQUIRED_FIELD_CHECK_ERROR = "        return UBUS_STATUS_INVALID_ARGUMENT;"
REQUIRED_FIELD_CHECK_END = "    }"

# Bitmask macro templates
BITMASK_MACRO = "#define {macro_name} (1U << {enum_item})"

# Field assignment templates
FIELD_ASSIGN_CUSTOM_TODO = "    // TODO: Handle custom type {field_type}"


# ============================================================================
# Template Functions - Generate complete code blocks
# ============================================================================

def get_field_assign_code(field_type: str, target: str, tb_name: str, enum_item: str) -> str:
    """Generate field assignment code for deserialization"""
    type_map = {
        "string": "blobmsg_get_string",
        "int8": "blobmsg_get_u8",
        "int16": "blobmsg_get_u16",
        "int32": "blobmsg_get_u32",
        "int64": "blobmsg_get_u64",
        "bool": "blobmsg_get_u8",
        "double": "blobmsg_get_double",
        "array": None,  # Direct assignment
        "unspec": None,  # Direct assignment
    }
    
    if field_type in ["array", "unspec"]:
        return f"    {target} = {tb_name}[{enum_item}];"
    elif field_type in type_map:
        func = type_map[field_type]
        return f"    {target} = {func}({tb_name}[{enum_item}]);"
    else:
        return FIELD_ASSIGN_CUSTOM_TODO.format(field_type=field_type)


def get_optional_field_assign_code(field_type: str, target: str, tb_name: str, 
                                   enum_item: str, struct_var: str, macro_name: str) -> str:
    """Generate optional field assignment code for deserialization"""
    if field_type in ["array", "unspec"]:
        return (
            f"    if ({tb_name}[{enum_item}]) {{\n"
            f"        {target} = {tb_name}[{enum_item}];\n"
            f"        UBUS_IDL_SET_FIELD({struct_var}, {macro_name});\n"
            f"    }}"
        )
    
    type_map = {
        "string": "string",
        "int8": "u8",
        "int16": "u16",
        "int32": "u32",
        "int64": "u64",
        "bool": "u8",
        "double": "double",
    }
    
    if field_type in type_map:
        blob_type = type_map[field_type]
        return f"    UBUS_IDL_GET_OPTIONAL({blob_type}, {tb_name}, {enum_item}, {target}, {struct_var}, {macro_name});"
    else:
        return FIELD_ASSIGN_CUSTOM_TODO.format(field_type=field_type)


def get_serialize_add_code(type_name: str, field_name: str, field_access: str) -> str:
    """Generate serialize add code for required fields"""
    if type_name == "string":
        return f'    UBUS_IDL_ADD(string, b, "{field_name}", {field_access});'
    elif type_name == "int8":
        return f'    UBUS_IDL_ADD(u8, b, "{field_name}", {field_access});'
    elif type_name == "int16":
        return f'    UBUS_IDL_ADD(u16, b, "{field_name}", {field_access});'
    elif type_name == "int32":
        return f'    UBUS_IDL_ADD(u32, b, "{field_name}", {field_access});'
    elif type_name == "int64":
        return f'    UBUS_IDL_ADD(u64, b, "{field_name}", {field_access});'
    elif type_name == "bool":
        return f'    UBUS_IDL_ADD(u8, b, "{field_name}", {field_access} ? 1 : 0);'
    elif type_name == "double":
        return f'    UBUS_IDL_ADD(double, b, "{field_name}", {field_access});'
    elif type_name == "array":
        return (
            f'    if ({field_access}) {{\n'
            f'        ret = blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "{field_name}", blob_data({field_access}), blob_len({field_access}));\n'
            f'    }} else {{\n'
            f'        ret = -1;  // Required field missing\n'
            f'    }}\n'
            f'    if (ret < 0) {{\n'
            f'        return UBUS_STATUS_INVALID_ARGUMENT;\n'
            f'    }}'
        )
    elif type_name == "unspec":
        return (
            f'    if ({field_access}) {{\n'
            f'        ret = blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "{field_name}", blob_data({field_access}), blob_len({field_access}));\n'
            f'    }} else {{\n'
            f'        ret = -1;  // Required field missing\n'
            f'    }}\n'
            f'    if (ret < 0) {{\n'
            f'        return UBUS_STATUS_INVALID_ARGUMENT;\n'
            f'    }}'
        )
    else:
        return (
            f'    // TODO: Handle custom type {type_name}\n'
            f'    ret = 0;  // Placeholder\n'
            f'    if (ret < 0) {{\n'
            f'        return UBUS_STATUS_INVALID_ARGUMENT;\n'
            f'    }}'
        )


def get_serialize_add_optional_code(type_name: str, field_name: str, field_access: str,
                                    struct_var: str, macro_name: str) -> str:
    """Generate serialize add code for optional fields"""
    if type_name == "string":
        return f'    UBUS_IDL_ADD_OPTIONAL(string, b, "{field_name}", {field_access}, {struct_var}, {macro_name});'
    elif type_name == "int8":
        return f'    UBUS_IDL_ADD_OPTIONAL(u8, b, "{field_name}", {field_access}, {struct_var}, {macro_name});'
    elif type_name == "int16":
        return f'    UBUS_IDL_ADD_OPTIONAL(u16, b, "{field_name}", {field_access}, {struct_var}, {macro_name});'
    elif type_name == "int32":
        return f'    UBUS_IDL_ADD_OPTIONAL(u32, b, "{field_name}", {field_access}, {struct_var}, {macro_name});'
    elif type_name == "int64":
        return f'    UBUS_IDL_ADD_OPTIONAL(u64, b, "{field_name}", {field_access}, {struct_var}, {macro_name});'
    elif type_name == "bool":
        return (
            f'    if (UBUS_IDL_HAS_FIELD({struct_var}, {macro_name})) {{\n'
            f'        blobmsg_add_u8(b, "{field_name}", {field_access} ? 1 : 0);\n'
            f'    }}'
        )
    elif type_name == "double":
        return f'    UBUS_IDL_ADD_OPTIONAL(double, b, "{field_name}", {field_access}, {struct_var}, {macro_name});'
    elif type_name == "array":
        return (
            f'    if (UBUS_IDL_HAS_FIELD({struct_var}, {macro_name})) {{\n'
            f'        blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "{field_name}", blob_data({field_access}), blob_len({field_access}));\n'
            f'    }}'
        )
    elif type_name == "unspec":
        return (
            f'    if (UBUS_IDL_HAS_FIELD({struct_var}, {macro_name})) {{\n'
            f'        blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "{field_name}", blob_data({field_access}), blob_len({field_access}));\n'
            f'    }}'
        )
    else:
        return f'    // TODO: Handle custom type {type_name}'
