/* Generated from ubus IDL - simple_test */

#include <libubox/blobmsg_json.h>
#include <libubus.h>
#include "simple_test_object.h"

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

enum {
    SIMPLE_TEST_HELLO_ID,
    SIMPLE_TEST_HELLO_MSG,
    __SIMPLE_TEST_HELLO_MAX
};

static const struct blobmsg_policy simple_test_hello_policy[] = {
    [SIMPLE_TEST_HELLO_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 },
    [SIMPLE_TEST_HELLO_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
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

    UBUS_IDL_GET_OPTIONAL(u32, tb_simple_test_hello, SIMPLE_TEST_HELLO_ID, params->id, params, SIMPLE_TEST_HELLO_HAS_ID);
    return UBUS_STATUS_OK;
}

int simple_test_hello_serialize(struct blob_buf *b, const struct simple_test_hello_params *params)
{
    UBUS_IDL_ADD_OPTIONAL(u32, b, "id", params->id, params, SIMPLE_TEST_HELLO_HAS_ID);
    UBUS_IDL_ADD(string, b, "msg", params->msg);
    return UBUS_STATUS_OK;
}

enum {
    SIMPLE_TEST_HELLO1_ID,
    SIMPLE_TEST_HELLO1_MSG,
    __SIMPLE_TEST_HELLO1_MAX
};

static const struct blobmsg_policy simple_test_hello1_policy[] = {
    [SIMPLE_TEST_HELLO1_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 },
    [SIMPLE_TEST_HELLO1_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
};

int simple_test_hello1_deserialize(struct blob_attr *msg, struct simple_test_hello1 *params)
{
    struct blob_attr *tb_simple_test_hello1[__SIMPLE_TEST_HELLO1_MAX];
    if (blobmsg_parse(simple_test_hello1_policy, ARRAY_SIZE(simple_test_hello1_policy), tb_simple_test_hello1, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_simple_test_hello1[SIMPLE_TEST_HELLO1_ID]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->has_fields = 0;
    params->id = blobmsg_get_u32(tb_simple_test_hello1[SIMPLE_TEST_HELLO1_ID]);

    UBUS_IDL_GET_OPTIONAL(string, tb_simple_test_hello1, SIMPLE_TEST_HELLO1_MSG, params->msg, params, SIMPLE_TEST_HELLO1_HAS_MSG);
    return UBUS_STATUS_OK;
}

int simple_test_hello1_serialize(struct blob_buf *b, const struct simple_test_hello1 *params)
{
    UBUS_IDL_ADD(u32, b, "id", params->id);
    UBUS_IDL_ADD_OPTIONAL(string, b, "msg", params->msg, params, SIMPLE_TEST_HELLO1_HAS_MSG);
    return UBUS_STATUS_OK;
}

enum {
    HELLO_COMMON_ID,
    HELLO_COMMON_MSG,
    __HELLO_COMMON_MAX
};

static const struct blobmsg_policy hello_common_policy[] = {
    [HELLO_COMMON_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 },
    [HELLO_COMMON_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
};

int hello_common_deserialize(struct blob_attr *msg, struct hello_common *params)
{
    struct blob_attr *tb_hello_common[__HELLO_COMMON_MAX];
    if (blobmsg_parse(hello_common_policy, ARRAY_SIZE(hello_common_policy), tb_hello_common, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_hello_common[HELLO_COMMON_ID]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->has_fields = 0;
    params->id = blobmsg_get_u32(tb_hello_common[HELLO_COMMON_ID]);

    UBUS_IDL_GET_OPTIONAL(string, tb_hello_common, HELLO_COMMON_MSG, params->msg, params, HELLO_COMMON_HAS_MSG);
    return UBUS_STATUS_OK;
}

int hello_common_serialize(struct blob_buf *b, const struct hello_common *params)
{
    UBUS_IDL_ADD(u32, b, "id", params->id);
    UBUS_IDL_ADD_OPTIONAL(string, b, "msg", params->msg, params, HELLO_COMMON_HAS_MSG);
    return UBUS_STATUS_OK;
}

int handler1(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg)
{
    struct simple_test_hello1 params;

    if (simple_test_hello1_deserialize(msg, &params) != UBUS_STATUS_OK) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    // TODO: Use params struct here
    // Example: int32_t id = params.id;

    // Custom handler from handler1
    // Include your custom handler implementation here
    // #include "handler1.c"

    // Call custom handler function
    // return handler1_impl(ctx, obj, req, method, msg, ...);

    return UBUS_STATUS_OK;
}

static const struct ubus_method simple_test_methods[] = {
    UBUS_METHOD("hello", simple_test_hello_handler, simple_test_hello_policy),
    UBUS_METHOD_NOARG("hello1", simple_test_hello1_handler),
    UBUS_METHOD("hello2", simple_test_hello2_handler, simple_test_hello1_policy),
    UBUS_METHOD("hello3", handler1, simple_test_hello1_policy),
    UBUS_METHOD("hello4", simple_test_hello4_handler, hello_common_policy)
};

static struct ubus_object_type simple_test_object_type =
    UBUS_OBJECT_TYPE("simple_test", simple_test_methods);

struct ubus_object simple_test_object = {
    .name = "simple_test",
    .type = &simple_test_object_type,
    .methods = simple_test_methods,
    .n_methods = ARRAY_SIZE(simple_test_methods),
};
