import os
import luigi
from luigi.contrib.external_program import ExternalProgramTask
from luigi.contrib.docker_runner import DockerTask

from wespipeline import utils
from wespipeline.processalign import AlignProcessing
from wespipeline.processalign import ReferenceGenome

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
            os.path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_platypus.vcf'))

    def program_args(self):
        return ['platypus', 'callVariants', 
            '--bamFiles='+self.input()['process']['bamNoDup']['bam'].path, 
            '--refFile='+self.input()['reference']['fa'].path, 
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
            os.path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_freebayes.vcf'))

    def program_args(self):
        return ['freebayes', 
            '-f', self.input()['reference']['fa'].path,
            '--bam', self.input()['process']['bamNoDup']['bam'].path,
            '--vcf', self.output().path
        ]

class VarscanCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using Varscan..

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
            os.path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_varscan.vcf'))

    def program_args(self):
        ref = self.input()['reference']['fa'].path
        bam = self.input()['process']['bamNoDup'].path

        return ['sh', 
                '-c', 
                f"samtools mpileup -f {ref} {bam} | varscan pileup2cns --output-vcf > {self.output().path}"
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
            os.path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_gatk.vcf'))

    def program_args(self):
        return [
            'gatk', '-T', 'HaplotypeCaller',
            '-R', self.input()['reference']['fa'].path,
            '-I', self.input()['process']['bamNoDup'].path,
            '-o', self.output().path
        ]

class DockerGatkCallVariants(DockerTask):
    """Task used for identifying varinats in the bam file provided using DeepVariant.

    Parameters:
        model_type (str): A string defining the model to use for the variant calling. Valid options are [WGS,WES,PACBIO].

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """

    model_type = luigi.Parameter(default='WES', description='A string defining the model to use for the variant calling. Valid options are [WGS,WES,PACBIO]')
    BIN_VERSION = '0.8.0'

    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    @property
    def image(self):
        return f'broadinstitute/gatk'

    @property
    def binds(self):
        return [f"{os.path.abspath(utils.GlobalParams().base_dir)}:/output",
                f"{os.path.dirname(os.path.abspath(self.input()['reference']['fa'].path))}:/input/ref",
                f"{os.path.dirname(os.path.abspath(self.input()['process']['bamNoDup'].path))}:/input/bam",
                ]

    @property
    def mount_tmp(self):
        return False

    @property
    def command(self): 
        command = f'gatk HaplotypeCaller ' + \
            f'-R /input/ref/{os.path.basename(self.input()["reference"]["fa"].path)} ' + \
            f'-I /input/bam/{os.path.basename(self.input()["process"]["bamNoDup"].path)} ' + \
            f'-O /output/{os.path.basename(self.output().path)} ' 

        print(command)
        return command

    def output(self):
        return luigi.LocalTarget(
            os.path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'_gatk.vcf'))


class DeepvariantDockerTask(DockerTask):
    """Task used for identifying varinats in the bam file provided using DeepVariant.

    Parameters:
        model_type (str): A string defining the model to use for the variant calling. Valid options are [WGS,WES,PACBIO].

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """

    model_type = luigi.Parameter(default='WES', description='A string defining the model to use for the variant calling. Valid options are [WGS,WES,PACBIO]')
    create_gvcf = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING, description='Boolean indicating wether to create a gVCF file with both variants, and non variant aligned information.')
    BIN_VERSION = '0.8.0'

    def requires(self):
        return {
            'reference' : ReferenceGenome(),
            'process' : AlignProcessing()
        }

    @property
    def image(self):
        return f'gcr.io/deepvariant-docker/deepvariant:{self.BIN_VERSION}'

    @property
    def binds(self):
        return [f"{os.path.abspath(utils.GlobalParams().base_dir)}:/output",
                f"{os.path.dirname(os.path.abspath(self.input()['reference']['fa'].path))}:/input/ref",
                f"{os.path.dirname(os.path.abspath(self.input()['process']['bamNoDup'].path))}:/input/bam",
                ]

    @property
    def mount_tmp(self):
        return False

    @property
    def command(self):
        command = '/opt/deepvariant/bin/run_deepvariant ' + \
            f'--model_type={self.model_type} ' + \
            f'--ref=/input/ref/{os.path.basename(self.input()["reference"]["fa"].path)} ' + \
            f'--reads=/input/bam/{os.path.basename(self.input()["process"]["bamNoDup"].path)} ' + \
            f'--output_vcf=/output/deepvariant.vcf.gz ' + \
            (f'--output_gvcf=/output/deepvariant.g.vcf.gz ' if self.create_gvcf == True else '') + \
            f'--num_shards={VariantCalling().cpus}'

        print(command)
        return command

    def output(self):
        outputs = dict()

        outputs.update({'vcf': luigi.LocalTarget(os.path.join(utils.GlobalParams().base_dir, 'deepvariant.vcf.gz'))})
        
        if self.create_gvcf == True:
            outputs.update({'gvcf': luigi.LocalTarget(os.path.join(utils.GlobalParams().base_dir, 'deepvariant.gvcf.gz'))})

        return outputs

