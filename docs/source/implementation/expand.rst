How to edit or extend the pipeline
==================================

Three main use cases can be distinguished:

* Replacing an existing task for another that serves the same function.
* Adding new tasks to an existing step.
* Adding upstream dependencies within a step, that should be exectued after
the rest of the tasks of the step.

Replacing an existing task for another with the same funtionallity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All tasks implemented in a module serve for one of the two possible objectives: fulfilling other tasks
dependencies, or providing with part (or the whole) output of the step.

The first step is identifying which of this two is the case. In both cases it must mantain
the parameters and out put format in order for it work as expected; however,  if relacing an intermediate task,
the upstream tasks should be changed to this new one instead.

In the case of a task that provides part of the output for the higher level task of the module, it
only requires to replace the previous task with the new one in the high level task. 

.. code-block:: python

	class HighLevelTask(utils.MetaOutputHandler, luigi.WrapperTask):
	    
		param1 = luigi.Parameter(default="", description="")
		local_file = luigi.Parameter(default='', description="")

		def requires(self):
			dependencies = dict()
	    
			dependencies.update({'a': SomeTask()})
			dependencies.update({'b': OtherTask()})

			return dependencies

Beware that high level tasks expose the outputs of all involved tasks of the step, making each output accesible in
a dictionary which keys should remain intact in order to preserve the well functioning tasks dependent on this.

.. warning:: In the example above, the output of ``SomeTask`` and ``OtherTask`` maintains the original structure. Be carefull not
	to change the expected result as this would enter be conflict with what other task would expect to receive from the
	higher level task.

Adding new tasks to an existing step
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When new, independent, tasks are desired to be run for a step, it is only needed to add them to the dictionary containing the
dependencies.

It is important to add them in the ``requires`` method in order for the output of this new task to be checked. This allows
Luigi to identify when the step has been completely runned, or if needs to run part -or the whole- of the tasks.

.. note:: If parameters for the new task are set in the higher level task too, it will allow the users to specify them through
	the same manner as for other tasks without knowing the specific name of this new task: **--HigherLevelTask-the-parameter value**
	will be accessible through the command line. Prefer this way rather than making the user know what other tasks in the step 
	need its parameters to be set.

.. note:: Note too that if parameters for the new task are set in the higher level task, removing the task will not brake 
	dependencies on the step that set this parameter; whilst it will cause an error when a user tries setting a parameter in a
	task that is not longer available.


Adding upstream dependencies within a step, that should be exectued after the rest of the tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A slightly different to the previous use case may occur: the necessity of adding a task that needs to be executed after 
some step, but which is related to the same one. 

When adding functionality that is related to a step, it is best to add it in the same module.

For this, it is possible to replace the base class ``luigi.WrapperTask`` with ``luigi.Task``:

* ``wespipeline.MetaOutputHandler`` allows to define the output of a class based on the input; which is similar to the
behaviour of ``luigi.WrapperTask``, but with the addition of propagating the input.
* If any of the dependencies is not fulfilled, the task will run. Thus, requiring the dependencies and then executing
the *run* method.
* From within the run method, any task can yield dynamic dependencies; we can use this to launch the execution of
our step related upstream dependencies.

.. code-block:: python

	class HighLevelTask(utils.MetaOutputHandler, luigi.Task):
	    
		param1 = luigi.Parameter(default="", description="")
		local_file = luigi.Parameter(default='', description="")

		def requires(self):
			dependencies = dict()
	    
			dependencies.update({'a': SomeTask()})
			dependencies.update({'b': OtherTask()})

			return dependencies

		def run(self):
			yield UpstreamTask(aoutput=self.input()['a'])

Thus, this approach allows to extend the step with extra tasks, that can use the outputs without
the need of newer dependencies or affecting the interface that the step provides to other task requiring it.

.. warning:: The default behaviour of a task is running first the output method to check if the task has 
	already been executed correctly; which -in the case of classes inheriting from ``wespieline.MetaOutputHandler``-
	is equivalent to checking the fulfillment of the dependencies.
	Therefore, if all the inputs are already present, the upstream tasks will be nor executed or even checked.

.. note:: The default behaviour can be changed by overwritting the ** method, and returning ``False`` when the task
	should be runned. Then, if False is always returned, upstream dependencies will always be launched. 

Even though, it is best adviced to remove outputs when forced returning False in order to ensure no duplicate or strange 
behaviour occurs because of the output already existing, this not the case for high level tasks.

This task does not produce the output, but rather forwards its inputs; thus removing the output may cause side effects.

.. code-block:: python

	class HighLevelTask(utils.MetaOutputHandler, luigi.Task):
		force = luigi.BoolParameter()
		param1 = luigi.Parameter(default="", description="")
		local_file = luigi.Parameter(default='', description="")
		
		def complete(self):
			outputs = luigi.task.flatten(self.output())

			for output in outputs:
			if self.force and output.exists():
				output.remove()

			return all(map(lambda output: output.exists(), outputs))
		
		def requires(self):
			dependencies = dict()
			    
			dependencies.update({'a': SomeTask()})
			dependencies.update({'b': OtherTask()})
			
			return dependencies
		
		def run(self):
			yield UpstreamTask(output=self.input()['a'])

The example above would work well if ``HighLevelTask`` did not inherit from ``wespieline.MetaOutputHandler``.
The following is a better suited implementation, where all dependencies (included ``UpstreamTask``) will be
check for completition and launched for execution if it is not the case, preserving the desired order:

.. code-block:: python

	class HighLevelTask(utils.MetaOutputHandler, luigi.Task):
		param1 = luigi.Parameter(default="", description="")
		local_file = luigi.Parameter(default='', description="")
		
		def complete(self):
			return False
		
		def requires(self):
			dependencies = dict()
			    
			dependencies.update({'a': SomeTask()})
			dependencies.update({'b': OtherTask()})
			
			return dependencies
		
		def run(self):
			yield UpstreamTask(output=self.input()['a'])

Upon execution,dependencies will be checked first, ceating if neccessary the outputs for the task. The the run method will
be checked and executed if neccessary.