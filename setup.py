from setuptools import setup, find_packages

setup(
    name="wearalyze",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    version="0.1.0",
)
