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
These extra dependencies are *not compulsary for all executions of the pipeline*, but depend on the
parameters and tasks selected.

Each of the dependencies correspond to a specific need in one or more of the steps, and thus 
are organized in that manner bellow.

* Secuence retrieval : Sra Toolkit, Fastqc

* Reference genome retrieval : No needed dependency

* Secuence alignment : Bwa

* Alignment processing : Bwa Samtools, 

* Variant calling : Freebayes, Varscan, Gatk, Deepvariant

* Variant calling evaluation : Vcf tools

Installing through Anaconda distributions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even though most of the programs listed can be installed through various different ways, I 
encourage the use of the `Anaconda Distribution <https://www.anaconda.com/distribution/>`_, one of the biggest platforms for 
installing the tools from well trusted sources. Optionally, `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ can be used too
for a lighter version of the package manager.

Installing miniconda is a simple task. Following an example installation for a x64 linux machine:

.. code-block:: bash

  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda. 
  bash ~/miniconda.sh -b -p $HOME/miniconda && rm ~/miniconda.sh
  export PATH="$HOME/miniconda/bin:$PATH"

Beware that, in order for the utilities and installed packages to be accessible the environment
must be activated:

.. code-block:: bash
  
  source $HOME/miniconda/bin/activate

The package archive is distributed through different channels, two of which are needed for the
installation of these packages. Easier than specifying the channel for each command is adding the channels:

.. code-block:: bash

  conda config --add channels bioconda 
  conda config --add channels conda-forge 

Installing from the repositories is a simple task doable through one-liner commands. Following
is an elaborated list of the installation commands for all of the external depenedencies listed
above, and a command for instaling them together:

Installing Samtools

.. code-block:: bash

  conda install -y samtools

Installing Bwa

.. code-block:: bash

  conda install -y bwa

Installing Picard

.. code-block:: bash

  conda install -y picard

Installing Platypus

.. code-block:: bash

  conda install -y platypus-variant

Installing Varscan

.. code-block:: bash

  conda install -y varscan

Installing Freebayes

.. code-block:: bash

  conda install -y freebayes

Installing VCFtools

.. code-block:: bash

  conda install -y vcftools

Installing Fastqc

.. code-block:: bash

  conda install -y fastqc

Installing Sra Toolkit

.. code-block:: bash

  conda install -y sra-tools

Installing all dependencies with a single command:

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
       conda install -y vcftools && \
       conda install -y gatk && \
       conda install -y vt

   rm ~/miniconda.sh
