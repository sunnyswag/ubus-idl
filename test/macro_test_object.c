/* Generated from ubus IDL - macro_test */

#include <libubox/blobmsg_json.h>
#include <libubus.h>
#include "macro_test_object.h"

enum {
    MACRO_TEST_HELLO_ID,
    MACRO_TEST_HELLO_MSG,
    __MACRO_TEST_HELLO_MAX
};

static const struct blobmsg_policy macro_test_hello_policy[] = {
    [MACRO_TEST_HELLO_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 },
    [MACRO_TEST_HELLO_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
};

int macro_test_hello_deserialize(struct blob_attr *msg, struct macro_test_hello_params_t *params)
{
    struct blob_attr *tb_macro_test_hello[__MACRO_TEST_HELLO_MAX];
    if (blobmsg_parse(macro_test_hello_policy, ARRAY_SIZE(macro_test_hello_policy), tb_macro_test_hello, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_macro_test_hello[MACRO_TEST_HELLO_ID]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    params->id = blobmsg_get_u32(tb_macro_test_hello[MACRO_TEST_HELLO_ID]);
    if (!tb_macro_test_hello[MACRO_TEST_HELLO_MSG]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    params->msg = blobmsg_get_string(tb_macro_test_hello[MACRO_TEST_HELLO_MSG]);
    return UBUS_STATUS_OK;
}

int macro_test_hello_serialize(struct blob_buf *b, const struct macro_test_hello_params_t *params)
{
    int ret;

    ret = blobmsg_add_u32(b, "id", params->id);
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    ret = blobmsg_add_string(b, "msg", params->msg);
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

enum {
    MACRO_TEST_HELLO5_ID,
    __MACRO_TEST_HELLO5_MAX
};

static const struct blobmsg_policy macro_test_hello5_policy[] = {
    [MACRO_TEST_HELLO5_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 }
};

int macro_test_hello5_deserialize(struct blob_attr *msg, struct macro_test_hello5_params_t *params)
{
    struct blob_attr *tb_macro_test_hello5[__MACRO_TEST_HELLO5_MAX];
    if (blobmsg_parse(macro_test_hello5_policy, ARRAY_SIZE(macro_test_hello5_policy), tb_macro_test_hello5, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_macro_test_hello5[MACRO_TEST_HELLO5_ID]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    params->id = blobmsg_get_u32(tb_macro_test_hello5[MACRO_TEST_HELLO5_ID]);
    return UBUS_STATUS_OK;
}

int macro_test_hello5_serialize(struct blob_buf *b, const struct macro_test_hello5_params_t *params)
{
    int ret;

    ret = blobmsg_add_u32(b, "id", params->id);
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

enum {
    MACRO_TEST_HELLO6_MSG,
    __MACRO_TEST_HELLO6_MAX
};

static const struct blobmsg_policy macro_test_hello6_policy[] = {
    [MACRO_TEST_HELLO6_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
};

int macro_test_hello6_deserialize(struct blob_attr *msg, struct macro_test_hello6_params_t *params)
{
    struct blob_attr *tb_macro_test_hello6[__MACRO_TEST_HELLO6_MAX];
    if (blobmsg_parse(macro_test_hello6_policy, ARRAY_SIZE(macro_test_hello6_policy), tb_macro_test_hello6, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_macro_test_hello6[MACRO_TEST_HELLO6_MSG]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    params->msg = blobmsg_get_string(tb_macro_test_hello6[MACRO_TEST_HELLO6_MSG]);
    return UBUS_STATUS_OK;
}

int macro_test_hello6_serialize(struct blob_buf *b, const struct macro_test_hello6_params_t *params)
{
    int ret;

    ret = blobmsg_add_string(b, "msg", params->msg);
    if (ret < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }
    return UBUS_STATUS_OK;
}

static const struct ubus_method macro_test_methods[] = {
    { __UBUS_METHOD("hello", macro_test_hello_handler, 1, macro_test_hello_policy, 5) },
    UBUS_METHOD_MASK("hello5", macro_test_hello5_handler, macro_test_hello5_policy, 2),
    UBUS_METHOD_TAG("hello6", macro_test_hello6_handler, macro_test_hello6_policy, 10),
    { __UBUS_METHOD_NOARG("hello7", macro_test_hello7_handler, 4, 0) },
    UBUS_METHOD_TAG_NOARG("hello8", macro_test_hello8_handler, 15),
    { __UBUS_METHOD_NOARG("hello9", macro_test_hello9_handler, 8, 20) }
};

static struct ubus_object_type macro_test_object_type =
    UBUS_OBJECT_TYPE("macro_test", macro_test_methods);

struct ubus_object macro_test_object = {
    .name = "macro_test",
    .type = &macro_test_object_type,
    .methods = macro_test_methods,
    .n_methods = ARRAY_SIZE(macro_test_methods),
};