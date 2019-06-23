Steps
=====

Basic Luigi Task class implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Luigi's scheduler allows the execution of the task specified and the
dependency resolution based on the execution of the `requires` method from
the Task implementation.

Any Task in Luigi has the following general structure:

.. code-block:: python

	class MyTask([luigi.Task, luigi.WrapperTask, luigi.contrib.ExternalProgramTask, ...]):
		param1 = luigi.Parameter(default=[value], description=[string])
		param2 = luigi.Parameter(default=[value], description=[string])
		. . .
		paramN = luigi.Parameter(default=[value], description=[string])

		def requires(self):
			return SomeTask()

			return [
				SomeTask(param=[value]),
				OtherTask(),
			]

			return {
				'a':SomeTask(param=[value]),
				'b':OtherTask(),
			}

		def output(self):
			returns luigi.LocalTarget([path])
			
			returns [luigi.LocalTarget([path]), luigi.contrib.mongodb.MongoTarget]
			
			returns {
				'c':luigi.LocalTarget([path]), 
				'd'luigi.contrib.mongodb.MongoTarget
			}

* Parameters are exposed in the command line interface, showing the optional argument `description` if provided.

* The requires method can return nothing, a Task instance, or an structure containing Task intances. These tasks will be accessible from within the class through the input method: `self.input()`; which will preserve the structure that was retrieved in the method.

* The output method can return nothing, a luigi.Target instance, or an structure containing Target intances. These targets will be accessible from within the class through the output method: `self.output()`; which will preserve the structure that was retrieved in the method. This is the first method executed,and used to find out if the Task needs to be runned.

Additionally, depending on the specific Task class on which it inherits, the class may have some other specific methods,
such as the `run` method for executing Python code, or the `program\_args` for returning the arguments for external program
executions.

Managing coupling in tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^

The analysis here proposed needs for various tasks within each of the different steps. However, if they are
implemented following the previous structure, maintaining and extending the pipeline would we too complicated; let's
see this in the following example:

.. code-block:: python

	import luigi
	from somePackage import ExtTask

	class FinalTask(luigi.Task):
		param = luigi.Parameter(default=[value])

		def requires(self):
			return IntermediateTask(param=param)

		def output(self):
			returns luigi.LocalTarget(pathA)

		def run(self):
			pass

	class IntermediateTask(luigi.Task):
		param = luigi.Parameter()

		def requires(self):
			return InitialTask(param=self.param)

		def output(self):
			returns luigi.LocalTarget(path2)

		def run(self):
			pass

	class InitialTask(luigi.Task):
		param = luigi.Parameter()

		def requires(self):
			return ExtTask(param2='1234')

		def output(self):
			returns luigi.LocalTarget(path1)

		def run(self):
			print(self.param1)

Here, a couple of problems arise related to the fact that:
* Only the first task makes use of the parameter `param`, but all of the previous tasks need to have it in order to pass it.

* If at any point it is needed to change the class required by ```FinalTask```, it would be neccessary to know what input ```FinalTask``` expects, what parameters ```InitialTask``` needs in order to preserve its interface, and change in ```FinalTask``` the name of the class that is being sustituted.

* This last point can be impossible for the case of tasks required in many others, where identitying each place where it is being used is too difficoult.

* This complicates even more when external tasks are imported, such as ```ExtTask```.

* If this pipeline was to be extended, it would be necessary to know in advance what parameters and results would the new task need to forward in order to keep the pipeline working, and the previous upstream dependency would need to be edited to include the new task.

These problems make it difficult to create a modular pipeline. To solve it, the following was done:

A lightweight class (`MetaOutputHandler <file:///home/alex/projects/wespipeline/docs/build/html/modules/wespipeline.html#wespipeline.utils.MetaOutputHandler>`_) 
was implemented to set the output of a task based on the input. This means that inputs are forwarded, and allows for implementing higher
level of abstraction tasks that allow to require al neccessary tasks for a step while making the outputs accessible.

**Each step** of the analysis is implemented in a **separate module**, with a **high level abstraction Task** subclass **as the entrypoint**.

Using this type of tasks allows too for putting parameters together, so that only one task exposes parameters; which makes it easier to
use in a decoupled way.

An example of this type of Task is the ` <>`_.

.. code-block:: Python

	class FastqAlign(utils.MetaOutputHandler, luigi.WrapperTask):
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
	        if self.sam_local_file != '':
	            return {'sam': utils.LocalFile(file_path=self.sam_local_file)}
	        else:
	            return {'sam' : BwaAlignFastq()}

This task doesn't do any actual computation, but requires the  Task neccessary for obtaining the fastq alignment. Even though that
right now Bwa is being used, changing the task for another one would be easy; as other tasks require wespipeline.align.FastqAlign,
and do not care about the tasks required by it. An example below:

.. code-block:: python

	import luigi
	from wespipeline.align import FastqAlign

	class MyTask(luigi.Task):

		def requires(self):
			return FastqAlign(cpus=2)

		def output(self):
			returns luigi.LocalTarget("/.../output.txt")

		def run(self):
			print(self.input()['sam'])

As shown, ```MyTask``` requires the higher level task, uses the outputs of the tasks in that step, and accesses the output through
an interface which is agnostic from the actual implementation of the task.

Morover, parameters set in this higher Task can be accesses from any other by using an instance (```FastqAlign().sam_local_file```);
this means that there is no longer a need for propagating unused parameters.