from setuptools import setup, find_packages

setup(
    name="servos",
    version="1.0.0",
    description="Servos – Offline AI Forensic Assistant",
    author="MoMoSapiens",
    author_email="akash@momosapiens.dev",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "psutil>=5.9.0",
        "ollama>=0.1.0",
        "pydantic>=2.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "jinja2>=3.1.0",
        "pyyaml>=6.0.0",
        "watchdog>=3.0.0",
        "sqlalchemy>=2.0.0",
        "reportlab>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "servos=servos.main:cli",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
)
