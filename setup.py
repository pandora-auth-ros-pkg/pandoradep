from setuptools import setup


setup(name='pandoradep',
      packages=['pandoradep'],
      version='0.4.0',
      py_modules=['index'],
      description="A tiny cli tool to manage PANDORA's dependencies.",
      author='PANDORA Robotics Team',
      author_email='siderisk@auth.gr',
      url='https://github.com/pandora-auth-ros-pkg/pandoradep',
      license='BSD',
      install_requires=[
          'click==5.1.0',
          'catkin-pkg==0.2.8',
          'requests==2.8.1',
          'colorama',
          'pyYAML'
          ],
      entry_points='''
        [console_scripts]
        pandoradep=index:cli
      ''',
      )
