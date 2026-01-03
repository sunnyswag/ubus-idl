"""Command line tool"""

import argparse
import sys
from pathlib import Path
from .parser import Parser
from .codegen import CodeGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Ubus IDL compiler - Generate ubus C code from .uidl files"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input .uidl file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=".",
        help="Output directory for generated files (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse
    try:
        parser = Parser()
        document = parser.parse(content)
    except Exception as e:
        print(f"Error parsing IDL file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generate code
    try:
        generator = CodeGenerator(document)
        generated_files = generator.generate()
    except Exception as e:
        print(f"Error generating code: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Write files
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, content in generated_files.items():
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()

