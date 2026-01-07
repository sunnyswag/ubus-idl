/* Generated from ubus IDL - special_types_test */

#ifndef __SPECIAL_TYPES_TEST_OBJECT_H__
#define __SPECIAL_TYPES_TEST_OBJECT_H__

#include <libubus.h>
#include <stdint.h>

/* Helper macros for optional field operations */
#define UBUS_IDL_HAS_FIELD(params, index) ((params)->has_fields & (1U << index))
#define UBUS_IDL_SET_FIELD(params, index) ((params)->has_fields |= (1U << index))
#define UBUS_IDL_CLEAR_FIELD(params, index) ((params)->has_fields &= ~(1U << index))


struct special_types_test_array_params {
    struct blob_attr * array_val;
};

struct special_types_test_unspec_params {
    struct blob_attr * unspec_val;
};

struct special_types_test_table_params {
    struct custom_table_type * table_val;
};

struct special_types_test_all_special_params {
    struct blob_attr * array_val;
    struct blob_attr * unspec_val;
    struct custom_table_type * table_val;
};

enum {
    SPECIAL_TYPES_TEST_ARRAY_ARRAY_VAL,
    __SPECIAL_TYPES_TEST_ARRAY_MAX
};

enum {
    SPECIAL_TYPES_TEST_UNSPEC_UNSPEC_VAL,
    __SPECIAL_TYPES_TEST_UNSPEC_MAX
};

enum {
    SPECIAL_TYPES_TEST_TABLE_TABLE_VAL,
    __SPECIAL_TYPES_TEST_TABLE_MAX
};

enum {
    SPECIAL_TYPES_TEST_ALL_SPECIAL_ARRAY_VAL,
    SPECIAL_TYPES_TEST_ALL_SPECIAL_UNSPEC_VAL,
    SPECIAL_TYPES_TEST_ALL_SPECIAL_TABLE_VAL,
    __SPECIAL_TYPES_TEST_ALL_SPECIAL_MAX
};

int special_types_test_array_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int special_types_test_unspec_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int special_types_test_table_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);
int special_types_test_all_special_handler(struct ubus_context *ctx, struct ubus_object *obj, struct ubus_request_data *req, const char *method, struct blob_attr *msg);

int special_types_test_array_deserialize(struct blob_attr *msg, struct special_types_test_array_params *params);
int special_types_test_array_serialize(struct blob_buf *b, const struct special_types_test_array_params *params);
int special_types_test_unspec_deserialize(struct blob_attr *msg, struct special_types_test_unspec_params *params);
int special_types_test_unspec_serialize(struct blob_buf *b, const struct special_types_test_unspec_params *params);
int special_types_test_table_deserialize(struct blob_attr *msg, struct special_types_test_table_params *params);
int special_types_test_table_serialize(struct blob_buf *b, const struct special_types_test_table_params *params);
int special_types_test_all_special_deserialize(struct blob_attr *msg, struct special_types_test_all_special_params *params);
int special_types_test_all_special_serialize(struct blob_buf *b, const struct special_types_test_all_special_params *params);

extern struct ubus_object special_types_test_object;

#endif /* __SPECIAL_TYPES_TEST_OBJECT_H__ */
