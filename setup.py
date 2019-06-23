import os
import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wespipeline-jancho",
    version="1.0.0",
    author="Alejandro Rodríguez Díaz",
    author_email="jancho@usal.es",
    description="An implementation of a whole exome analysis pipeline using the library Luigi for workflow management.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        'Documentation': 'https://wespipeline.readthedocs.io/en/latest/index.html',
        'Source': 'https://github.com/Janchorizo/wespipeline',
        'Tracker': 'https://github.com/Janchorizo/wespipeline/issues',
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'luigi',
        'python-daemon'
    ]
)
