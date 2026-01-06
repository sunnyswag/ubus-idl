#!/usr/bin/env python3
"""通用工具：处理 UIDL 文件并生成 C 代码

用法:
    python process_uidl.py <输入文件夹> [输出文件夹]
    
    如果未提供输出文件夹，则输出文件将生成在输入文件夹中。
    处理输入文件夹中的所有 .uidl 文件。
"""

import sys
import argparse
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ubus_idl.parser import Parser
    from ubus_idl.codegen import CodeGenerator
    
    def process_uidl_file(uidl_file: Path, output_dir: Path):
        """处理单个 UIDL 文件并生成 C 代码"""
        print(f"\n{'='*70}")
        print(f"处理中: {uidl_file}")
        print('='*70)
        
        with open(uidl_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("解析 IDL 文件...")
        parser = Parser()
        document = parser.parse(content)
        
        print(f"已解析 {len(document.objects)} 个对象")
        for obj in document.objects:
            print(f"  对象: {obj.name}")
            print(f"    类型: {len(obj.types)}")
            print(f"    方法: {len(obj.methods)}")
        
        print("\n生成 C 代码...")
        generator = CodeGenerator(document)
        generated_files = generator.generate()
        
        # 写入生成的文件到输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in generated_files.items():
            output_path = output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已生成: {output_path}")
        
        print(f"✓ 成功处理 {uidl_file.name}")
        return True
    
    def main():
        parser = argparse.ArgumentParser(
            description="处理 UIDL 文件并生成 C 代码",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  python process_uidl.py ./test
  python process_uidl.py ./test ./output
            """
        )
        parser.add_argument(
            "input_dir",
            type=str,
            help="输入文件夹路径（包含 .uidl 文件）"
        )
        parser.add_argument(
            "output_dir",
            type=str,
            nargs='?',
            default=None,
            help="输出文件夹路径（可选，默认为输入文件夹）"
        )
        
        args = parser.parse_args()
        
        # 确定输入路径
        input_dir = Path(args.input_dir)
        if not input_dir.is_absolute():
            input_dir = Path.cwd() / input_dir
        
        # 检查输入路径是否存在
        if not input_dir.exists():
            print(f"错误: 路径不存在: {input_dir}", file=sys.stderr)
            sys.exit(1)
        
        if not input_dir.is_dir():
            print(f"错误: 路径不是文件夹: {input_dir}", file=sys.stderr)
            sys.exit(1)
        
        # 确定输出路径
        if args.output_dir:
            output_dir = Path(args.output_dir)
            if not output_dir.is_absolute():
                output_dir = Path.cwd() / output_dir
        else:
            # 如果不提供输出文件夹，使用输入文件夹
            output_dir = input_dir
        
        # 查找所有 .uidl 文件
        uidl_files = sorted(input_dir.glob("*.uidl"))
        if not uidl_files:
            print(f"错误: 在文件夹中未找到 .uidl 文件: {input_dir}", file=sys.stderr)
            sys.exit(1)
        
        print(f"在 {input_dir} 中找到 {len(uidl_files)} 个 .uidl 文件")
        print(f"输出目录: {output_dir}")
        
        success_count = 0
        for uidl_file in uidl_files:
            try:
                if process_uidl_file(uidl_file, output_dir):
                    success_count += 1
            except Exception as e:
                print(f"\n✗ 处理 {uidl_file.name} 时出错: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*70}")
        print(f"摘要: {success_count}/{len(uidl_files)} 个文件处理成功")
        print('='*70)
        
        if success_count == len(uidl_files):
            print("\n✓ 所有文件处理成功!")
            sys.exit(0)
        else:
            print(f"\n✗ {len(uidl_files) - success_count} 个文件处理失败", file=sys.stderr)
            sys.exit(1)
    
    if __name__ == "__main__":
        main()
    
except ImportError as e:
    print(f"错误: {e}", file=sys.stderr)
    print("请安装依赖: pip install lark", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

