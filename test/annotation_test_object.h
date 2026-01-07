/* Generated from ubus IDL - annotation_test */

#ifndef __ANNOTATION_TEST_OBJECT_H__
#define __ANNOTATION_TEST_OBJECT_H__

#include <libubus.h>
#include <stdint.h>

/* Helper macros for optional field operations */
#define UBUS_IDL_HAS_FIELD(params, index) ((params)->has_fields & (1U << index))
#define UBUS_IDL_SET_FIELD(params, index) ((params)->has_fields |= (1U << index))
#define UBUS_IDL_CLEAR_FIELD(params, index) ((params)->has_fields &= ~(1U << index))


struct annotation_test_hello_params {
    int32_t id;
    const char * msg;
};

struct annotation_test_hello1_params {
    int32_t id;
};

struct annotation_test_hello2_params {
    const char * msg;
};

enum {
    ANNOTATION_TEST_HELLO_ID,
    ANNOTATION_TEST_HELLO_MSG,
    __ANNOTATION_TEST_HELLO_MAX
};

enum {
    ANNOTATION_TEST_HELLO1_ID,
    __ANNOTATION_TEST_HELLO1_MAX
};

enum {
    ANNOTATION_TEST_HELLO2_MSG,
    __ANNOTATION_TEST_HELLO2_MAX
};

int annotation_test_hello_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int annotation_test_hello1_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int annotation_test_hello2_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int annotation_test_hello3_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int annotation_test_hello4_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int annotation_test_hello5_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);

int annotation_test_hello_deserialize(struct blob_attr *msg, struct annotation_test_hello_params *params);
int annotation_test_hello_serialize(struct blob_buf *b, const struct annotation_test_hello_params *params);
int annotation_test_hello1_deserialize(struct blob_attr *msg, struct annotation_test_hello1_params *params);
int annotation_test_hello1_serialize(struct blob_buf *b, const struct annotation_test_hello1_params *params);
int annotation_test_hello2_deserialize(struct blob_attr *msg, struct annotation_test_hello2_params *params);
int annotation_test_hello2_serialize(struct blob_buf *b, const struct annotation_test_hello2_params *params);

extern struct ubus_object annotation_test_object;

#endif /* __ANNOTATION_TEST_OBJECT_H__ */
