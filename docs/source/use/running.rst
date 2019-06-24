Running the pipeline
====================

Executing tasks
^^^^^^^^^^^^^^^

The execution of the tasks follows the same as other Luigi tasks,
using each of the provided modules to execute one of the defined steps 
of the analysis.

Secuence retrieval
++++++++++++++++++

Retrieving the secuencing is a step that takes into account wether the experiment
is paired end, or the sources are gz compressed.

Several options can be configured for selecting the source for the exome sequences:

* The origin of the files
* Wether the files are compressed
* Wether the experiment is paired end

Different sources can be set, in which case the one used for retrieving will be
the following:

1. Files accessible localy
2. Files specified by the NCBI accession number.
3. External sources set by their url

.. warning:: This task will fail along with the upstream tasks if the quality report
   is selected but `Fastqc <https://www.bioinformatics.babraham.ac.uk/projects/fastqc/>`_ is not 
   installed.

In the case of using the NCBI accession number, the ``compressed`` is ignored as
it is already handled with the ``fastq-dump`` tool from the `Sra toolkit`. 

.. warning:: This task will fail along with the upstream tasks if the accession number
   is used but `Sra toolkit <https://www.ncbi.nlm.nih.gov/sra/docs/toolkitsoft/>`_ is not 
   installed.

The execution of this step with all the posible parameters is the following:

.. code-block:: bash

   luigi --module wespipeline.fastq GetFastq \
      --GetFastq-paired-end true \
      --GetFastq-compressed true \
      --GetFastq-fastq1-local-file ./experiment_1.fastq.gz \
      --GetFastq-fastq2-local-file ./experiment_2.fastq.gz \
      --GetFastq-accession_number SRRXXXXXX
      --GetFastq-fastq1-url ftp.archive.x/exp/exome_1.fastq.gz \
      --GetFastq-fastq2-url ftp.archive.x/exp/exome_2.fastq.gz

.. note:: Eventhough parameters for the selected task ``GetFastq`` can be set directly,
   it is encourage to prepend the task name in order to keep the call consistent and
   distinguish them from parameters set to other tasks.

.. note:: Note that GloablParams is used for setting common pipeline wide parameters.

This task is used required by the ``Align`` task. If the secuences are available locally,
set the ``fastqx-local-file`` parameter to the correspondent path; for instance, for 
a set of fastq files relative to the current directory that don't require to be uncompressed 
the following command would be used:

.. code-block:: bash

   luigi --module wespipeline.fastq GetFastq \
      --GetFastq-paired-end true \
      --GetFastq-fastq1-local-file ./experiment_1.fastq \
      --GetFastq-fastq2-local-file ./experiment_2.fastq



Reference genome retrieval
++++++++++++++++++++++++++

The reference genome, essential for more steps than the alignment, may be obtained 
in 2bit format (and then converted to fa).

Secuence alignment
++++++++++++++++++

Aligning the secuencing against the reference genome is a process that produces a not
sorted, nor indexed, sam file.

Alignment processing
++++++++++++++++++++

Processing the alignment includes sorting, indexing and removing duplicates from the 
original alignment. In the end, it produces a bam and bai file.

Variant calling
+++++++++++++++

Variants can be obatined with different tools; each of which depends in the reference 
genome retrieval (``wespipeline.reference.ReferenceGenome``) and the align processing step
(``wespipeline.processalign.AlignProcessing``).

The desired tools to be used are specified as boolean parameters, from a total of five
eligible:

- Platypus
- Freebayes
- DeepVariant
- Gatk
- Samtools

.. warning:: DeepVariant requires `Docker <https://www.docker.com/>`_ to be installed. Additionally,
   it needs the Python Docker package for Luigi to interact with it; this last one is a dependency
   specified in the package, so it will be automatically installed if *wespipeline* is installed with
   a package manager.

   An example for using DeepVariant on reference genome, and bam files located in the current directory
   would be the following:

.. code:: bash
   
   python3 -m luigi --module wespipeline.vcf VariantCalling 
   --VariantCalling-use-deepvariant True  \
   --VariantCalling-cpus 2  \
   --ReferenceGenome-reference-local-file hg19.fa  \
   --AlignProcessing-no-dup-bam-local-file hg19_nodup.bam  \
   --AlignProcessing-no-dup-bai-local-file hg19_nodup.bam.bai  \
   --GlobalParams-exp-name hg19  \
   --GlobalParams-base-dir .  \
   --GlobalParams-log-dir . \

Variant calling evaluation
++++++++++++++++++++++++++

Variant calling comparation and estatistical summaries for the variants identifyed.

Global vs task specific parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Luigi provides a convenient way to expose a task' parameters both for Python code 
task instancetiating, and command line usage. The modular approach taken for the 
design of the pipeline 

Whole analysis example
^^^^^^^^^^^^^^^^^^^^^^

The following command allows to execute the pipeline for...

.. code:: bash
   
   nohup python3.6 -m luigi --module wespipeline.vcf_analysis VariantCallingAnalysis \ 
   --workers 3 \ 
   --VariantCalling-use-platypus true \ 
   --VariantCalling-use-freebayes true \ 
   --VariantCalling-use-samtools false \ 
   --VariantCalling-use-gatk false \ 
   --VariantCalling-use-deepcalling false \ 
   --AlignProcessing-cpus 6 \ 
   --FastqAlign-cpus 6 \ 
   --FastqAlign-create-report True \ 
   --GetFastq-gz-compressed True \ 
   --GetFastq-fastq1-url 
   ftp://ftp-trace.ncbi.nih.gov/giab/ftp/data/NA12878/Garvan_NA12878_HG001
   _HiSeq_Exome/NIST7035_TAAGGCGA_L001_R1_001.fastq.gz \ 
   --GetFastq-fastq2-url 
   ftp://ftp-trace.ncbi.nih.gov/giab/ftp/data/NA12878/Garvan_NA12878_HG001_HiSeq_Exome/NIST7035_TAAGGCGA_L001_R2_001.fastq.gz \ 
   --GetFastq-from-ebi False \ 
   --GetFastq-paired-end True \ 
   --ReferenceGenome-ref-url 
   ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit \ --ReferenceGenome-from2bit True \ 
   --GlobalParams-base-dir ./tfm_experiment \ 
   --GlobalParams-log-dir .logs \ 
   --GlobalParams-exp-name hg19 & 
