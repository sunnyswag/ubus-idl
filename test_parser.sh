#!/bin/bash
# 测试脚本：生成所有 .uidl 文件的 C 和 TypeScript 代码

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 测试目录
TEST_DIR="${SCRIPT_DIR}/test"

# 检查 test 目录是否存在
if [ ! -d "$TEST_DIR" ]; then
    echo "错误: test 目录不存在: $TEST_DIR"
    exit 1
fi

# 检查是否存在虚拟环境，如果存在则激活
if [ -d "${SCRIPT_DIR}/venv" ]; then
    echo "检测到虚拟环境，正在激活..."
    source "${SCRIPT_DIR}/venv/bin/activate"
fi

echo "=========================================="
echo "ubus-idl 代码生成测试"
echo "输入目录: $TEST_DIR"
echo "输出目录: $TEST_DIR"
echo "生成目标: C + TypeScript"
echo "=========================================="
echo ""

# 计数器
success_count=0
fail_count=0

# 遍历所有 .uidl 文件
for uidl_file in "$TEST_DIR"/*.uidl; do
    if [ -f "$uidl_file" ]; then
        filename=$(basename "$uidl_file")
        echo "处理: $filename"
        
        # 使用 ubus_idl 模块生成所有代码 (C + TypeScript)
        python3 -m ubus_idl "$uidl_file" -t all -o "$TEST_DIR" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "  ✓ 成功"
            ((success_count++))
        else
            echo "  ✗ 失败"
            ((fail_count++))
        fi
        echo ""
    fi
done

echo "=========================================="
echo "结果: 成功 $success_count, 失败 $fail_count"
echo "=========================================="

if [ $fail_count -gt 0 ]; then
    exit 1
fi
