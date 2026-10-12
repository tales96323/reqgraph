from setuptools import setup

setup(
    name="reqgraph",
    version="1.0.0",
    description="Rastreabilidade automatica de requisitos via Call Graph (AST).",
    # O diretorio deste setup.py e o proprio pacote 'reqgraph'.
    package_dir={"reqgraph": "."},
    packages=["reqgraph"],
    python_requires=">=3.8",
    install_requires=[
        "networkx>=3.0.0",
        "matplotlib>=3.5.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "reqgraph=reqgraph.cli:main",
        ],
    },
)
