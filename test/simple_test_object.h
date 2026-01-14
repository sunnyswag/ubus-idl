/* Generated from ubus IDL - simple_test */

#ifndef __SIMPLE_TEST_OBJECT_H__
#define __SIMPLE_TEST_OBJECT_H__

#include <libubus.h>
#include <stdint.h>


struct simple_test_hello1 {
    int32_t id1;
    const char * msg1;
    /* Bitfields for optional field presence */
    union {
        struct {
            uint8_t has_msg1: 1;
        };
        uint8_t has_fields;
    };
};

struct simple_test_response {
    const char * weather;
    const char * res;
};

struct simple_test_hello_params {
    const char * msg;
    int32_t id;
    /* Bitfields for optional field presence */
    union {
        struct {
            uint8_t has_id: 1;
        };
        uint8_t has_fields;
    };
};

enum {
    SIMPLE_TEST_HELLO_MSG,
    SIMPLE_TEST_HELLO_ID,
    __SIMPLE_TEST_HELLO_MAX
};

enum {
    SIMPLE_TEST_HELLO1_ID1,
    SIMPLE_TEST_HELLO1_MSG1,
    __SIMPLE_TEST_HELLO1_MAX
};

int simple_test_hello_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int simple_test_hello2_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int xxx(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);

int simple_test_hello_deserialize(struct blob_attr *msg, struct simple_test_hello_params *params);
int simple_test_hello_serialize(struct blob_buf *b, const struct simple_test_hello_params *params);
int simple_test_hello1_deserialize(struct blob_attr *msg, struct simple_test_hello1 *params);
int simple_test_hello1_serialize(struct blob_buf *b, const struct simple_test_hello1 *params);

extern struct ubus_object simple_test_object;

#endif /* __SIMPLE_TEST_OBJECT_H__ */
