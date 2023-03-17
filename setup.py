from setuptools import find_packages, setup

setup(
    name="var_annot",
    version="1.0.0",
    description="Prototype a variant annotation tool",
    author="Keith Dunaway",
    packages=find_packages(where="var_annot"),
    install_requires=[
        "pysam",
        "pytest",
        "requests",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
