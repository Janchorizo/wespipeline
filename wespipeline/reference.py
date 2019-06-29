import os
import luigi
from luigi.contrib.external_program import ExternalProgramTask
from wespipeline import utils 

class GetProgram(ExternalProgramTask):
    """Task user for downloading and giving execution permissions to the 2bit program.

    The task gives execute permissions to the conversion utility for 2bit files
    to be converted to fa files which can then be used for aligning the sequences.

    The source for the program is ftp://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/twoBitToFa.

    Parameters:
        none

    Output:
        A `luigi.LocalTarget` for the executable.

    """
    
    def requires(self):
        program_file = path.join(utils.utils.GlobalParams().base_dir, 'twoBitToFa')
        program_url = 'ftp://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/twoBitToFa'

        return Wget(url=program_url, output_file=program_file)

    def output(self):
        program_file = path.join(utils.utils.GlobalParams().base_dir, 'twoBitToFa')
        return luigi.LocalTarget(program_file)

    def program_args(self):
        return ['chmod', '700', self.output().path]

class TwoBitToFa(ExternalProgramTask):
    """Task user for Converting 2bit files to the fa format.

    The task will use a local executable or require the task for obtaining it, and 
    use with the reference genome.

    Parameters:
        ref_url (str): Url for the resource with the reference genome.
        reference_local_file (str): Path for the reference genome 2bit file. If given
            the ``ref_url`` parameter will be ignored.

    Output:
        A `luigi.LocalTarget` for the reference genome fa file.

    """

    ref_url = luigi.Parameter()
    reference_local_file = luigi.Parameter(default='')

    def requires(self):
        if self.reference_local_file != '':
            dependencies = {
                'program': utils.GetProgram(), 
                'file': utils.LocalFile(file=self.reference_local_file),
            }
        else:
            file = path.join(utils.utils.GlobalParams().base_dir, utils.utils.GlobalParams().exp_name+'.2bit')
            dependencies = {
                'program': GetProgram(), 
                'file': utils.Wget(url=self.ref_url, output_file=file),
            }

        return dependencies 

    def output(self):
        return luigi.LocalTarget(path.join(utils.utils.GlobalParams().base_dir,utils.utils.GlobalParams().exp_name+'.fa'))

    def program_args(self):
        return [self.input()['program'].path, self.input()['file'].path, self.output().path]

class GetReferenceFa(utils.MetaOutputHandler, luigi.WrapperTask):
    """Task user for obtaining the reference genome .fa file.

    This task will retrieve an external genome or use a provided local one, and convert
    it from 2bit format to .fa if neccessary.

    Parameters:
        ref_url (str): Url for the resource with the reference genome.
        reference_local_file (str): Path for the reference genome 2bit file. If given
            the ``ref_url`` parameter will be ignored.
        from2bit (bool): Non case sensitive boolean indicating wether the reference genome
            if in 2bit format. Defaults to false.

    Output:
        A `luigi.LocalTarget` for the reference genome fa file.  
    
    """

    reference_local_file = luigi.Parameter(default='')
    ref_url = luigi.Parameter(default='')
    from2bit = luigi.BoolParameter()

    def requires(self):
        if self.from2bit == True:
            dependency = TwoBitToFa(reference_local_file=self.reference_local_file ,ref_url=self.ref_url) 
        else:
            if self.reference_local_file != '':
                dependency = utils.LocalFile(self.reference_local_file)
            else:
                out_file = luigi.LocalTarget(path.join(utils.utils.GlobalParams().base_dir, utils.utils.GlobalParams().exp_name+'.fa'))
                dependency = Wget(url=self.ref_url, output_file=out_file)

        return dependency

class PicardDict(ExternalProgramTask):
    """Task user for creating a dict file with the reference genome .fa file with the picard utility.

    Parameters:
        None

    Output:
        A `luigi.LocalTarget` for the .fai index file for the reference genome .  
    
    """

    def requires(self): 
        return GetReferenceFa(reference_local_file=ReferenceGenome().reference_local_file,
                from2bit=ReferenceGenome().from2bit ,
                ref_url=ReferenceGenome().ref_url)

    def output(self):
        return luigi.LocalTarget(self.input().path.replace('.fa','.dict'))

    def program_args(self):
        return ['picard', 'CreateSequenceDictionary', f'R={self.input().path}']

