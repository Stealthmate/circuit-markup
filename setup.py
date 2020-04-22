import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="circuit-markup-stealthmate", # Replace with your own username
    version="0.0.1",
    author="Valeri Haralanov",
    author_email="stealthmate.dev@gmail.com",
    description="A package for drawing electronic circuits on SVGs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stealthmate/circuit-markup",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
