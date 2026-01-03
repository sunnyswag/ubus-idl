# ubus-idl

Ubus Interface Definition Language - IDL compiler for generating ubus C code

## Installation

```bash
pip install -r requirements.txt
# or
python setup.py install
```

## Usage

```bash
ubus-idl input.uidl -o output_dir
```

Or use Python module:

```bash
python -m ubus_idl input.uidl -o output_dir
```

## IDL Syntax

### Object Definition

```idl
object ObjectName {
    // Type definition
    type_name: {
        field: int32
        optional_field?: string
    }
    
    // Method definition
    method_name(param: int32, msg: string)
    
    // Method with annotations
    @name("method_name")
    @mask(0x1)
    @tag(0x1)
    method_with_annotations(id: int32)
    
    // Method without parameters
    no_param_method()
    
    // Using defined type
    method_with_type(type_name)
}
```

### Supported Types

- `int8` - 8-bit integer (BLOBMSG_TYPE_INT8)
- `int16` - 16-bit integer (BLOBMSG_TYPE_INT16)
- `int32` - 32-bit integer (BLOBMSG_TYPE_INT32)
- `int64` - 64-bit integer (BLOBMSG_TYPE_INT64)
- `string` - String (BLOBMSG_TYPE_STRING)
- `bool` - Boolean (BLOBMSG_TYPE_BOOL)
- `double` - Double precision floating point (BLOBMSG_TYPE_DOUBLE)
- `array` - Array type (BLOBMSG_TYPE_ARRAY)
- `unspec` - Unspecified type (BLOBMSG_TYPE_UNSPEC)
- Custom types - Uses BLOBMSG_TYPE_TABLE (via type definitions)

### Annotations

- `@name("value")` - Specify method name in ubus (overrides method name)
- `@mask(value)` - Specify method mask (bitmask, e.g., 0x1)
- `@tag(value)` - Specify method tag (bitmask, e.g., 0x1)

### Optional Fields

Use `?` to mark optional fields:

```idl
type_name: {
    required: int32
    optional?: string
}
```

## Generated Code

For each object, two files are generated:

- `{object_name}_object.h` - Header file (function declarations, object declaration)
- `{object_name}_object.c` - Implementation file (policy, handler functions, method and object definitions)

## Examples

See test files in `test/` directory for examples:
- `test/simple_test.uidl` - Basic functionality
- `test/macro_test.uidl` - Macro and annotation tests
- `test/type_test.uidl` - Type system tests

Generate code:

```bash
ubus-idl test/simple_test.uidl -o test/output
```

## Development

Run tests:

```bash
python test_parser.py
```
