import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AbacusPYQ",
    version="1.0.0",
    author="Hidden Odds",
    author_email="david.arturo.silva@gmail.com",
    description="Classifier and count car.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
