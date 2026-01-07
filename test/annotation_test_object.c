/* Generated from ubus IDL - annotation_test */

#include <libubox/blobmsg_json.h>
#include <libubus.h>
#include "annotation_test_object.h"

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
    ANNOTATION_TEST_HELLO_ID,
    ANNOTATION_TEST_HELLO_MSG,
    __ANNOTATION_TEST_HELLO_MAX
};

static const struct blobmsg_policy annotation_test_hello_policy[] = {
    [ANNOTATION_TEST_HELLO_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 },
    [ANNOTATION_TEST_HELLO_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
};

int annotation_test_hello_deserialize(struct blob_attr *msg, struct annotation_test_hello_params *params)
{
    struct blob_attr *tb_annotation_test_hello[__ANNOTATION_TEST_HELLO_MAX];
    if (blobmsg_parse(annotation_test_hello_policy, ARRAY_SIZE(annotation_test_hello_policy), tb_annotation_test_hello, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_annotation_test_hello[ANNOTATION_TEST_HELLO_ID] || !tb_annotation_test_hello[ANNOTATION_TEST_HELLO_MSG]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->id = blobmsg_get_u32(tb_annotation_test_hello[ANNOTATION_TEST_HELLO_ID]);
    params->msg = blobmsg_get_string(tb_annotation_test_hello[ANNOTATION_TEST_HELLO_MSG]);
    return UBUS_STATUS_OK;
}

int annotation_test_hello_serialize(struct blob_buf *b, const struct annotation_test_hello_params *params)
{
    UBUS_IDL_ADD(u32, b, "id", params->id);
    UBUS_IDL_ADD(string, b, "msg", params->msg);
    return UBUS_STATUS_OK;
}

enum {
    ANNOTATION_TEST_HELLO1_ID,
    __ANNOTATION_TEST_HELLO1_MAX
};

static const struct blobmsg_policy annotation_test_hello1_policy[] = {
    [ANNOTATION_TEST_HELLO1_ID] = { .name = "id", .type = BLOBMSG_TYPE_INT32 }
};

int annotation_test_hello1_deserialize(struct blob_attr *msg, struct annotation_test_hello1_params *params)
{
    struct blob_attr *tb_annotation_test_hello1[__ANNOTATION_TEST_HELLO1_MAX];
    if (blobmsg_parse(annotation_test_hello1_policy, ARRAY_SIZE(annotation_test_hello1_policy), tb_annotation_test_hello1, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_annotation_test_hello1[ANNOTATION_TEST_HELLO1_ID]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->id = blobmsg_get_u32(tb_annotation_test_hello1[ANNOTATION_TEST_HELLO1_ID]);
    return UBUS_STATUS_OK;
}

int annotation_test_hello1_serialize(struct blob_buf *b, const struct annotation_test_hello1_params *params)
{
    UBUS_IDL_ADD(u32, b, "id", params->id);
    return UBUS_STATUS_OK;
}

enum {
    ANNOTATION_TEST_HELLO2_MSG,
    __ANNOTATION_TEST_HELLO2_MAX
};

static const struct blobmsg_policy annotation_test_hello2_policy[] = {
    [ANNOTATION_TEST_HELLO2_MSG] = { .name = "msg", .type = BLOBMSG_TYPE_STRING }
};

int annotation_test_hello2_deserialize(struct blob_attr *msg, struct annotation_test_hello2_params *params)
{
    struct blob_attr *tb_annotation_test_hello2[__ANNOTATION_TEST_HELLO2_MAX];
    if (blobmsg_parse(annotation_test_hello2_policy, ARRAY_SIZE(annotation_test_hello2_policy), tb_annotation_test_hello2, blob_data(msg), blob_len(msg)) < 0) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    if (!tb_annotation_test_hello2[ANNOTATION_TEST_HELLO2_MSG]) {
        return UBUS_STATUS_INVALID_ARGUMENT;
    }

    params->msg = blobmsg_get_string(tb_annotation_test_hello2[ANNOTATION_TEST_HELLO2_MSG]);
    return UBUS_STATUS_OK;
}

int annotation_test_hello2_serialize(struct blob_buf *b, const struct annotation_test_hello2_params *params)
{
    UBUS_IDL_ADD(string, b, "msg", params->msg);
    return UBUS_STATUS_OK;
}

static const struct ubus_method annotation_test_methods[] = {
    { __UBUS_METHOD("hello", annotation_test_hello_handler, 1, annotation_test_hello_policy, 5) },
    UBUS_METHOD_MASK("hello1", annotation_test_hello1_handler, annotation_test_hello1_policy, 2),
    UBUS_METHOD_TAG("hello2", annotation_test_hello2_handler, annotation_test_hello2_policy, 10),
    { __UBUS_METHOD_NOARG("hello3", annotation_test_hello3_handler, 4, 0) },
    UBUS_METHOD_TAG_NOARG("hello4", annotation_test_hello4_handler, 15),
    { __UBUS_METHOD_NOARG("hello5", annotation_test_hello5_handler, 8, 20) }
};

static struct ubus_object_type annotation_test_object_type =
    UBUS_OBJECT_TYPE("annotation_test", annotation_test_methods);

struct ubus_object annotation_test_object = {
    .name = "annotation_test",
    .type = &annotation_test_object_type,
    .methods = annotation_test_methods,
    .n_methods = ARRAY_SIZE(annotation_test_methods),
};
