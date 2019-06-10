Running the pipeline
====================

Executing tasks
^^^^^^^^^^^^^^^

The execution of the tasks follows the same as other Luigi tasks,
using each of the provided modules to execute one of the defined steps 
of the analysis.

Global vs task specific parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Luigi provides a convenient way to expose a task' parameters both for Python code 
task instancetiating, and command line usage. The modular approach taken for the 
design of the pipeline 

Whole analysis example
^^^^^^^^^^^^^^^^^^^^^^

The following command allows to execute the pipeline for...

.. code:: bash
   
   PYTHONPATH=./luigi-wes-pipeline/pipeline/ nohup python3.6 -m luigi \ 
   --module tasks.vcf_analysis VariantCallingAnalysis \ 
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
