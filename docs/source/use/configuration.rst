Configuration
=============

Within the scope of the analysis, there are a set of options that can be set for 
adjusting the experiment to one's neccesities. There are, however, other configuration
options that affect the environment in which the pipeline is executed:

Making Luigi task historic persistent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Luigi offers a web interface for monitoring and analysing the execution of the pipeline.
However, it may be the case that a persistent history may be used for later analysis.

For this, Luigi offers a -at the moment beta- option for accessing the excutions through
the /history api.
