Installation
============

Run ```pip install wespipeline``` to install the latest stable version from PyPI. Documentation for the
latest release is hosted on readthedocs.

To install from source, download the project ```git clone https://github.com/janchorizo/wespipeline.git```
and run ```python3 setup.py install``` in the root directoy.

Usage
+++++

Each of the modules in the package contains tasks for executing a specific setp in the analysis pipline.
Use Luigi's typipcal call format for launching the execution of a task:

```luigi -m wespipeline.reference GetReference --GlobalParams-exp-name hg19 --workers 2 --local-scheduler```