import os
import luigi
from luigi.contrib.external_program import ExternalProgramTask

class GlobalParams(luigi.Config):
    """Task used for specifying globally accessible parameters.

    Parameters defined in this class are task independent and should
    mantain low.

    Parameters:
        exp_name (str): Name for the experiment. Useful for defining file names.
        log_dir (str): Absolute path for the logs of the application.
        base_dir (str): Absolute path to the directory where files are expected
            to appear if not specifyed differently.

    """

    exp_name = luigi.Parameter(description='(str): Name for the experiment. Useful for defining file names.')
    log_dir = luigi.Parameter(description='(str): Absolute path for the logs of the application.')
    base_dir = luigi.Parameter(description='(str): Absolute path to the directory where files are expected' \
        + 'to appear if not specifyed differently.')

class MetaOutputHandler:
    """Helper class for propagating inputs in WrapperTasks"""

    def output(self):
        return {key: task for key,task in self.input().items()}

class LocalFile(luigi.Task):
    """Helper task for making.

    No extra processing is done in the task. It allows to make tasks
    dependent on files using the same strategy as with other tasks.

    Parameters:
        file (str): Absolute path to the file to be tested.
    """

    file = luigi.Parameter(description='(str): Absolute path to the file to be tested.')

    def output(self):
        return luigi.LocalTarget(self.file)

    def run(self):
        if not os.path.isfile(self.file):
            raise Exception(f'{self.file} could not be found.')

class Wget(ExternalProgramTask):
    """Task for downloading files using the tool wget.

    Parameters:
        url (str): Url indicating the location of the resource to be retreived.
        output_file (str): Absolute path for the destiny location of the retrived resource.
    """

    url = luigi.Parameter(description='(str): Url indicating the location of the resource to be retreived.')
    output_file = luigi.Parameter(description='(str): Absolute path for the destiny location of the retrived resource.')

    def requires(self):
        return None

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def program_args(self):
        return ['wget', '-O', self.output().path, self.url]

class GunzipFile(ExternalProgramTask):
    """Task for unzipping compressed files.

    Gunzip will allways do the process inplace, deleting the extension.

    Parameters:
        input_file (str): Absolute path to the compressed file.
    """

    input_file = luigi.Parameter(description='(str): Absolute path to the compressed file.')

    def requires(self):
        return None

    def output(self):
        return luigi.LocalTarget('.'.join(self.input_file.split('.')[:-1]))

    def program_args(self):
        if os.path.isfile(self.input_file):
            return ['gunzip', '-d', self.input_file]
        else:
            raise Exception(f"Can't uncompress {self.input_file}. The file was not found")

class UncompressFile(ExternalProgramTask):
    """Task for unzipping compressed files to a desired location.

    Gunzip will allways do the process inplace, deleting the extension. This
    task allows to select the destination.

    This operation

    Parameters:
        input_file (str): Absolute path to the compressed file.
        output_file (str): Absolute path to the desired final location.
        copy (bool): Non case sensitive boolean indicating wether to copy or
            to move the file. Defaults to false.
    """

    input_file = luigi.Parameter(description='(str): Absolute path to the compressed file.')
    output_file = luigi.Parameter(description='(str): Absolute path to the'
        +' desired final location.')
    copy = luigi.Parameter(default='false', description='(bool): Non case sensitive'
        + 'boolean indicating wether to copy or to move the file. Defaults to false.')

    def requires(self):
        return GunzipFile(self.input_file)

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def program_args(self):
        if os.path.isfile(self.input().path):
            command = 'cp' if self.copy.lower() == 'true' else 'mv'

            if os.path.abspath(self.input().path) != os.path.abspath(self.output_file):
                return [command, self.input().path, self.output_file]
            else:
                return ['echo', 'Input and output files are the same']
        else:
            raise Exception(f"Can't uncompress {self.input_file}. The file was not found")