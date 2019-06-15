import os
import luigi
from luigi.contrib.external_program import ExternalProgramTask
from wespipeline import utils 
from .utils import MetaOutputHandler
from .utils import Wget
from .utils import GlobalParams

class GetProgram(ExternalProgramTask):
    def requires(self):
        program_file = path.join(GlobalParams().base_dir, 'twoBitToFa')
        program_url = 'ftp://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/twoBitToFa'

        return Wget(url=program_url, output_file=program_file)

    def output(self):
        program_file = path.join(GlobalParams().base_dir, 'twoBitToFa')
        return luigi.LocalTarget(program_file)

    def program_args(self):
        return ['chmod', '700', self.output().path]

class TwoBitToFa(ExternalProgramTask):
    ref_url = luigi.Parameter()

    def requires(self):
        file = path.join(GlobalParams().base_dir, GlobalParams().exp_name+'.2bit')

        return {
            'program': GetProgram(), 
            'file': Wget(url=self.ref_url, output_file=file),
        }    

    def output(self):
        return luigi.LocalTarget(path.join(GlobalParams().base_dir,GlobalParams().exp_name+'.fa'))

    def program_args(self):
        return [self.input()['program'].path, self.input()['file'].path, self.output().path]

class GetReferenceFa(MetaOutputHandler, luigi.WrapperTask):
    reference_local_file = luigi.Parameter(default='')
    ref_url = luigi.Parameter(default='')
    from2bit = luigi.Parameter(default='')

    def requires(self):
        if self.from2bit.lower() == 'true':
            dependency = TwoBitToFa(reference_local_file=self.reference_local_file ,ref_url=self.ref_url) 
        else:
            if self.reference_local_file != '':
                dependency = LocalFile(self.reference_local_file)
            else:
                out_file = luigi.LocalTarget(path.join(GlobalParams().base_dir,GlobalParams().exp_name+'.fa'))
                dependency = Wget(url=self.ref_url, output_file=out_file)

        return {'fa' : dependency}

class FaidxIndex(ExternalProgramTask):
    ref_url = luigi.Parameter()
    from2bit = luigi.Parameter()

    def requires(self): 
        return GetReferenceFa(from2bit=self.from2bit ,ref_url=self.ref_url)

    def output(self):
        return luigi.LocalTarget(self.input()['fa'].path+'.fai')

    def program_args(self):
        return ['samtools', 'faidx', self.input()['fa'].path]

class BwaIndex(ExternalProgramTask):
    ref_url = luigi.Parameter()
    from2bit = luigi.Parameter()

    def requires(self): 
        return GetReferenceFa(from2bit=self.from2bit ,ref_url=self.ref_url)

    def output(self):
        outputs = set()

        outputs.add(
            luigi.LocalTarget(
                path.join(GlobalParams().base_dir,GlobalParams().exp_name+".fa.amb")))
        outputs.add(
            luigi.LocalTarget(
                path.join(GlobalParams().base_dir,GlobalParams().exp_name+".fa.ann")))
        outputs.add(
            luigi.LocalTarget(
                path.join(GlobalParams().base_dir,GlobalParams().exp_name+".fa.bwt")))
        outputs.add(
            luigi.LocalTarget(
                path.join(GlobalParams().base_dir,GlobalParams().exp_name+".fa.pac")))
        outputs.add(
            luigi.LocalTarget(
                path.join(GlobalParams().base_dir,GlobalParams().exp_name+".fa.sa")))

        return outputs

    def program_args(self):
        return ['bwa', 'index', self.input()['fa'].path]

class ReferenceGenome(MetaOutputHandler, luigi.WrapperTask):
    reference_local_file = luigi.Parameter(default='',description='Optional string indicating the location for the reference genome. If set, it will not be downloaded.')
    ref_url = luigi.Parameter(default='', description="Url for the download of the reference genome.")
    from2bit = luigi.Parameter(default='', description="A boolean [True, False] indicating whether the reference genome must be converted from 2bit.")

    def requires(self):
        return {
            'faidx' : FaidxIndex(reference_local_file=self.reference_local_file, from2bit=self.from2bit ,ref_url=self.ref_url), \
            'bwa' : BwaIndex(reference_local_file=self.reference_local_file, from2bit=self.from2bit ,ref_url=self.ref_url), \
            'fa' : GetReferenceFa(reference_local_file=self.reference_local_file, from2bit=self.from2bit ,ref_url=self.ref_url) \
            }

if __name__ == '__main__':
    luigi.run(['ReferenceGenome', 
            '--ReferenceGenome-ref-url', 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.2bit',
            '--ReferenceGenome-from2bit', 'True',
            '--GlobalParams-base-dir', path.abspath(path.curdir),
            '--GlobalParams-log-dir', path.abspath(path.curdir),
            '--GlobalParams-exp-name', 'hg19'])
