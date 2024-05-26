from setuptools import setup

setup(
  name='metralabs',
  version='0.0.1',
  description='MetraLabs Kickelhack Challenge Package',
  author='Adrian Kriegel',
  author_email='adrian.kriegel@metralabs.com',
  packages=['metralabs'], 
  install_requires=[
    'pyvista',
    'pyvistaqt',
    'numpy',
    'open3d',
    'matplotlib',
    'pytest',
    'pillow',
    'scipy',
    'munkres'
  ]
)
