pandoradep |PyPI version|
=========================

pandoradep is a python tool for easy deployment of PANDORA packages

Install
~~~~~~~

Via `PyPI`_:

::

    sudo pip install pandoradep

Or clone the code and install it, running:

::

    python setup.py install

Usage
~~~~~

Start working on a repo with

::
   pandoradep get pandora_vision

This will download the ``pandora_vision`` repo with all its dependencies.

Fetching dependencies in a workspace

::
    pandoradep fetch

This will scan and fetch all the dependencies from the current directory.


You can also use pandoradep to create rosinstall files.

Init ``wstool`` in your workspace:

::

    wstool init .

Scan and write the dependencies to a ``rosinstall`` file:

::

    pandoradep scan repo_root_directory > some_file.rosinstall

Install the dependencies, by running:

::

    wstool merge some_file.rosinstall
    wstool update

You can find more info about ``wstool`` and ``rosinstall`` files `here`_.

.. _PyPI: https://pypi.python.org/pypi/pandoradep
.. _here: https://github.com/pandora-auth-ros-pkg/pandora_docs/wiki/Setup%20Packages

.. |PyPI version| image:: https://badge.fury.io/py/pandoradep.svg
   :target: http://badge.fury.io/py/pandoradep
