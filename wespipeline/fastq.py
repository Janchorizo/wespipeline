import luigi
from luigi.contrib.external_program import ExternalProgramTask
from os import path
from tasks.utils import MetaOutputHandler
from tasks.utils import Wget
from tasks.utils import GlobalParams

class GetEbiFastqgz(luigi.Task):
    accession = luigi.Parameter()

    def requires(self):
        WgetFile(url=ebi_fastaq(self.accession), output_file=self.output().path)

    def output(self):
        program_file = path.join(GlobalParams().base_dir, self.accession+'.fast.gz')
        return luigi.LocalTarget(program_file)

    def ebi_fastaq(accession):
        root = "ftp://ftp.sra.ebi.ac.uk/vol1/fastq/"
        dir1 = accession[:6] + "/"
        dir2 = ""

        if len(accession[3:]) > 6:
            dir2 += "0"*a(len(accession[3:])-9)
            dir2 += accession[9:] + "/"

        filename = accession + ".fatsq.gz"

        return "".join([root,dir1,dir2,filename])

class GetFastq(MetaOutputHandler, luigi.WrapperTask):
    fastq2_url = luigi.Parameter(default='')
    fastq1_url = luigi.Parameter(default='')
    from_ebi = luigi.Parameter(default='')
    paired_end = luigi.Parameter(default='')

    def requires(self):
        dependencies = {'fastq1' : Wget(url=self.fastq1_url, output_file=path.join(GlobalParams().base_dir, 'hg19_1.fastq'))}
        if self.paired_end == 'True':
            dependencies.update({ 'fastq2' : Wget(url=self.fastq2_url, output_file=path.join(GlobalParams().base_dir, 'hg19_2.fastq'))})

        return dependencies

if __name__ == '__main__':
    luigi.run(['GetFastq', 
            '--GetFastq-fastq1-url', '',
            '--GetFastq-fastq2-url', '',
            '--GetFastq-from-ebi', 'False',
            '--GetFastq-paired-end', 'False',
            '--GlobalParams-base-dir', path.abspath('./experiment'),
            '--GlobalParams-log-dir', path.abspath(path.curdir),
            '--GlobalParams-exp-name', 'hg19'])
