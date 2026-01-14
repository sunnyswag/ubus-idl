/* Generated from ubus IDL - type_test */

#include <libubox/blobmsg_json.h>
#include <libubus.h>
#include "type_test_object.h"

/* Helper macros for field serialization with error checking */
#define UBUS_IDL_ADD(type, b, name, val) \
    do { \
        int _ret = blobmsg_add_##type((b), (name), (val)); \
        if (_ret < 0) { \
            return UBUS_STATUS_INVALID_ARGUMENT; \
        } \
    } while (0)

static const struct blobmsg_policy type_test_all_types_policy[] = {
    [TYPE_TEST_ALL_TYPES_INT8_VAL] = { .name = "int8_val", .type = BLOBMSG_TYPE_INT8 },
    [TYPE_TEST_ALL_TYPES_INT16_VAL] = { .name = "int16_val", .type = BLOBMSG_TYPE_INT16 },
    [TYPE_TEST_ALL_TYPES_INT32_VAL] = { .name = "int32_val", .type = BLOBMSG_TYPE_INT32 },
    [TYPE_TEST_ALL_TYPES_INT64_VAL] = { .name = "int64_val", .type = BLOBMSG_TYPE_INT64 },
    [TYPE_TEST_ALL_TYPES_BOOL_VAL] = { .name = "bool_val", .type = BLOBMSG_TYPE_BOOL },
    [TYPE_TEST_ALL_TYPES_DOUBLE_VAL] = { .name = "double_val", .type = BLOBMSG_TYPE_DOUBLE },
    [TYPE_TEST_ALL_TYPES_STRING_VAL] = { .name = "string_val", .type = BLOBMSG_TYPE_STRING }
};

int type_test_all_types_deserialize(struct blob_attr *msg, struct type_test_all_types_params *params)
{
    struct blob_attr *tb_type_test_all_types[__TYPE_TEST_ALL_TYPES_MAX];
    if (blobmsg_parse(type_test_all_types_policy, ARRAY_SIZE(type_test_all_types_policy), tb_type_test_all_types, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT8_VAL] || !tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT16_VAL] || !tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT32_VAL] || !tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT64_VAL] || !tb_type_test_all_types[TYPE_TEST_ALL_TYPES_BOOL_VAL] || !tb_type_test_all_types[TYPE_TEST_ALL_TYPES_DOUBLE_VAL] || !tb_type_test_all_types[TYPE_TEST_ALL_TYPES_STRING_VAL]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->int8_val = blobmsg_get_u8(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT8_VAL]);
    params->int16_val = blobmsg_get_u16(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT16_VAL]);
    params->int32_val = blobmsg_get_u32(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT32_VAL]);
    params->int64_val = blobmsg_get_u64(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_INT64_VAL]);
    params->bool_val = blobmsg_get_u8(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_BOOL_VAL]) != 0;
    params->double_val = blobmsg_get_double(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_DOUBLE_VAL]);
    params->string_val = blobmsg_get_string(tb_type_test_all_types[TYPE_TEST_ALL_TYPES_STRING_VAL]);
    return UBUS_STATUS_OK;
}

int type_test_all_types_serialize(struct blob_buf *b, const struct type_test_all_types_params *params)
{
    UBUS_IDL_ADD(u8, b, "int8_val", params->int8_val);
    UBUS_IDL_ADD(u16, b, "int16_val", params->int16_val);
    UBUS_IDL_ADD(u32, b, "int32_val", params->int32_val);
    UBUS_IDL_ADD(u64, b, "int64_val", params->int64_val);
    UBUS_IDL_ADD(u8, b, "bool_val", params->bool_val ? 1 : 0);
    UBUS_IDL_ADD(double, b, "double_val", params->double_val);
    UBUS_IDL_ADD(string, b, "string_val", params->string_val);
    return UBUS_STATUS_OK;
}

static const struct blobmsg_policy type_with_all_types_policy[] = {
    [TYPE_WITH_ALL_TYPES_INT8_FIELD] = { .name = "int8_field", .type = BLOBMSG_TYPE_INT8 },
    [TYPE_WITH_ALL_TYPES_INT16_FIELD] = { .name = "int16_field", .type = BLOBMSG_TYPE_INT16 },
    [TYPE_WITH_ALL_TYPES_INT32_FIELD] = { .name = "int32_field", .type = BLOBMSG_TYPE_INT32 },
    [TYPE_WITH_ALL_TYPES_INT64_FIELD] = { .name = "int64_field", .type = BLOBMSG_TYPE_INT64 },
    [TYPE_WITH_ALL_TYPES_BOOL_FIELD] = { .name = "bool_field", .type = BLOBMSG_TYPE_BOOL },
    [TYPE_WITH_ALL_TYPES_DOUBLE_FIELD] = { .name = "double_field", .type = BLOBMSG_TYPE_DOUBLE },
    [TYPE_WITH_ALL_TYPES_STRING_FIELD] = { .name = "string_field", .type = BLOBMSG_TYPE_STRING },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_INT8] = { .name = "optional_int8", .type = BLOBMSG_TYPE_INT8 },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_INT16] = { .name = "optional_int16", .type = BLOBMSG_TYPE_INT16 },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_INT32] = { .name = "optional_int32", .type = BLOBMSG_TYPE_INT32 },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_INT64] = { .name = "optional_int64", .type = BLOBMSG_TYPE_INT64 },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_BOOL] = { .name = "optional_bool", .type = BLOBMSG_TYPE_BOOL },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_DOUBLE] = { .name = "optional_double", .type = BLOBMSG_TYPE_DOUBLE },
    [TYPE_WITH_ALL_TYPES_OPTIONAL_STRING] = { .name = "optional_string", .type = BLOBMSG_TYPE_STRING }
};

