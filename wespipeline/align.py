import luigi
from luigi.contrib.external_program import ExternalProgramTask
from os import path
from wespipeline import utils 

from wespipeline.reference import ReferenceGenome
from wespipeline.fastq import GetFastq

class BwaAlignFastq(ExternalProgramTask):
    """Task used for aligning fastq files against the reference genome.

    It requires the output of both the wespipeline.reference.ReferenceGenome and
    wespipeline.fastq.GetFastq higher level tasks in order to proceed with 
    the alignment.

    If ``wespipeline.utils.GlobalParams.exp_name`` is set, it will be used for giving name
    to the Sam file produced.

    Parameters:
        none

    Output:
        A `luigi.LocalTarget` instance for the aligned sam file.

    """

    def requires(self): 
        return {
            'reference' : ReferenceGenome(),
            'fastq' : GetFastq()
        }

    def output(self):
        get_name = lambda x: os.path.splitext(os.path.basename(os.path.realpath(x)))[0]
        output_filename = get_name(self.input['fastq']['fastq1'].path) + '.sam'

        if utils.GlobalParams().exp_name:
            output_filename = path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+".sam")
        
        return luigi.LocalTarget(output_filename)

    def program_args(self):
        name = 'wespipeline' if not utils.GlobalParams().exp_name else utils.GlobalParams().exp_name

        rg = '@RG\\tID:'+name+'\\tSM:'+name+'\\tPL:illumina'

        args = ['bwa', 'mem', '-M', '-R', rg,
            '-t', FastqAlign().cpus,
            self.input()['reference']['fa'].path,
            self.input()['fastq']['fastq1'].path,
            ]

        if 'fastq_2' in self.input()['fastq']:
            args.append(self.input()['fastq']['fastq2'].path)

        args.append('-o')
        args.append(self.output().path)

        return args

class FastqAlign(utils.MetaOutputHandler, luigi.Task):
    """Higher level task for the alignment of fastq files.
    
    It is given preference to local files over processing the alignment
    in order to reduce computational overhead. 

    Alignment is done with the Bwa mem utility.

    Parameters:
        fastq1_local_file (str): String indicating the location of a local
            Sam file for the alignment. 
        cpus (int): Integer indicating the number of cpus that can be used for 
            the alignment.

    Output:
        A dict mapping keys to `luigi.LocalTarget` instances for each of the 
        processed files. 
        The following keys are available:

        'sam' : Local file with the alignment.     

    """

    sam_local_file = luigi.Parameter(default='', description='Optional file path for the aligned sam file. If set, the alignment will be skipped.')
    cpus = luigi.Parameter(default='', description="Number of cpus to be used by each task thread.")

    def requires(self):
        dependencies = dict()

        if self.sam_local_file != '':
            dependencies.update({'sam': utils.LocalFile(file_path=self.sam_local_file)})
        else:
            dependencies.update({'sam' : BwaAlignFastq()})

        return dependencies

    def run(self)
        # yield PostDependency()
        pass

if __name__ == '__main__':
    luigi.run(['FastqAlign', 
            '--FastqAlign-create-report', 'False',
            '--FastqAlign-cpus', '8',
            '--GetFastq-fastq1-url', '',
            '--GetFastq-fastq2-url', '',
            '--GetFastq-from-ebi', 'False',
            '--GetFastq-paired-end', 'False',
            '--ReferenceGenome-ref-url', 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit',
            '--ReferenceGenome-from2bit', 'True',
            '--utils.GlobalParams-base-dir', path.abspath('./experiment'),
            '--utils.GlobalParams-log-dir', path.abspath(path.curdir),
            '--utils.GlobalParams-exp-name', 'hg19'])
