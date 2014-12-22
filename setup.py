from setuptools import setup, find_packages


setup(name='PandoraDep',
      version='0.1',
      py_modules=['index'],
      description="A tiny cli tool to manage PANDORA's dependencies.",
      author='PANDORA Robotics Team',
      license='BSD',
      packages=find_packages(),
      install_requires=[
          'click',
          'catkin-pkg',
          'requests',
          'colorama',
          'pyYAML'
          ],
      entry_points='''
        [console_scripts]
        pandoradep=index:cli
      ''',
      )
