"""The setup script."""

from setuptools import find_namespace_packages, setup

setup(
    name="Fluid",
    version="0.0.1",
    author="Vincent Dutordoir",
    description="Reactive Python Framework",
    packages=find_namespace_packages(include=["fluid*"]),
)