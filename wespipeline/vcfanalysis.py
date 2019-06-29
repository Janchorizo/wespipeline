import itertools
import luigi
from luigi.contrib.external_program import ExternalProgramTask
from luigi.contrib.docker_runner import DockerTask
from os import path
from wespipeline import utils 

from wespipeline.vcf import VariantCalling
from wespipeline.reference import ReferenceGenome

class VcftoolsCompare(ExternalProgramTask):
    """Task used for comparing a pair of vcf files using VcfTools.

    Parameters:
        vcf1 (str): Absolute path to the first file to be compared.
        vcf2 (str): Absolute path to the second file to be compared.

    Dependencies:
        None

    Output:
        A `luigi.LocalTarget` instance for the result of comparing the files.

    """

    vcf1 = luigi.Parameter()
    vcf2 = luigi.Parameter()

    def requires(self):
        return None

    def output(self):
        filename = lambda f: path.split(f)[-1].split('.')[0]

        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            ''.join([filename(self.vcf1), '_vs_', filename(self.vcf2)]) +'.diff.sites_in_files'
            ))

    def program_args(self):
        filename = lambda f: path.split(f)[-1].split('.')[0]
        output_filename = path.join(utils.GlobalParams().base_dir, \
            ''.join([filename(self.vcf1), '_vs_', filename(self.vcf2)]))
        return ['vcftools',
            '--vcf',
            self.vcf1,
            '--diff',
            self.vcf2,
            '--diff-site',
            '--out',
            output_filename
        ]

class VcftoolsDepthAnalysis(ExternalProgramTask):
    """Task used for extracting basic statistics for the variant calls using VcfTools.

    Parameters:
        vcf (str): Absolute path to the file with the variant annotations.

    Dependencies:
        None

    Output:
        A `luigi.LocalTarget` instance for the file with the vcf statistics.

    """

    vcf = luigi.Parameter()

    def requires(self):
        return None

    def output(self):
        return luigi.LocalTarget(self.vcf.replace('.vcf', '_depth_info.txt'))

    def program_args(self):
        return ['sh','-c',f'vcftools --vcf {self.vcf} --depth -c > {self.output().path}']

class VcftoolsFreqAnalysis(ExternalProgramTask):
    """Task used for extracting basic statistics for the variant calls using VcfTools.

    Parameters:
        vcf (str): Absolute path to the file with the variant annotations.

    Dependencies:
        None

    Output:
        A `luigi.LocalTarget` instance for the file with the vcf statistics.

    """

    vcf = luigi.Parameter()

    def requires(self):
        return None

    def output(self):
        return luigi.LocalTarget(self.vcf.replace('.vcf', '_freq_info.txt'))

    def program_args(self):
        return ['sh','-c',f'vcftools --vcf {self.vcf} --freq > {self.output().path}']

class DockerVTnormalizeVCF(DockerTask):


    VERSION = "0.57721--hdf88d34_2"

    vcf = luigi.Parameter()
    output = luigi.Parameter()

    biallelic_block_substitutions = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING)
    biallelic_clumped_variant = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING)
    biallelic_block_substitutions = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING)
    decomposes_multiallelic_variants = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING,
        description='decomposes multiallelic variants into biallelic variants')

    def requires(self):
        return ReferenceGenome()

    def output(self):
        return luigi.LocalTarget(self.output)

    @property
    def image(self):
        return f'quay.io/biocontainers/vt:{self.VERSION}'

    @property
    def binds(self):
        return [f"{os.path.dirname(os.path.abspath(self.input().path))}:/input/ref",
                f"{os.path.dirname(os.path.abspath(self.vcf))}:/input/vcf",
                f"{os.path.dirname(os.path.abspath(self.output))}:/output",
                ]

    @property
    def mount_tmp(self):
        return False

    @property
    def command(self):
        command = 'vt normalize ' + \
            f'/input/vcf/{os.path.basename(self.vcf)} ' + \
            f'-r /input/ref/{os.path.basename(self.input().path)} ' + \
            f'-o /output/{os.path.basename(self.output)} ' 

        return command

class VTnormalizeVCF(ExternalProgramTask):

    vcf = luigi.Parameter()
    out = luigi.Parameter()

    def requires(self):
        return ReferenceGenome()

    def output(self):
        return luigi.LocalTarget(self.out)

    def program_args(self):
        command = ['sh', '-c',
        'vt normalize -r '+self.input()['fa'].path+' -o '+self.out+'_tmp.vcf '+self.vcf+' && picard SortVcf SEQUENCE_DICTIONARY='+self.input()['dict'].path+' O='+self.out+' I='+self.out+'_tmp.vcf && rm '+self.out+'_tmp.vcf']

        print(command)

        return command


class NormalizeVcfFiles(utils.MetaOutputHandler, luigi.Task):
    """docstring for NormalizeVcfFiles"""
    
    def requires(self):
        return VariantCalling()

    def output(self):
        
        output = {vcf[0]:luigi.LocalTarget(vcf[1].path.replace('.vcf','_normalized.vcf')) for vcf in self.input().items()}
        return output

    def run(self):
        yield {entry[0]:VTnormalizeVCF(vcf=entry[1].path, out=self.output()[entry[0]].path) for entry in self.input().items()}
        

class VariantCallingAnalysis(luigi.Task):
    """Higher level task for comparing variant calls.
    
    Comparing variant calls is a delicate task that increments in complexity when
    dealing in diploid sequences (such us the human genome), where different variants
    can appear in the same position in each of the pair chromomes.

    The normalization is done with vt, and the comparison with VcfTools

    Parameters:
        None

    Output:
        None. The resulting files are not provided as task output. Each of the n vcf files is analyzed and comparied by pairs. 
        It is a total of 2n-1 files.

    """

    normalize = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING, 
        description="A boolean indicating wether to normalize vcf files prior to analysis")

    def requires(self):
        return NormalizeVcfFiles() if self.normalize == True else VariantCalling()

    def output(self):
        output = [luigi.LocalTarget(vcf.path.replace('.vcf','vcf_info')) for vcf in self.input().values()]
        return output

    def run(self):
        yield((VcftoolsDepthAnalysis(vcf=vcf.path) for vcf in self.input().values()))
        yield((VcftoolsFreqAnalysis(vcf=vcf.path) for vcf in self.input().values()))
        if len(self.input()) > 1:
            yield((VcftoolsCompare(vcf1=vcf1.path, vcf2=vcf2.path) \
                for vcf1,vcf2 in itertools.combinations(self.input().values(),2)))
    

if __name__ == '__main__':
    luigi.run(['VariantCallingAnalysis', 
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
