#!/bin/bash
# 测试脚本：使用 process_uidl.py 处理 test 目录

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
echo "测试 process_uidl.py"
echo "输入目录: $TEST_DIR"
echo "输出目录: $TEST_DIR (默认)"
echo "=========================================="
echo ""

# 调用 process_uidl.py，不提供输出目录（将输出到输入目录）
python3 "${SCRIPT_DIR}/process_uidl.py" "$TEST_DIR"

# 检查退出状态
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 测试完成!"
else
    echo ""
    echo "✗ 测试失败!"
    exit 1
fi

