import luigi
from luigi.contrib.external_program import ExternalProgramTask
from os import path
from wespipeline import utils

from wespipeline.reference import ReferenceGenome
from wespipeline.align import FastqAlign

class SortSam(ExternalProgramTask):
    """Task used for sorting the alignment sam file.

    It requires the output of the ``wespipeline.reference.FastqAlign`` step.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the Bam file produced.

    Parameters:
        none

    Output:
        A `luigi.LocalTarget` instance for the sorted Sam Bam file.

    """

    def requires(self):
        return FastqAlign()

    def output(self):
        return luigi.LocalTarget(
            path.join(utils.GlobalParams().base_dir,
            utils.GlobalParams().exp_name+'.bam')
            )

    def program_args(self):
        return ['samtools', 'sort', '-@', AlignProcessing().cpus, 
            self.input()['sam'].path, '-o', self.output().path
        ]

class IndexBam(ExternalProgramTask):
    """Task used for indexing the Bam file.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the Bai file produced.

    Parameters:
        none

    Output:
        A `luigi.LocalTarget` instance for the index Bai file.

    """

    def requires(self):
        return SortSam()

    def output(self):
        return luigi.LocalTarget(self.input().path+'.bai')

    def program_args(self):
        return ['samtools', 'index', '-@', AlignProcessing().cpus, self.input().path]

class PicardMarkDuplicates(ExternalProgramTask):
    """Task used for removing duplicates from the Bam file.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the Bam file produced.

    Parameters:
        none

    Output:
        A `luigi.LocalTarget` instance for the Bam file without the duplicates.

    """

    def requires(self):
        return {'index' : IndexBam(),
            'bam' : SortSam()
        }

    def output(self):
        return {
            'bam' : luigi.LocalTarget( \
                path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+'_nodup.bam')),
            'metrics' : luigi.LocalTarget( \
                path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+'_MD.matrix'))
        }

    def program_args(self):
        return ['picard', 'MarkDuplicates', 
            'I='+self.input()['bam'].path, 
            'O='+self.output()['bam'].path, 
            'METRICS_FILE='+self.output()['metrics'].path,
            'REMOVE_DUPLICATES=true'
        ]

class IndexNoDup(ExternalProgramTask):
    """Task used for indexing the Bam file without duplicates.

    The ``wespipeline.utils.GlobalParams.exp_name`` will be used for giving name
    to the Bai file produced.

    Parameters:
        none

    Output:
        A `luigi.LocalTarget` instance for the index Bai file.

    """

    def requires(self):
        return PicardMarkDuplicates()

    def output(self):
        return luigi.LocalTarget(self.input()['bam'].path+'.bai')

    def program_args(self):
        return ['samtools', 'index', '-@', AlignProcessing().cpus, self.input()['bam'].path]

class AlignProcessing(utils.MetaOutputHandler, luigi.Task):
    """Higher level task for the alignment of fastq files.
    
    It is given preference to local files over processing the alignment
    in order to reduce computational overhead. 

    If the bam and bai local files are set, they will be used instead of
    the 

    Alignment is done with the Bwa mem utility.

    Parameters:
        bam_local_file (str) : String indicating the location of a local
            bam file with the sorted alignment. If set, this file will not be created.
        bai_local_file (str) : String indicating the location of a local
            bai file with the index for the alignment. If set, this file will not be created.
        no_dup_bam_local_file (str) : String indicating the location of a local
            sam file without the duplicates. If set, this file will not be created.
        no_dup_bai_local_file (str) : String indicating the location of a local
            file with the index for the bam file without duplicates. If set, this 
            file will not be created.
        cpus (int): Integer indicating the number of cpus that can be used for 
            the alignment.

    Output:
        A dict mapping keys to `luigi.LocalTarget` instances for each of the 
        processed files. 
        The following keys are available:
    
        'bam' : Local file with the sorted alignment.
        'bai' : Local file with the alignment index.
        'bamNoDup' : Local sorted file with duplicates removed.
        'indexNoDup' : Local file with the index for sorted alignment without duplicates.

    """

    cpus = luigi.IntParameter(default=1, description="Number of cpus to be used by each task thread.")
    bam_local_file = luigi.Parameter(default='', description='Optional path for the file. If set, wil be skipped.')
    bai_local_file = luigi.Parameter(default='', description='Optional path for the file. If set, wil be skipped.')
    no_dup_bam_local_file = luigi.Parameter(default='', description='Optional path for the file. If set, wil be skipped.')
    no_dup_bai_local_file = luigi.Parameter(default='', description='Optional path for the file. If set, wil be skipped.')

    def requires(self):
        dependencies = dict()

        if self.no_dup_bam_local_file != '' and self.no_dup_bai_local_file != '':
            dependencies.update({'bam': utils.LocalFile(file=self.no_dup_bam_local_file)})
            dependencies.update({'bai': utils.LocalFile(file=self.no_dup_bai_local_file)})
            dependencies.update({'bamNoDup': {'bam' : utils.LocalFile(file=self.no_dup_bam_local_file)}})
            dependencies.update({'baiNoDup': utils.LocalFile(file=self.no_dup_bai_local_file)})
        else:
            dependencies.update({'bamNoDup': PicardMarkDuplicates()})
            dependencies.update({'baiNoDup': IndexNoDup()})

        if self.bam_local_file != '' and self.bai_local_file != '':
            dependencies.update({'bam': utils.LocalFile(file=self.bam_local_file)})
            dependencies.update({'bai': utils.LocalFile(file=self.bai_local_file)})
        else:
            dependencies.update({'bam': SortSam()})
            dependencies.update({'bai': IndexBam()})

        return dependencies

    def run(self):
        # yield PostDependency()
        pass

if __name__ == '__main__':
    luigi.run(['AlignProcessing', 
            '--AlignProcessing-cpus', '6',
            '--FastqAlign-cpus', '6', 
            '--FastqAlign-create-report', 'True', 
            '--GetFastq-fastq1-url', '',
            '--GetFastq-fastq2-url', '',
            '--GetFastq-from-ebi', 'False',
            '--GetFastq-paired-end', 'True',
            '--ReferenceGenome-ref-url', 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit',
            '--ReferenceGenome-from2bit', 'True',
            '--utils.GlobalParams-base-dir', path.abspath(path.curdir),
            '--utils.GlobalParams-log-dir', path.abspath(path.curdir),
            '--utils.GlobalParams-exp-name', 'hg19'])
