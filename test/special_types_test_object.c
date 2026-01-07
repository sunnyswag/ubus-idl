/* Generated from ubus IDL - special_types_test */

#include <libubox/blobmsg_json.h>
#include <libubus.h>
#include "special_types_test_object.h"

/* Helper macros for optional field deserialization */
#define UBUS_IDL_GET_OPTIONAL(type, tb, enum, field, params, mask) \
    do { \
        if ((tb)[(enum)]) { \
            (field) = blobmsg_get_##type((tb)[(enum)]); \
            UBUS_IDL_SET_FIELD((params), (mask)); \
        } \
    } while (0)

/* Helper macros for optional field serialization */
#define UBUS_IDL_ADD_OPTIONAL(type, b, name, field, params, mask) \
    do { \
        if (UBUS_IDL_HAS_FIELD((params), (mask))) { \
            blobmsg_add_##type((b), (name), (field)); \
        } \
    } while (0)

/* Helper macros for field serialization with error checking */
#define UBUS_IDL_ADD(type, b, name, val) \
    do { \
        int _ret = blobmsg_add_##type((b), (name), (val)); \
        if (_ret < 0) { \
            return UBUS_STATUS_INVALID_ARGUMENT; \
        } \
    } while (0)

static const struct blobmsg_policy special_types_test_array_policy[] = {
    [SPECIAL_TYPES_TEST_ARRAY_ARRAY_VAL] = { .name = "array_val", .type = BLOBMSG_TYPE_ARRAY }
};

