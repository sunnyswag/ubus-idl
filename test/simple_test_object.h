/* Generated from ubus IDL - simple_test */

#ifndef __SIMPLE_TEST_OBJECT_H__
#define __SIMPLE_TEST_OBJECT_H__

#include <libubus.h>
#include <stdint.h>


struct hello_common {
    int32_t id;
    const char * msg;
    /* Bitfields for optional field presence */
    union {
        struct {
            uint8_t has_msg: 1;
        };
        uint8_t has_fields;
    };
};

struct simple_test_hello1 {
    int32_t id;
    const char * msg;
    /* Bitfields for optional field presence */
    union {
        struct {
            uint8_t has_msg: 1;
        };
        uint8_t has_fields;
    };
};

struct simple_test_hello_params {
    int32_t id;
    const char * msg;
    /* Bitfields for optional field presence */
    union {
        struct {
        };
        uint8_t has_fields;
    };
};

enum {
    SIMPLE_TEST_HELLO_ID,
    SIMPLE_TEST_HELLO_MSG,
    __SIMPLE_TEST_HELLO_MAX
};

enum {
    SIMPLE_TEST_HELLO1_ID,
    SIMPLE_TEST_HELLO1_MSG,
    __SIMPLE_TEST_HELLO1_MAX
};

enum {
    HELLO_COMMON_ID,
    HELLO_COMMON_MSG,
    __HELLO_COMMON_MAX
};

int simple_test_hello_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int simple_test_hello1_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int simple_test_hello2_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int handler1(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int simple_test_hello4_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);

int simple_test_hello_deserialize(struct blob_attr *msg, struct simple_test_hello_params *params);
int simple_test_hello_serialize(struct blob_buf *b, const struct simple_test_hello_params *params);
int simple_test_hello1_deserialize(struct blob_attr *msg, struct simple_test_hello1 *params);
int simple_test_hello1_serialize(struct blob_buf *b, const struct simple_test_hello1 *params);
int hello_common_deserialize(struct blob_attr *msg, struct hello_common *params);
int hello_common_serialize(struct blob_buf *b, const struct hello_common *params);

extern struct ubus_object simple_test_object;

#endif /* __SIMPLE_TEST_OBJECT_H__ */
