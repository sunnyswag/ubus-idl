/* Generated from ubus IDL - type_test */

#ifndef __TYPE_TEST_OBJECT_H__
#define __TYPE_TEST_OBJECT_H__

#include <libubus.h>
#include <stdint.h>

/* Helper macros for optional field operations */
#define UBUS_IDL_HAS_FIELD(params, mask) ((params)->has_fields & (mask))
#define UBUS_IDL_SET_FIELD(params, mask) ((params)->has_fields |= (mask))
#define UBUS_IDL_CLEAR_FIELD(params, mask) ((params)->has_fields &= ~(mask))


struct type_with_all_types {
    int8_t int8_field;
    int16_t int16_field;
    int32_t int32_field;
    int64_t int64_field;
    bool bool_field;
    double double_field;
    const char * string_field;
    int8_t optional_int8;
    int16_t optional_int16;
    int32_t optional_int32;
    int64_t optional_int64;
    bool optional_bool;
    double optional_double;
    const char * optional_string;
    unsigned int has_fields;
};
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_INT8 (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_INT8)
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_INT16 (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_INT16)
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_INT32 (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_INT32)
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_INT64 (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_INT64)
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_BOOL (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_BOOL)
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_DOUBLE (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_DOUBLE)
#define TYPE_WITH_ALL_TYPES_HAS_OPTIONAL_STRING (1U << TYPE_WITH_ALL_TYPES_OPTIONAL_STRING)

struct type_test_all_types_params {
    int8_t int8_val;
    int16_t int16_val;
    int32_t int32_val;
    int64_t int64_val;
    bool bool_val;
    double double_val;
    const char * string_val;
};


int type_test_all_types_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int type_test_type_with_all_types_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);

int type_test_all_types_deserialize(struct blob_attr *msg, struct type_test_all_types_params *params);
int type_test_all_types_serialize(struct blob_buf *b, const struct type_test_all_types_params *params);
int type_with_all_types_deserialize(struct blob_attr *msg, struct type_with_all_types *params);
int type_with_all_types_serialize(struct blob_buf *b, const struct type_with_all_types *params);

extern struct ubus_object type_test_object;

#endif /* __TYPE_TEST_OBJECT_H__ */