int special_types_test_array_deserialize(struct blob_attr *msg, struct special_types_test_array_params *params)
{
    struct blob_attr *tb_special_types_test_array[__SPECIAL_TYPES_TEST_ARRAY_MAX];
    if (blobmsg_parse(special_types_test_array_policy, ARRAY_SIZE(special_types_test_array_policy), tb_special_types_test_array, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_special_types_test_array[SPECIAL_TYPES_TEST_ARRAY_ARRAY_VAL]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->array_val = tb_special_types_test_array[SPECIAL_TYPES_TEST_ARRAY_ARRAY_VAL];
    return UBUS_STATUS_OK;
}

int special_types_test_array_serialize(struct blob_buf *b, const struct special_types_test_array_params *params)
{
    int ret;
    if (params->array_val) {
        ret = blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "array_val", blob_data(params->array_val), blob_len(params->array_val));
    } else {
        ret = -1;  // Required field missing
    }
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

static const struct blobmsg_policy special_types_test_unspec_policy[] = {
    [SPECIAL_TYPES_TEST_UNSPEC_UNSPEC_VAL] = { .name = "unspec_val", .type = BLOBMSG_TYPE_UNSPEC }
};

int special_types_test_unspec_deserialize(struct blob_attr *msg, struct special_types_test_unspec_params *params)
{
    struct blob_attr *tb_special_types_test_unspec[__SPECIAL_TYPES_TEST_UNSPEC_MAX];
    if (blobmsg_parse(special_types_test_unspec_policy, ARRAY_SIZE(special_types_test_unspec_policy), tb_special_types_test_unspec, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_special_types_test_unspec[SPECIAL_TYPES_TEST_UNSPEC_UNSPEC_VAL]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->unspec_val = tb_special_types_test_unspec[SPECIAL_TYPES_TEST_UNSPEC_UNSPEC_VAL];
    return UBUS_STATUS_OK;
}

int special_types_test_unspec_serialize(struct blob_buf *b, const struct special_types_test_unspec_params *params)
{
    int ret;
    if (params->unspec_val) {
        ret = blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "unspec_val", blob_data(params->unspec_val), blob_len(params->unspec_val));
    } else {
        ret = -1;  // Required field missing
    }
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

static const struct blobmsg_policy special_types_test_table_policy[] = {
    [SPECIAL_TYPES_TEST_TABLE_TABLE_VAL] = { .name = "table_val", .type = BLOBMSG_TYPE_TABLE }
};

int special_types_test_table_deserialize(struct blob_attr *msg, struct special_types_test_table_params *params)
{
    struct blob_attr *tb_special_types_test_table[__SPECIAL_TYPES_TEST_TABLE_MAX];
    if (blobmsg_parse(special_types_test_table_policy, ARRAY_SIZE(special_types_test_table_policy), tb_special_types_test_table, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_special_types_test_table[SPECIAL_TYPES_TEST_TABLE_TABLE_VAL]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    // TODO: Handle custom type custom_table_type
    return UBUS_STATUS_OK;
}

int special_types_test_table_serialize(struct blob_buf *b, const struct special_types_test_table_params *params)
{
    // TODO: Handle custom type custom_table_type
    ret = 0;  // Placeholder
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

static const struct blobmsg_policy special_types_test_all_special_policy[] = {
    [SPECIAL_TYPES_TEST_ALL_SPECIAL_ARRAY_VAL] = { .name = "array_val", .type = BLOBMSG_TYPE_ARRAY },
    [SPECIAL_TYPES_TEST_ALL_SPECIAL_UNSPEC_VAL] = { .name = "unspec_val", .type = BLOBMSG_TYPE_UNSPEC },
    [SPECIAL_TYPES_TEST_ALL_SPECIAL_TABLE_VAL] = { .name = "table_val", .type = BLOBMSG_TYPE_TABLE }
};

int special_types_test_all_special_deserialize(struct blob_attr *msg, struct special_types_test_all_special_params *params)
{
    struct blob_attr *tb_special_types_test_all_special[__SPECIAL_TYPES_TEST_ALL_SPECIAL_MAX];
    if (blobmsg_parse(special_types_test_all_special_policy, ARRAY_SIZE(special_types_test_all_special_policy), tb_special_types_test_all_special, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_special_types_test_all_special[SPECIAL_TYPES_TEST_ALL_SPECIAL_ARRAY_VAL] || !tb_special_types_test_all_special[SPECIAL_TYPES_TEST_ALL_SPECIAL_UNSPEC_VAL] || !tb_special_types_test_all_special[SPECIAL_TYPES_TEST_ALL_SPECIAL_TABLE_VAL]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->array_val = tb_special_types_test_all_special[SPECIAL_TYPES_TEST_ALL_SPECIAL_ARRAY_VAL];
    params->unspec_val = tb_special_types_test_all_special[SPECIAL_TYPES_TEST_ALL_SPECIAL_UNSPEC_VAL];
    // TODO: Handle custom type custom_table_type
    return UBUS_STATUS_OK;
}

int special_types_test_all_special_serialize(struct blob_buf *b, const struct special_types_test_all_special_params *params)
{
    int ret;
    if (params->array_val) {
        ret = blobmsg_add_field(b, BLOBMSG_TYPE_ARRAY, "array_val", blob_data(params->array_val), blob_len(params->array_val));
    } else {
        ret = -1;  // Required field missing
    }
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    if (params->unspec_val) {
        ret = blobmsg_add_field(b, BLOBMSG_TYPE_UNSPEC, "unspec_val", blob_data(params->unspec_val), blob_len(params->unspec_val));
    } else {
        ret = -1;  // Required field missing
    }
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    // TODO: Handle custom type custom_table_type
    ret = 0;  // Placeholder
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

static const struct ubus_method special_types_test_methods[] = {
    UBUS_METHOD("array", special_types_test_array_handler, special_types_test_array_policy),
    UBUS_METHOD("unspec", special_types_test_unspec_handler, special_types_test_unspec_policy),
    UBUS_METHOD("table", special_types_test_table_handler, special_types_test_table_policy),
    UBUS_METHOD("all_special", special_types_test_all_special_handler, special_types_test_all_special_policy)
};

static struct ubus_object_type special_types_test_object_type =
    UBUS_OBJECT_TYPE("special_types_test", special_types_test_methods);

struct ubus_object special_types_test_object = {
    .name = "special_types_test",
    .type = &special_types_test_object_type,
    .methods = special_types_test_methods,
    .n_methods = ARRAY_SIZE(special_types_test_methods),
};