int type_with_all_types_deserialize(struct blob_attr *msg, struct type_with_all_types *params)
{
    struct blob_attr *tb_type_with_all_types[__TYPE_WITH_ALL_TYPES_MAX];
    if (blobmsg_parse(type_with_all_types_policy, ARRAY_SIZE(type_with_all_types_policy), tb_type_with_all_types, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT8_FIELD] || !tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT16_FIELD] || !tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT32_FIELD] || !tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT64_FIELD] || !tb_type_with_all_types[TYPE_WITH_ALL_TYPES_BOOL_FIELD] || !tb_type_with_all_types[TYPE_WITH_ALL_TYPES_DOUBLE_FIELD] || !tb_type_with_all_types[TYPE_WITH_ALL_TYPES_STRING_FIELD]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->has_fields = 0;
    params->int8_field = blobmsg_get_u8(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT8_FIELD]);
    params->int16_field = blobmsg_get_u16(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT16_FIELD]);
    params->int32_field = blobmsg_get_u32(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT32_FIELD]);
    params->int64_field = blobmsg_get_u64(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_INT64_FIELD]);
    params->bool_field = blobmsg_get_u8(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_BOOL_FIELD]) != 0;
    params->double_field = blobmsg_get_double(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_DOUBLE_FIELD]);
    params->string_field = blobmsg_get_string(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_STRING_FIELD]);

    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT8]) {
        params->optional_int8 = blobmsg_get_u8(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT8]);
        params->has_optional_int8 = 1;
    }
    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT16]) {
        params->optional_int16 = blobmsg_get_u16(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT16]);
        params->has_optional_int16 = 1;
    }
    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT32]) {
        params->optional_int32 = blobmsg_get_u32(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT32]);
        params->has_optional_int32 = 1;
    }
    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT64]) {
        params->optional_int64 = blobmsg_get_u64(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_INT64]);
        params->has_optional_int64 = 1;
    }
    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_BOOL]) {
        params->optional_bool = blobmsg_get_u8(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_BOOL]) != 0;
        params->has_optional_bool = 1;
    }
    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_DOUBLE]) {
        params->optional_double = blobmsg_get_double(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_DOUBLE]);
        params->has_optional_double = 1;
    }
    if (tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_STRING]) {
        params->optional_string = blobmsg_get_string(tb_type_with_all_types[TYPE_WITH_ALL_TYPES_OPTIONAL_STRING]);
        params->has_optional_string = 1;
    }
    return UBUS_STATUS_OK;
}

int type_with_all_types_serialize(struct blob_buf *b, const struct type_with_all_types *params)
{
    UBUS_IDL_ADD(u8, b, "int8_field", params->int8_field);
    UBUS_IDL_ADD(u16, b, "int16_field", params->int16_field);
    UBUS_IDL_ADD(u32, b, "int32_field", params->int32_field);
    UBUS_IDL_ADD(u64, b, "int64_field", params->int64_field);
    UBUS_IDL_ADD(u8, b, "bool_field", params->bool_field ? 1 : 0);
    UBUS_IDL_ADD(double, b, "double_field", params->double_field);
    UBUS_IDL_ADD(string, b, "string_field", params->string_field);
    if (params->has_optional_int8) {
        blobmsg_add_u8(b, "optional_int8", params->optional_int8);
    }
    if (params->has_optional_int16) {
        blobmsg_add_u16(b, "optional_int16", params->optional_int16);
    }
    if (params->has_optional_int32) {
        blobmsg_add_u32(b, "optional_int32", params->optional_int32);
    }
    if (params->has_optional_int64) {
        blobmsg_add_u64(b, "optional_int64", params->optional_int64);
    }
    if (params->has_optional_bool) {
        blobmsg_add_u8(b, "optional_bool", params->optional_bool ? 1 : 0);
    }
    if (params->has_optional_double) {
        blobmsg_add_double(b, "optional_double", params->optional_double);
    }
    if (params->has_optional_string) {
        blobmsg_add_string(b, "optional_string", params->optional_string);
    }
    return UBUS_STATUS_OK;
}

static const struct ubus_method type_test_methods[] = {
    UBUS_METHOD("all_types", type_test_all_types_handler, type_test_all_types_policy),
    UBUS_METHOD("type_with_all_types", type_test_type_with_all_types_handler, type_with_all_types_policy)
};

static struct ubus_object_type type_test_object_type =
    UBUS_OBJECT_TYPE("type_test", type_test_methods);

struct ubus_object type_test_object = {
    .name = "type_test",
    .type = &type_test_object_type,
    .methods = type_test_methods,
    .n_methods = ARRAY_SIZE(type_test_methods),
};
