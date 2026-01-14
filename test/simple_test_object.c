/* Generated from ubus IDL - simple_test */

#include <libubox/blobmsg_json.h>
#include <libubus.h>
#include "simple_test_object.h"

/* Helper macros for field serialization with error checking */
#define UBUS_IDL_ADD(type, b, name, val) \
    do { \
        int _ret = blobmsg_add_##type((b), (name), (val)); \
        if (_ret < 0) { \
            return UBUS_STATUS_INVALID_ARGUMENT; \
        } \
    } while (0)

static const struct blobmsg_policy simple_test_hello_policy[] = {
    [SIMPLE_TEST_HELLO_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING },
    [SIMPLE_TEST_HELLO_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 }
};

int simple_test_hello_deserialize(struct blob_attr *msg, struct simple_test_hello_params *params)
{
    struct blob_attr *tb_simple_test_hello[__SIMPLE_TEST_HELLO_MAX];
    if (blobmsg_parse(simple_test_hello_policy, ARRAY_SIZE(simple_test_hello_policy), tb_simple_test_hello, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_simple_test_hello[SIMPLE_TEST_HELLO_MSG]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->has_fields = 0;
    params->msg = blobmsg_get_string(tb_simple_test_hello[SIMPLE_TEST_HELLO_MSG]);

    if (tb_simple_test_hello[SIMPLE_TEST_HELLO_ID]) {
        params->id = blobmsg_get_u32(tb_simple_test_hello[SIMPLE_TEST_HELLO_ID]);
        params->has_id = 1;
    }
    return UBUS_STATUS_OK;
}

int simple_test_hello_serialize(struct blob_buf *b, const struct simple_test_hello_params *params)
{
    UBUS_IDL_ADD(string, b, "msg", params->msg);
    if (params->has_id) {
        blobmsg_add_u32(b, "id", params->id);
    }
    return UBUS_STATUS_OK;
}

static const struct blobmsg_policy simple_test_hello1_policy[] = {
    [SIMPLE_TEST_HELLO1_ID1] = { .name = "id1", .type = BLOBMSG_TYPE_INT32 },
    [SIMPLE_TEST_HELLO1_MSG1] = { .name = "msg1", .type = BLOBMSG_TYPE_STRING }
};

int simple_test_hello1_deserialize(struct blob_attr *msg, struct simple_test_hello1 *params)
{
    struct blob_attr *tb_simple_test_hello1[__SIMPLE_TEST_HELLO1_MAX];
    if (blobmsg_parse(simple_test_hello1_policy, ARRAY_SIZE(simple_test_hello1_policy), tb_simple_test_hello1, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_simple_test_hello1[SIMPLE_TEST_HELLO1_ID1]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->has_fields = 0;
    params->id1 = blobmsg_get_u32(tb_simple_test_hello1[SIMPLE_TEST_HELLO1_ID1]);

    if (tb_simple_test_hello1[SIMPLE_TEST_HELLO1_MSG1]) {
        params->msg1 = blobmsg_get_string(tb_simple_test_hello1[SIMPLE_TEST_HELLO1_MSG1]);
        params->has_msg1 = 1;
    }
    return UBUS_STATUS_OK;
}

int simple_test_hello1_serialize(struct blob_buf *b, const struct simple_test_hello1 *params)
{
    UBUS_IDL_ADD(u32, b, "id1", params->id1);
    if (params->has_msg1) {
        blobmsg_add_string(b, "msg1", params->msg1);
    }
    return UBUS_STATUS_OK;
}

int xxx(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg)
{
    struct simple_test_hello1 params;

    if (simple_test_hello1_deserialize(msg, &params) != UBUS_STATUS_OK) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    // TODO: Use params struct here
    // Example: int32_t id = params.id;

    // Custom handler from xxx
    // Include your custom handler implementation here
    // #include "xxx.c"

    // Call custom handler function
    // return xxx_impl(ctx, obj, req, method, msg, ...);

    return UBUS_STATUS_OK;
}

static const struct ubus_method simple_test_methods[] = {
    UBUS_METHOD("hello", simple_test_hello_handler, simple_test_hello_policy),
    UBUS_METHOD("hello2", simple_test_hello2_handler, simple_test_hello1_policy),
    UBUS_METHOD("hello3", xxx, simple_test_hello1_policy)
};

static struct ubus_object_type simple_test_object_type =
    UBUS_OBJECT_TYPE("simple_test", simple_test_methods);

struct ubus_object simple_test_object = {
    .name = "simple_test",
    .type = &simple_test_object_type,
    .methods = simple_test_methods,
    .n_methods = ARRAY_SIZE(simple_test_methods),
};
