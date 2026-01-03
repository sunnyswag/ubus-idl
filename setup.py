"""Setup script for ubus-idl"""

from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
def get_version():
    try:
        init_file = this_directory / "ubus_idl" / "__init__.py"
        with open(init_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.1.0"

setup(
    name="ubus-idl",
    version=get_version(),
    description="Ubus Interface Definition Language compiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="https://github.com/yourusername/ubus-idl",  # Update with your repository URL
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ubus-idl/issues",
        "Source": "https://github.com/yourusername/ubus-idl",
        "Documentation": "https://github.com/yourusername/ubus-idl#readme",
    },
    packages=find_packages(exclude=["test", "test.*", "ubus", "ubus.*"]),
    install_requires=[
        "lark>=1.1.0",
    ],
    entry_points={
        "console_scripts": [
            "ubus-idl=ubus_idl.main:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="ubus idl code-generator c compiler",
    include_package_data=True,
    zip_safe=False,
)

