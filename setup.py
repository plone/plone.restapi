from setuptools import setup, find_packages

version = '1.0a18'

long_description = (
    open('README.rst').read() + '\n' +
    'Contributors\n'
    '============\n' + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read() + '\n'
)

setup(name='plone.restapi',
      version=version,
      description="plone.restapi is a RESTful hypermedia API for Plone.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone rest restful hypermedia api json',
      author='Timo Stollenwerk',
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
          'plone.rest >= 1.0a6',  # json renderer moved to plone.restapi
          'Products.PasswordResetTool',  # gone in Plone 5.1
          'PyJWT',
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
      ]},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
