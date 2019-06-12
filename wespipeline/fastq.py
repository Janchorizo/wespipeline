import luigi
from luigi.contrib.external_program import ExternalProgramTask
from os import path
from wespipeline import utils 

class FastqcQualityCheck(ExternalProgramTask):
    """Task used for creating a quality report on fastq files.

    The report is created using the Fastqc utility, reulsting on an
    html report, an a zip folder containing more detailed information
    about the quality of the reads.

    Parameters:
        fastq_file (str): Path os the fastq file to be analyzed.
    """

    fastq_file = luigi.Parameter()

    def output(self):
        return [
            luigi.LocalTarget(self.fastq_file.replace('.fastq', '_fastqc.html')),
            luigi.LocalTarget(self.fastq_file.replace('.fastq', '_fastqc.zip')),
        ]

    def program_args(self):
        return ['fastqc', '-f', 'fastq', self.fastq_file]
    
class SraToolkitFastq(ExternalProgramTask):
    """Task used for downloading fastq files from the NVBI archive.

    In case of the reads to be paired end, the output will consist
    of two separate fastq files.

    The output file(s) will have for name the accession number and,
        in the case of paired end reads, a suffix identifying each
        of the two fastq.

    Parameters:
        accession_number (str): NCBI accession number for the experiment.
        paired_end (bool): Non case sensitive boolean indicating wether
            the reads are paired_end.
    """

    accession_number = luigi.Parameter()
    paired_end = luigi.Parameter()

    def output(self):
        output_files = {'fastq1' : luigi.LocalTarget(self.accession_number + '.fastq')}
        if self.paired_end.lower() == 'true':
            output_files = {'fastq1' : luigi.LocalTarget(self.accession_number + '_1.fastq'),
                'fastq2' : luigi.LocalTarget(self.accession_number + '_2.fastq')}

        return output_files

    def program_args(self):
        command = ['fastq-dump']

        if self.paired_end.lower() == 'true':
            command.append('--split-files')

        command.append(self.accession_number)

        return command

class UncompressFastqgz(luigi.Task):
    """Task for uncompressing fastq files.

    The task uses utils.UncompressFile for uncompressing into fastq.
    If both fastq_local_file and fastq_url are set, the local file will
    have preference; thus reducing the overhead in the process.

    Parameters:
        fastq_local_file (str): String indicating the location of a local
            compressed fastq file.
        fastq_url (str): Url indicating the location of the resource for
            the compressed fastq file.
        output_file (str): String indicating the desired location and name 
            the output uncompressed fastq file.
    """

    fastq_local_file = luigi.Parameter(default='')
    fastq_url = luigi.Parameter(default='')
    output_file = luigi.Parameter(default='')

    def requires(self):
        if self.fastq_local_file != '':
            return utils.LocalFile(file=self.fastq_local_file)
        else:
            return utils.Wget(url=self.fastq_url, output_file=self.output_file + '.gz')

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def run(self):
        yield utils.UncompressFile(input_file=self.input().path, output_file=self.output().path)

