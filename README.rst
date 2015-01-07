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
