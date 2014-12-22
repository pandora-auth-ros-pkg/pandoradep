from setuptools import setup, find_packages


setup(name='pandoradep',
      packages=['pandoradep'],
      version='0.1',
      py_modules=['index'],
      description="A tiny cli tool to manage PANDORA's dependencies.",
      author='PANDORA Robotics Team',
      author_email='siderisk@auth.gr',
      url='https://github.com/pandora-auth-ros-pkg/pandoradep',
      license='BSD',
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