class GetFastq(utils.MetaOutputHandler, luigi.Task):
    """Higher level task for the retrieval of the experiment fastq files.

    Three diferent sources for the fastq files are accepted: an existing local
    file, an NCBI accession number for the reads, and an external url indicating
    the location for the resources. The order in which the sources will be searched
    is the same as above: it is given preference to local files over external
    resources in order to reduce computational overhead, and NCBI accession number
    over external resources for reproducibility reasons.

    Parameters:
        fastq1_local_file (str): String indicating the location of a local
            compressed fastq file.
        fastq2_local_file (str): String indicating the location of a local
            compressed fastq file.
        fastq1_url (str): Url indicating the location of the resource for
            the compressed fastq file.
        fastq2_url (str): Url indicating the location of the resource for
            the compressed fastq file.
        paired_end (bool): Non case sensitive boolean indicating wether
            the reads are paired_end.
        compressed (bool): Non case sensitive boolean indicating wether
            the reads are compressed.
        create_report (bool): A non case-sensitive boolean indicating wether 
            to create a quality check report.
    """

    fastq1_local_file = luigi.Parameter(default='',description='Path to the fastq/ fastq.gz file. Use this parameter only if "from_local_file" is set to True.')
    fastq2_local_file = luigi.Parameter(default='',description='Path to the fastq/ fastq.gz file. Only used if the experiment is paired end.')

    fastq1_url = luigi.Parameter(default='', description="Url for the download of the sequenced data.")
    fastq2_url = luigi.Parameter(default='', description="Url for the download of the sequenced data. This will only be used for paired-end experiments.")

    accession_number = luigi.Parameter(default='', description="Optional string indicating the EBI accession number for retrieving the experiment.")

    paired_end = luigi.Parameter(default='false', description="A non case-sensitive boolean indicating wether the experimwnt is paired ended or not.")
    compressed = luigi.Parameter(default='false', description="A non case-sensitive boolean indicating wether the provided files are compressed or not.")
    create_report = luigi.Parameter(default='false', description="A non case-sensitive boolean indicating wether to create a quality check report.")

    def requires(self):
        if self.accession_number != '' and self.fastq1_local_file == '' and self.fastq1_local_file == '':
            return SraToolkitFastq(accession_number=self.accession_number, paired_end=self.paired_end)

        if self.compressed.lower() == 'true':
            if self.fastq1_local_file != '':
                dependencies = {'fastq1' : UncompressFastqgz(
                        fastq_local_file=self.fastq1_local_file, 
                        fastq_url=self.fastq1_url, 
                        output_file='.'.join(self.fastq1_local_file.split('.')[:-1]))}
            else: 
                dependencies = {'fastq1' : UncompressFastqgz(
                        fastq_local_file=self.fastq1_local_file, 
                        fastq_url=self.fastq1_url, 
                        output_file=path.join(utils.GlobalParams().base_dir, 'hg19_1.fastq'))}
        else:
            if self.fastq1_local_file != '':
                dependencies = {'fastq1' : utils.LocalFile(file=self.fastq1_local_file)}
            else:
                dependencies = {'fastq1' : utils.Wget(url=self.fastq1_url, output_file=path.join(utils.GlobalParams().base_dir, 'hg19_1.fastq'))}

        if self.paired_end.lower() == 'true':
            if self.compressed.lower() == 'true':
                if self.fastq2_local_file != '':
                    dependencies = {'fastq2' : UncompressFastqgz(
                            fastq_local_file=self.fastq2_local_file, 
                            fastq_url=self.fastq2_url, 
                            output_file='.'.join(self.fastq2_local_file.split('.')[:-1]))}
                else: 
                    dependencies = {'fastq2' : UncompressFastqgz(
                            fastq_local_file=self.fastq2_local_file, 
                            fastq_url=self.fastq2_url, 
                            output_file=path.join(utils.GlobalParams().base_dir, 'hg19_1.fastq'))}
            else:
                if self.fastq2_local_file != '':
                    dependencies = {'fastq2' : utils.LocalFile(file=self.fastq2_local_file)}
                else:
                    dependencies = {'fastq2' : utils.Wget(url=self.fastq2_url, output_file=path.join(utils.GlobalParams().base_dir, 'hg19_1.fastq'))}

        return dependencies

    def run(self):
        if self.create_report.lower() == 'true':
            report = [FastqcQualityCheck(fastq_file=self.input()['fastq1'].path)]
            if self.paired_end.lower() == 'true':
                report.append(FastqcQualityCheck(fastq_file=self.input()['fastq2'].path))

            yield report

if __name__ == '__main__':
    luigi.run(['GetFastq', 
            '--GetFastq-fastq1-url', '',
            '--GetFastq-fastq2-url', '',
            '--GetFastq-from-ebi', 'False',
            '--GetFastq-paired-end', 'False',
            '--GlobalParams-base-dir', path.abspath('./experiment'),
            '--GlobalParams-log-dir', path.abspath(path.curdir),
            '--GlobalParams-exp-name', 'hg19'])