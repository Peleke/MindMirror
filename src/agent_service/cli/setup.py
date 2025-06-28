"""
Setup script for agent service CLI.

This creates a console script entry point for easy CLI access.
"""

from setuptools import setup

setup(
    name="agent-service-cli",
    version="1.0.0",
    description="CLI tools for agent service data management",
    py_modules=["agent_service.cli.main"],
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "agent-service=agent_service.cli.main:cli",
        ],
    },
)