class FaidxIndex(ExternalProgramTask):
    """Task user for indexing the reference genome .fa file with the samtools faidx utility.

    Aligning the reference genome helps reducing access time drastically.

    Parameters:
        None

    Output:
        A `luigi.LocalTarget` for the .fai index file for the reference genome .  
    
    """

    def requires(self): 
        return GetReferenceFa(reference_local_file=ReferenceGenome().reference_local_file,
                from2bit=ReferenceGenome().from2bit ,
                ref_url=ReferenceGenome().ref_url)

    def output(self):
        return luigi.LocalTarget(self.input().path+'.fai')

    def program_args(self):
        return ['samtools', 'faidx', self.input().path]

class BwaIndex(ExternalProgramTask):
    """Task user for indexing the reference genome .fa file with the bwa index utility.

    Aligning the reference genome helps reducing access time drastically.

    Parameters:
        None

    Output:
        A set of five files are result of indexing the reference genome. The extensions
        for each of the files are '.amb', '.ann', '.bwt', '.pac', '.sa'.
    
    """

    def requires(self): 
        return GetReferenceFa(reference_local_file=ReferenceGenome().reference_local_file,
                from2bit=ReferenceGenome().from2bit ,
                ref_url=ReferenceGenome().ref_url)

    def output(self):
        outputs = set()

        outputs.add(
            luigi.LocalTarget(
                os.path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+".fa.amb")))
        outputs.add(
            luigi.LocalTarget(
                os.path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+".fa.ann")))
        outputs.add(
            luigi.LocalTarget(
                os.path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+".fa.bwt")))
        outputs.add(
            luigi.LocalTarget(
                os.path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+".fa.pac")))
        outputs.add(
            luigi.LocalTarget(
                os.path.join(utils.GlobalParams().base_dir, utils.GlobalParams().exp_name+".fa.sa")))

        return outputs

    def program_args(self):
        return ['bwa', 'index', self.input().path]

class ReferenceGenome(utils.MetaOutputHandler, luigi.Task):
    """Higher level task for retrieving the reference genome.
    
    It is given preference to local files over downloading the reference. However the 
    indexing of the reference genome is always done using ``GloablParams.exp_name`` and
    ``GlobalParams.base_dir`` for determining filenames and location for newer files
    respectively.

    The indexing is done using both Samtools and Bwa toolkits.

    Parameters:
        reference_local_file (str) : Optional string indicating the location for the reference genome. If set, it will not be downloaded.
        ref_url (str) : Url for the download of the reference genome.
        from2bit (bool) : A boolean [True, False] indicating whether the reference genome must be converted from 2bit.


    Output:
        A dict mapping keys to `luigi.LocalTarget` instances for each of the processed files. 
        The following keys are available:

        'faidx' : Local file with the index, result of indexing with Samtools.     
        'bwa' : Set of five files, result of indexing the reference genome with Bwa.
        'fa' : Local file with the reference genome.

    """

    reference_local_file = luigi.Parameter(default='',
        description='Optional string indicating the location for the reference genome. If set, it will not be downloaded.')

    ref_url = luigi.Parameter(default='', 
        description="Url for the download of the reference genome.")

    from2bit = luigi.BoolParameter(parsing=luigi.BoolParameter.EXPLICIT_PARSING, 
        description="A boolean indicating whether the reference genome must be converted from 2bit. Defaults to false.")

    def requires(self):
        dependencies = dict()

        dependencies.update({'faidx' : FaidxIndex()})
        dependencies.update({'bwa' : BwaIndex()})
        dependencies.update({'dict' : PicardDict()})
        dependencies.update({'fa' : GetReferenceFa(reference_local_file=self.reference_local_file, from2bit=self.from2bit ,ref_url=self.ref_url)})

        return dependencies

    def run(self):
        # yield PostDependency()
        pass

if __name__ == '__main__':
    luigi.run(['ReferenceGenome', 
            '--ReferenceGenome-ref-url', 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit',
            '--ReferenceGenome-from2bit', 'True',
            '--utils.GlobalParams-base-dir', path.abspath(path.curdir),
            '--utils.GlobalParams-log-dir', path.abspath(path.curdir),
            '--utils.GlobalParams-exp-name', 'hg19'])
