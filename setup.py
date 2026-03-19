from setuptools import setup, find_packages

setup(
    name="reqgraph",
    version="1.0.0",
    description="Rastreabilidade automatica de requisitos via Call Graph (AST).",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "networkx",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "reqgraph=reqgraph.cli:main",
        ],
    },
)
