#!/usr/bin/env python3
"""Test script for ubus IDL parser and code generator

Usage:
    python test_parser.py [file_or_directory]
    
    If no argument is provided, processes simple_test.uidl in the test directory.
    If a file is provided, processes that single file.
    If a directory is provided, processes all .uidl files in that directory.
"""

import sys
from pathlib import Path

# Add project path (parent directory)
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ubus_idl.parser import Parser
    from ubus_idl.codegen import CodeGenerator
    
    def process_uidl_file(uidl_file: Path, output_dir: Path):
        """Process a single UIDL file and generate C code"""
        print(f"\n{'='*70}")
        print(f"Processing: {uidl_file}")
        print('='*70)
        
        with open(uidl_file, 'r', encoding='utf-8') as f:
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
        
        # Write generated files to output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in generated_files.items():
            output_path = output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Generated: {output_path}")
        
        print(f"✓ Successfully processed {uidl_file.name}")
        return True
    
    # Determine input path
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
        # If relative path, make it relative to test directory
        if not input_path.is_absolute():
            input_path = Path(__file__).parent / input_path
    else:
        input_path = Path(__file__).parent / "simple_test.uidl"
    
    # Check if input exists
    if not input_path.exists():
        print(f"Error: Path does not exist: {input_path}")
        sys.exit(1)
    
    output_dir = Path(__file__).parent
    
    # Process single file or directory
    if input_path.is_file():
        # Single file
        if input_path.suffix != '.uidl':
            print(f"Warning: File does not have .uidl extension: {input_path}")
        process_uidl_file(input_path, output_dir)
        print("\n✓ All tests passed!")
    elif input_path.is_dir():
        # Directory - process all .uidl files
        uidl_files = sorted(input_path.glob("*.uidl"))
        if not uidl_files:
            print(f"Error: No .uidl files found in directory: {input_path}")
            sys.exit(1)
        
        print(f"Found {len(uidl_files)} .uidl file(s) in {input_path}")
        success_count = 0
        for uidl_file in uidl_files:
            try:
                if process_uidl_file(uidl_file, output_dir):
                    success_count += 1
            except Exception as e:
                print(f"\n✗ Error processing {uidl_file.name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*70}")
        print(f"Summary: {success_count}/{len(uidl_files)} file(s) processed successfully")
        print('='*70)
        
        if success_count == len(uidl_files):
            print("\n✓ All tests passed!")
        else:
            print(f"\n✗ {len(uidl_files) - success_count} file(s) failed")
            sys.exit(1)
    else:
        print(f"Error: Path is neither a file nor a directory: {input_path}")
        sys.exit(1)
    
except ImportError as e:
    print(f"Error: {e}")
    print("Please install lark: pip install lark")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

