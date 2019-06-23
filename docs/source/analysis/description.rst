The analysis pipeline
=====================

Although the basic pipeline for analyzing whole exome sequencing, as propuested in NCBI, consists of 
three basic phases (secuencing retrieval, aliengment, and variant calling), more steps are distinguished
to make the pipeline more flexible:

* Secuence retrieval

* Reference genome retrieval

* Secuence alignment

* Alignment processing

* Variant calling

* Variant calling evaluation

Secuence retrieval
^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.githubusercontent.com/janchorizo/wespipeline/master/docs/fastq.png
   :alt: Steps Logo
   :align: center

Retrieving the secuencing is a step that takes into account wether the experiment
is paired end, or the sources are gz compressed.

Reference genome retrieval
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.githubusercontent.com/janchorizo/wespipeline/master/docs/reference.png
   :alt: Steps Logo
   :align: center

The reference genome, essential for more steps than the alignment, may be obtained 
in 2bit format (and then converted to fa).

Secuence alignment
^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.githubusercontent.com/janchorizo/wespipeline/master/docs/align.png
   :alt: Steps Logo
   :align: center

Aligning the secuencing against the reference genome is a process that produces a not
sorted, nor indexed, sam file.

Alignment processing
^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.githubusercontent.com/janchorizo/wespipeline/master/docs/process.png
   :alt: Steps Logo
   :align: center

Processing the alignment includes sorting, indexing and removing duplicates from the 
original alignment. In the end, it produces a bam and bai file.

Variant calling
^^^^^^^^^^^^^^^

.. figure:: https://raw.githubusercontent.com/janchorizo/wespipeline/master/docs/vcf.png
   :alt: Steps Logo
   :align: center

The process of identifying variants within the secuenced exome.

Variant calling evaluation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://raw.githubusercontent.com/janchorizo/wespipeline/master/docs/vcftools.png
   :alt: Steps Logo
   :align: center

Variant calling comparation and estatistical summaries for the variants identifyed.
