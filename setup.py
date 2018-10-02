from setuptools import setup, find_packages

version = '3.4.6-dev.0'

long_description = (
    open('README.rst').read() + '\n' +
    'Contributors\n'
    '============\n' + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read() + '\n'
)

TEST_REQUIRES = [
    'collective.MockMailHost',
    'plone.app.contenttypes',
    'plone.app.robotframework',
    'plone.app.testing [robot] >= 4.2.2',  # ROBOT_TEST_LEVEL added
    'plone.api',
    'requests',
    'freezegun',
    'plone.tiles',
    'mock',
]

PY2_ONLY = [
    'Products.Archetypes',
    'plone.app.collection',
]

if sys.version_info[0] == 2:
    TEST_REQUIRES += PY2_ONLY


setup(name='plone.restapi',
      version=version,
      description="plone.restapi is a RESTful hypermedia API for Plone.",
      long_description=long_description,
      # Get more strings from
      # https://pypi.org/classifiers/
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Framework :: Plone :: 5.1",
          "Framework :: Plone :: 5.2",
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
      namespace_packages=['plone', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'python-dateutil',
          'plone.behavior>=1.1',  # adds name to behavior directive 
          'plone.rest >= 1.0a6',  # json renderer moved to plone.restapi
          'plone.schema >= 1.2.0',  # new json field          
          'PyJWT',
          'pytz',
      ],
      extras_require={'test': TEST_REQUIRES},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
