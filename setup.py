from setuptools import setup, find_packages
import sys

version = "8.30.1.dev0"

assert sys.version_info >= (
    3,
    6,
    0,
), "plone.restapi 8 requires Python 3.6.0+. Please downgrade to plone.restapi 7 for Python 2 and Plone 4.3/5.1."


def read(filename):
    with open(filename) as myfile:
        try:
            return myfile.read()
        except UnicodeDecodeError:
            # Happens on one Jenkins node on Python 3.6,
            # so maybe it happens for users too.
            pass
    # Opening and reading as text failed, so retry opening as bytes.
    with open(filename, "rb") as myfile:
        contents = myfile.read()
        return contents.decode("utf-8")


long_description = (
    read("README.rst")
    + "\n"
    + "Contributors\n"
    + "============\n"
    + "\n"
    + read("CONTRIBUTORS.rst")
    + "\n"
    + read("CHANGES.rst")
    + "\n"
)

TEST_REQUIRES = [
    "collective.MockMailHost",
    "plone.app.caching",
    "plone.app.contenttypes",
    "plone.app.robotframework",
    "plone.app.testing [robot] >= 4.2.2",  # ROBOT_TEST_LEVEL added
    "plone.api",
    "requests",
    "plone.tiles",
    "mock",
]

setup(
    name="plone.restapi",
    version=version,
    description="plone.restapi is a RESTful hypermedia API for Plone.",
    long_description=long_description,
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone rest restful hypermedia api json",
    author="Timo Stollenwerk (kitconcept GmbH)",
    author_email="tisto@plone.org",
    url="https://github.com/plone/plone.restapi/",
    license="gpl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plone"],
    python_requires=">=3.6.0",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "importlib-metadata; python_version<'3.8'",
        "python-dateutil",
        "plone.rest",  # json renderer moved to plone.restapi
        "plone.schema>=1.2.1",  # new/fixed json field
        "Products.CMFPlone>=5.2",
        "PyJWT>=1.7.0",
        "pytz",
    ],
    extras_require={"test": TEST_REQUIRES},
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
