#!/usr/bin/env python3
"""
Setup script for ADAMSNRC Python package.
"""

from setuptools import find_packages, setup


# Read the README file for long description
def read_readme():
    """Read README.md file."""
    with open("README.md", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    with open("requirements.txt", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="adamsnrc",
    version="2.0.13",
    author="Max Oliver",
    author_email="max.oliver@cintrax.com.br",
    description="A robust Python client for the Nuclear Regulatory Commission's ADAMS API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/adamsnrc",
    packages=find_packages(exclude=[
        "*.tests*",
        "*.test*",
        "tests*",
        "test*",
        "venv*",
        ".venv*",
        "env*",
        "ENV*",
        "build*",
        "dist*",
        ".git*",
        "*.egg-info*",
    ]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.8.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "adamsnrc=adamsnrc.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="adams, nrc, nuclear, regulatory, api, client, documents",
    project_urls={
        "Bug Reports": "https://github.com/maxoliverbr/adamsnrc/issues",
        "Source": "https://github.com/maxoliverbr/adamsnrc",
        "Documentation": "https://adamsnrc.readthedocs.io/",
    },
)
