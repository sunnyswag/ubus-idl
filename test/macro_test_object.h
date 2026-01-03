/* Generated from ubus IDL - macro_test */

#ifndef __UBUS_IDL_GENERATED_H__
#define __UBUS_IDL_GENERATED_H__

#include <libubus.h>
#include <stdint.h>

struct macro_test_hello_params_t {
    int32_t id;
    const char * msg;
};

struct macro_test_hello5_params_t {
    int32_t id;
};

struct macro_test_hello6_params_t {
    const char * msg;
};

int macro_test_hello_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int macro_test_hello5_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int macro_test_hello6_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int macro_test_hello7_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int macro_test_hello8_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int macro_test_hello9_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int macro_test_hello_deserialize(struct blob_attr *msg, struct macro_test_hello_params_t *params);
int macro_test_hello_serialize(struct blob_buf *b, const struct macro_test_hello_params_t *params);
int macro_test_hello5_deserialize(struct blob_attr *msg, struct macro_test_hello5_params_t *params);
int macro_test_hello5_serialize(struct blob_buf *b, const struct macro_test_hello5_params_t *params);
int macro_test_hello6_deserialize(struct blob_attr *msg, struct macro_test_hello6_params_t *params);
int macro_test_hello6_serialize(struct blob_buf *b, const struct macro_test_hello6_params_t *params);

extern struct ubus_object macro_test_object;

#endif /* __UBUS_IDL_GENERATED_H__ */