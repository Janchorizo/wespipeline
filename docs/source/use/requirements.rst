Requirements
============

Python dependencies
^^^^^^^^^^^^^^^^^^^

Wespipeline depends on an existing installation of the library `Luigi <https://pypi.org/project/luigi/>`_.
If this package was installed following the recomended steps, this dependency should be fulfilled.

External dependencies
^^^^^^^^^^^^^^^^^^^^^

Whole exome sequencing variant calling analysis needs for external programs for
doing both the processing, and the analysis and summaries. Following is a list of
the different dependencies.

Optionally, some type of database is needed for making use of the persistent storage 
of executions. In the configuration proposed, is used.

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

Optional dependencies
^^^^^^^^^^^^^^^^^^^^^

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