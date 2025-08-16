from setuptools import setup, find_packages
import os
import re

# read  README file for description 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# read version since __init__.py
def get_version():
    with open(os.path.join("osram_cli", "__init__.py"), "r") as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Impossible to find string  version.")

setup(
    name="osram-cli",
    version=get_version(),
    author="Mike Amega",
    author_email="mikeamega910@gmail.com",
    description="Osram CLI - Assistant IA for developer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Volgat/osram-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "osram=osram_cli.__main__:main",  # call  function main
        ],
    },
)