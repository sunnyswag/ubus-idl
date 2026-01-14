/* Generated from ubus IDL - type_test */

#ifndef __TYPE_TEST_OBJECT_H__
#define __TYPE_TEST_OBJECT_H__

#include <libubus.h>
#include <stdint.h>


struct type_test_all_types_params {
    int8_t int8_val;
    int16_t int16_val;
    int32_t int32_val;
    int64_t int64_val;
    bool bool_val;
    double double_val;
    const char * string_val;
};

enum {
    TYPE_TEST_ALL_TYPES_INT8_VAL,
    TYPE_TEST_ALL_TYPES_INT16_VAL,
    TYPE_TEST_ALL_TYPES_INT32_VAL,
    TYPE_TEST_ALL_TYPES_INT64_VAL,
    TYPE_TEST_ALL_TYPES_BOOL_VAL,
    TYPE_TEST_ALL_TYPES_DOUBLE_VAL,
    TYPE_TEST_ALL_TYPES_STRING_VAL,
    __TYPE_TEST_ALL_TYPES_MAX
};

int type_test_all_types_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int type_test_type_with_all_types_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);

int type_test_all_types_deserialize(struct blob_attr *msg, struct type_test_all_types_params *params);
int type_test_all_types_serialize(struct blob_buf *b, const struct type_test_all_types_params *params);

extern struct ubus_object type_test_object;

#endif /* __TYPE_TEST_OBJECT_H__ */
