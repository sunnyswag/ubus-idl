#!/usr/bin/env python3
"""Temporary test script"""

import sys
from pathlib import Path

# Add project path (parent directory)
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ubus_idl.parser import Parser
    from ubus_idl.codegen import CodeGenerator
    
    # Read test file (use simple_test.uidl by default, or specify via command line)
    if len(sys.argv) > 1:
        test_file = Path(__file__).parent / sys.argv[1]
    else:
        test_file = Path(__file__).parent / "simple_test.uidl"
    output_dir = Path(__file__).parent
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Parsing IDL file...")
    parser = Parser()
    document = parser.parse(content)
    
    print(f"Parsed {len(document.objects)} object(s)")
    for obj in document.objects:
        print(f"  Object: {obj.name}")
        print(f"    Types: {len(obj.types)}")
        print(f"    Methods: {len(obj.methods)}")
    
    print("\nGenerating C code...")
    generator = CodeGenerator(document)
    generated_files = generator.generate()
    
    # Write generated files to test directory
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in generated_files.items():
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {output_path}")
    
    print("\n✓ Test passed!")
    
except ImportError as e:
    print(f"Error: {e}")
    print("Please install lark: pip install lark")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