class DeepvariantCallVariants(ExternalProgramTask):
    """Task used for identifying varinats in the bam file provided using DeepVariant.

    Parameters:
        model_type (str): A string defining the model to use for the variant calling. Valid options are [WGS,WES,PACBIO].

    Dependencies:
        ReferenceGenome
        AlignProcessing

    Output:
        A `luigi.LocalTarget` instance for the index vcf file.

    """

    def requires(self):
        return DeepvariantDockerTask()

    def output(self):
        return luigi.LocalTarget(os.path.join(utils.GlobalParams().base_dir,'deepvariant.vcf'))

    def program_args(self):
        return ['gunzip',self.input()["vcf"].path]


class VariantCalling(utils.MetaOutputHandler, luigi.Task):
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
        use_deepvariant (bool) : A non-case sensitive boolean indicating wether to use DeepVariant for variant callign.
        vcf_local_files (string) : A comma delimited list of vfc files to be used instead of using the variant calling tools.
        cpus (int) : Number of cpus that are available for each of the methods selected.

    Output:
        A dict mapping keys to `luigi.LocalTarget` instances for each of the 
        processed files. 
        The following keys are available:
    
        'platypus' : Local file with the variant calls obtained using Platypus.
        'freebayes' : Local file with the variant calls obtained using Freevayes.
        'Varscan' : Local sorted file with variant calls obtained using Varscan.
        'gatk' : Local file with the variant calls obtained using GATK.
        'deepvariant' : Local file with the variant calls obtained using DeepVariant.

    """

    use_platypus = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING, description="A boolean indicating wether to create a vcf file using Platypus")
    use_freebayes = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING,description="A boolean indicating wether to create a vcf file using Freebayes")
    use_varscan = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING,  description="A boolean indicating wether to create a vcf file using Varscan")
    use_gatk = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING, description="A boolean indicating wether to create a vcf file using GATK")
    use_deepvariant = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING, description="A boolean indicating wether to create a vcf file using DeepVariant")
    cpus = luigi.IntParameter(default=1, description="Number of cpus that are available for each of the methods selected.")
    vcf_local_files = luigi.Parameter(default='', description="Comma separated list for the local files to be used instead of processing the alignments.")

    def requires(self):
        dependencies = dict()
        
        if '.vcf' in self.vcf_local_files :
            for file in self.vcf_local_files.split(','):
                dependencies.update({file.strip(),utils.LocalFile(file=file.stip())})
        else:
            if self.use_platypus == True:
                dependencies.update({'platypus': PlatypusCallVariants()})

            if self.use_freebayes == True:
                dependencies.update({'freebayes': FreebayesCallVariants()})

            if self.use_varscan == True:
                dependencies.update({'varscan': VarscanCallVariants()})

            if self.use_gatk == True:
                dependencies.update({'gatk': DockerGatkCallVariants()})

            if self.use_deepvariant == True:
                dependencies.update({'deepvariant': DeepvariantCallVariants()})

        return dependencies

    def run(self):
        # yield PostDependency()
        pass

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
