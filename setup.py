from setuptools import setup, find_packages

import os

version = '3.2.1.dev0'

long_description = (
    open('README.rst').read() + '\n' +
    'Contributors\n'
    '============\n' + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read() + '\n'
)


HTTP_EXAMPLES_PATH = 'docs/source/_json/'


def collect_http_examples():
    """Gather relative paths to every HTTP example file.

    We need to do this dynamically because the data_files argument to
    setup() doesn't support globs (wildcards).

    If the HTTP examples directory is ever moved, the HTTP_EXAMPLES_PATH
    above needs to be updated before a new release is cut.

    The examples need to be included via data_files because they are outside
    a Python package. So we can't include them using package_data, which only
    works relative to Python packages. (The MANIFEST only controls what gets
    included in the source distribution. Listing these files in data_files
    ensures they actually get copied to the installed .egg).
    """
    examples_path = HTTP_EXAMPLES_PATH
    example_filenames = os.listdir(examples_path)
    return [os.path.join(examples_path, fn) for fn in example_filenames]


setup(name='plone.restapi',
      version=version,
      description="plone.restapi is a RESTful hypermedia API for Plone.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Framework :: Plone :: 5.1",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone rest restful hypermedia api json',
      author='Timo Stollenwerk (kitconcept GmbH)',
      author_email='tisto@plone.org',
      url='https://github.com/plone/plone.restapi/',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      data_files=[
          (HTTP_EXAMPLES_PATH, collect_http_examples()),
      ],
      namespace_packages=['plone', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'python-dateutil',
          'plone.rest >= 1.0a6',  # json renderer moved to plone.restapi
          'plone.schema >= 1.2.0',  # new json field          
          'PyJWT',
          'pytz',
      ],
      extras_require={'test': [
          'Products.Archetypes',
          'collective.MockMailHost',
          'plone.app.collection',
          'plone.app.contenttypes',
          'plone.app.robotframework',
          'plone.app.testing [robot] >= 4.2.2',  # ROBOT_TEST_LEVEL added
          'plone.api',
          'requests',
          'freezegun',
          'plone.tiles',
          'mock',
      ]},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
