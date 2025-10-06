"""
Setup script for SpokyAI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [line.strip() for line in requirements_file.read_text().splitlines() 
                   if line.strip() and not line.startswith('#')]

setup(
    name="spokyai",
    version="0.1.0",
    author="Opinion-Mining-System Team",
    author_email="",
    description="Intelligent AI agent for user action automation and voice control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AccentureMacr0s/Opinion-Mining-System",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'spokyai=core.agent:main',
        ],
    },
)
