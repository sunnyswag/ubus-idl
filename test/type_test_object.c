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

static const struct ubus_method type_test_methods[] = {
    UBUS_METHOD("all_types", type_test_all_types_handler, type_test_all_types_policy),
    UBUS_METHOD_NOARG("type_with_all_types", type_test_type_with_all_types_handler)
};

static struct ubus_object_type type_test_object_type =
    UBUS_OBJECT_TYPE("type_test", type_test_methods);

struct ubus_object type_test_object = {
    .name = "type_test",
    .type = &type_test_object_type,
    .methods = type_test_methods,
    .n_methods = ARRAY_SIZE(type_test_methods),
};
