# Test Files Organization

测试文件已按类别拆分，便于理解和维护：

## Test Files

### 1. `simple_test.uidl` - 基础功能测试
测试基本的 IDL 功能和简单方法：
- 基本类型定义（hello1）
- 全局类型定义（hello_common）
- 简单方法（带参数、无参数）
- 使用已定义类型的方法
- 自定义 handler

**生成文件：**
- `simple_test_object.h`
- `simple_test_object.c`

### 2. `macro_test.uidl` - 宏和注解测试
测试 ubus 宏和注解功能：
- `@name` 注解（重命名方法）
- `@mask` 注解（方法掩码）
- `@tag` 注解（方法标签）
- 各种宏组合（UBUS_METHOD, UBUS_METHOD_MASK, UBUS_METHOD_TAG 等）

**生成文件：**
- `macro_test_object.h`
- `macro_test_object.c`

### 3. `type_test.uidl` - 类型系统测试
测试所有支持的类型和可选字段：
- 所有基本类型（int8, int16, int32, int64, bool, double, string）
- 可选字段（optional fields）
- 类型定义中的可选字段
- 方法参数中的类型

**生成文件：**
- `type_test_object.h`
- `type_test_object.c`

**注意：** 此文件已被分类测试文件替代，建议使用分类测试文件进行测试。

## Usage

生成单个测试文件的代码：
```bash
python3 -m ubus_idl test/simple_test.uidl -o test/
python3 -m ubus_idl test/macro_test.uidl -o test/
python3 -m ubus_idl test/type_test.uidl -o test/
```

生成综合测试：
```bash
python3 -m ubus_idl test/test.uidl -o test/
```

## Test Coverage

- ✅ 基本类型和方法定义
- ✅ 全局类型定义
- ✅ 对象内类型定义
- ✅ 可选字段（optional fields）
- ✅ 所有支持的类型（int32, int64, bool, double, string）
- ✅ 方法注解（@name, @mask, @tag）
- ✅ 所有 UBUS_METHOD 宏变体
- ✅ 自定义 handler
- ✅ 序列化和反序列化函数

