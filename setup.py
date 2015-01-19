from setuptools import setup


setup(name='pandoradep',
      packages=['pandoradep'],
      version='0.2.2',
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
