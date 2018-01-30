Getting started with plone.restapi
==================================
If you haven't installed Plone locally, proceed to the next section, that is, installing Plone with plone.restapi. Make sure you have Python 2.7 and https://virtualenv.pypa.io installed.
If you have already set-up Plone locally, you can skip the next section and add plone.restapi as an add-on.

Install Plone locally with plone.restapi
----------------------------------------
.. code-block::

    git clone git@github.com:plone/plone.restapi
    virtualenv-2.7 . || virtualenv .
    python bootstrap.py
    bin/buildout -Nv -c plone-5.0.x.cfg
    
::

Run an instance of Plone

.. code-block::

    ./bin/instance fg 
 
::

Add plone.restapi as an add-on
------------------------------

**Using Control Panel**

Plone site setup(admin) -->  Add ons control panel -->  Install plone.restapi

**Installing plone.restapi add-on using buildout**


Edit your *buildout.cfg* file and add the plone.restapi package to the list of eggs:

.. code-block::

    [buildout]
    ...
    eggs =
      ...
      plone.restapi
  
::

Re-run buildout from your console:

.. code-block::

    bin/buildout
    
::

Re-start Plone:

.. code-block::

    bin/instance restart
    
::

