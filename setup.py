from setuptools import setup, find_packages

setup(
    name="fund-nav",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    extras_require={
        "dev": ["pytest>=7.0"],
    },
)
