from setuptools import setup
from __init__ import __version__


setup(name='beaver',
      version=__version__,
      description='Beaver, an experimental semantic programming language for processing RDF graphs.',
      author='Ben Morris',
      author_email='ben@bendmorris.com',
      url='https://github.com/bendmorris/beaver',
      packages=['beaver.lib', 'beaver'],
      package_dir={
                'beaver':''
                },
      entry_points={
        'console_scripts': [
            'beaver = beaver.beaver:main',
        ],
      },
      )
