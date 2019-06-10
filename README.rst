wespipeline
===========
Source code repository for the Python package wespipeline. An implementation of a whole exome analysis pipeline using Luigi for workflow management.

The usage of data pipelines for automating and streamline bioinformatic processes helps reduce the overhead of having to 
learn and operate a wide range of tools, thus simplifying the analysis. Additionally, data pipelines provide with utilities
for managing resources, ginving a homogeneous access to sources, and ensuring a robust execution model that resolves
dependencies automatically.

The former is the implementation of a data pipeline for variant calling analysis in whole exome sequencing experiments. The
package provides tasks for been executed with Luigi, a library for managing pipeline workflows.

Run the whole analysis pipeline or just separate steps.

_Documentation for the latest version is being hosted by `readthedocs <https://wespipeline.readthedocs.io/en/latest/>`_.

Getting Started
---------------

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

Prerequisites
+++++++++++++

Even though pip packages dependencies are resolved upon installation, third party tools are not.
There are two groups of dependencies attending to their : functional and documenting.

Functional dependencies are packages needed for the essential steps such as the alignment or 
marking duplicates. These are the following :

* Bwa
* Samtools
* Gatk
* Vcftools

Five different options are given for doing the variant calling. Depending on the desired tools,
the correspondent packages must be installed.

* Bwa
* Freebayes
* Gatk
* Deepvariant

A set of tools can be used for generating reports for the different steps in the pipeline. They are
not required by default, but must be installed if the correspondent option is selected.

* Fastqcheck

**It is encauraged to use the Anaconda distribution** for software installation if possible. Most of
the cited packages are available through the Anaconda distribution, which allows to make the installation
with a simple command.

An example for installing Miniconda and the needed packages is the following :

.. code-block:: bash

   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
   bash ~/miniconda.sh -b -p $HOME/miniconda
   export PATH="$HOME/miniconda/bin:$PATH"
   source $HOME/miniconda/bin/activate && \
       conda config --add channels bioconda && \
       conda config --add channels conda-forge && \
       conda install -y samtools && \
       conda install -y bwa && \
       conda install -y picard && \
       conda install -y platypus-variant && \
       conda install -y varscan && \
       conda install -y freebayes && \
       conda install -y vcftools 

   rm ~/miniconda.sh



Installing
++++++++++

Run ```pip install wespipeline``` to install the latest stable version from PyPI. Documentation for the
latest release is hosted on readthedocs.

To install from source, download the project ```git clone https://github.com/janchorizo/wespipeline.git```
and run ```python3 setup.py install``` in the root directoy.

Usage
+++++

Each of the modules in the package contains tasks for executing a specific setp in the analysis pipline.
Use Luigi's typipcal call format for launching the execution of a task:

```luigi -m wespipeline.reference GetReference --GlobalParams-exp-name hg19 --workers 2 --local-scheduler```

Running the tests
-----------------

Explain how to run the automated tests for this system

Break down into end to end tests
------------------------------------
Explain what these tests test and why

```
Give an example
```

And coding style tests

Explain what these tests test and why

```
Give an example
```

Deployment
----------

Add additional notes about how to deploy this on a live system

Built With
----------

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

Contributing
------------

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

Versioning
----------

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

Authors
-------

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.


License
-------

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

Acknowledgments

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)
* Inspiration
* etc

