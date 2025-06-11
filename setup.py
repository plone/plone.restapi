from setuptools import find_packages
from setuptools import setup

import pathlib
import sys


version = "9.15.0"

if sys.version_info.major == 2:
    raise ValueError(
        "plone.restapi 10 requires Python 3. "
        "Please downgrade to plone.restapi 7 for Python 2 and Plone 4.3/5.1."
    )


long_description = "\n".join(
    [
        pathlib.Path(filename).read_text()
        for filename in ("README.md", "CONTRIBUTORS.md", "CHANGES.md")
    ]
)

TEST_REQUIRES = [
    "collective.MockMailHost",
    "plone.app.caching",
    "plone.app.contenttypes[test]",
    "plone.app.iterate",
    "plone.app.discussion[test]",
    "plone.app.multilingual",
    "plone.app.testing",
    "plone.app.upgrade",
    "plone.api",
    "plone.rest>=3.0.1",
    "requests",
]

setup(
    name="plone.restapi",
    version=version,
    description="plone.restapi is a RESTful hypermedia API for Plone.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        # "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "packaging",
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
      [console_scripts]
      update_restapi_locales = plone.restapi.locales.update:update_locale
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
