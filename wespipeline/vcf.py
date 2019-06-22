import luigi
from luigi.contrib.external_program import ExternalProgramTask
from os import path
from wespipeline import utils

from wespipeline.reference import ReferenceGenome
from wespipeline.processalign import AlignProcessing

class PlatypusCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using Platypus.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the vcf produced.

    Parameters:
        none

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """
    
    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    def output(self):
        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_platypus.vcf'))

    def program_args(self):
        return ['platypus', 'callVariants', 
            '--bamFiles='+self.input()['process']['bamNoDup']['bam'].path, 
            '--refFile='+self.input()['reference']['fa']['fa'].path, 
            '--output='+self.output().path,
        ]

class FreebayesCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using Freebayes.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the vcf produced.

    Parameters:
        none

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """
    
    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    def output(self):
        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_freebayes.vcf'))

    def program_args(self):
        return ['freebayes', 
            '-f', self.input()['reference']['fa']['fa'].path,
            '--bam', self.input()['process']['bamNoDup']['bam'].path,
            '--vcf', self.output().path
        ]

class SamtoolsCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using Samtools.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the vcf produced.

    Parameters:
        none

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """
    
    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    def output(self):
        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_samtools.vcf'))

    def program_args(self):
        return [
            self.input()['reference']['fa']['fa'].path,
            self.input()['process']['bamNoDup']['bam'].path,
            self.output().path
        ]

class GatkCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using GatkCallVariants.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the vcf produced.

    Parameters:
        none

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """
    
    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    def output(self):
        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_gatk.vcf'))

    def program_args(self):
        return [
            self.input()['reference']['fa']['fa'].path,
            self.input()['process']['bamNoDup']['bam'].path,
            self.output().path
        ]

class DeepcallingCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using DeepCalling.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the vcf produced.

    Parameters:
        none

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """

    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    def output(self):
        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_deepcalling.vcf'))

    def program_args(self):
        return [
            self.input()['reference']['fa']['fa'].path,
            self.input()['process']['bamNoDup']['bam'].path,
            self.output().path
        ]

class VariantCalling(utils.MetaOutputHandler, luigi.WrapperTask):
    """Higher level task for the alignment of fastq files.
    
    It is given preference to local files over processing the alignment
    in order to reduce computational overhead. 

    If the bam and bai local files are set, they will be used instead of
    the 

    Alignment is done with the Bwa mem utility.

    Parameters:
        use_platypus (bool) : A non-case sensitive boolean indicating wether to use Platypus for variant callign.
        use_freebayes (bool) : A non-case sensitive boolean indicating wether to use Freebayesfor variant callign.
        use_samtools (bool) : A non-case sensitive boolean indicating wether to use Samtools for variant callign.
        use_gatk (bool) : A non-case sensitive boolean indicating wether to use Gatk for variant callign.
        use_deepcalling (bool) : A non-case sensitive boolean indicating wether to use DeepCalling for variant callign.
        vcf_local_files (string) : A comma delimited list of vfc files to be used instead of using the variant calling tools.

    Output:
        A dict mapping keys to `luigi.LocalTarget` instances for each of the 
        processed files. 
        The following keys are available:
    
        'platypus' : Local file with the variant calls obtained using Platypus.
        'freebayes' : Local file with the variant calls obtained using Freevayes.
        'samtools' : Local sorted file with variant calls obtained using Samtools.
        'gatk' : Local file with the variant calls obtained using GATK.
        'deepcalling' : Local file with the variant calls obtained using DeepCalling.

    """

    use_platypus = luigi.Parameter(default="False", description="A boolean [True, False] indicating wether to create a vcf file using Platypus")
    use_freebayes = luigi.Parameter(default="False",description="A boolean [True, False] indicating wether to create a vcf file using Freebayes")
    use_samtools = luigi.Parameter(default="False",  description="A boolean [True, False] indicating wether to create a vcf file using Samtools")
    use_gatk = luigi.Parameter(default="False", description="A boolean [True, False] indicating wether to create a vcf file using GATK")
    use_deepcalling = luigi.Parameter(default="False", description="A boolean [True, False] indicating wether to create a vcf file using DeepCalling")
    vcf_local_files = luigi.Parameter(default='', description="Comma separated list for the local files to be used instead of processing the alignments.")

    def requires(self):
        dependencies = dict()
        
        if '.vcf' in self.vcf_local_files :
            for file in self.vcf_local_files.split(','):
                dependencies.update({file.strip()})
        else:
            if self.use_platypus == 'true':
                dependencies.update({'platypus': PlatypusCallVariants()})

            if self.use_freebayes == 'true':
                dependencies.update({'freebayes': FreebayesCallVariants()})

            if self.use_samtools == 'true':
                dependencies.update({'samtools': SamtoolsCallVariants()})

            if self.use_gatk == 'true':
                dependencies.update({'gatk': GatkCallVariants()})

            if self.use_deepcalling == 'true':
                dependencies.update({'deepcalling': DeepcallingCallVariants()})

        return dependencies


if __name__ == '__main__':
    luigi.run(['VariantCalling', 
            '--VariantCalling-use-platypus', 'true',
            '--VariantCalling-use-freebayes', 'true',
            '--VariantCalling-use-samtools', 'false',
            '--VariantCalling-use-gatk', 'false',
            '--VariantCalling-use-deepcalling', 'false',
            '--AlignProcessing-cpus', '6',
            '--FastqAlign-cpus', '6', 
            '--FastqAlign-create-report', 'True', 
            '--GetFastq-fastq1-url', '',
            '--GetFastq-fastq2-url', '',
            '--GetFastq-from-ebi', 'False',
            '--GetFastq-paired-end', 'True',
            '--ReferenceGenome-ref-url', 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit',
            '--ReferenceGenome-from2bit', 'True',
            '--utils.GlobalParams-base-dir', './experiment',
            '--utils.GlobalParams-log-dir', path.abspath(path.curdir),
            '--utils.GlobalParams-exp-name', 'hg19'])
