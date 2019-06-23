import itertools
import luigi
from luigi.contrib.external_program import ExternalProgramTask
from os import path
from wespipeline import utils 

from wespipeline.vcf import VariantCalling

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
            ''.join([filename(self.vcf1), '_vs_', filename(self.vcf2)])))

    def program_args(self):
        return ['vcftools',
            '--vcf',
            self.vcf1,
            '--diff',
            self.vcf2,
            '--not-chr',
            '--diff-site',
            '--out',
            self.output().path
        ]

class VcftoolsAnalysis(ExternalProgramTask):
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
        return luigi.LocalTarget(self.vcf.replace('.vcf', '.vcf_info'))

    def program_args(self):
        return ['vcftools',
            '--vcf',
            self.vcf,
            '--out',
            self.output().path
        ]

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

    def requires(self):
        return VariantCalling()

    def outputs(self):
        output = [vcf.path.replace('.vcf','vcf_info') for vcf in self.input().values()]

        return output

    def run(self):
        yield((VcftoolsAnalysis(vcf=vcf.path) for vcf in self.input().values()))
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
