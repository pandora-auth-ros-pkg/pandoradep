pandoradep
==========

pandoradep is a python tool for easy deployment of PANDORA packages

### Install
Via `PyPI`:
```
sudo pip install pandoradep
```
Or clone the code and install it, running:
```
python setup.py install
```

### Usage
Init `wstool` in your workspace:
```
wstoll init .
```
Scan and write the dependencies to a `.rosinstall` file:
```
pandoradep scan <repo_root_directory> > some_file.rosinstall
```
Intall the dependencies, by running:
```
wstool merge some_file.rosinstall
wstool update
```

_Note: you can find more info about `wstool` and `rosinstall` files [here](https://github.com/pandora-auth-ros-pkg/pandora_docs/wiki/Setup%20Packages)._
