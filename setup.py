from setuptools import setup, find_packages
import os

# Read dependencies from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Read long description from README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="four-sided-triangle",
    version="0.1.0",
    description="A RAG pipeline with domain expert LLM for sprint running",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Four Sided Triangle Team",
    author_email="team@four-sided-triangle.ai",
    url="https://github.com/yourusername/four-sided-triangle",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=required,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        'console_scripts': [
            'run-api=run_api:main',
            'run-modeler=backend.run_modeler_api:main',
        ],
    },
    include_package_data=True,
)
