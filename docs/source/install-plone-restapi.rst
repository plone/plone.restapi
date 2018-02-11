Getting started with plone.restapi
==================================
If you haven't installed Plone locally, proceed to the next section, that is, installing Plone with plone.restapi. Make sure you have Python 2.7 and `virtualenv
<https://virtualenv.pypa.io>`_ installed.
If you have already set-up Plone locally, you can skip the next section and add plone.restapi as an add-on.

Install Plone locally with plone.restapi
----------------------------------------
.. code-block::

    git clone git@github.com:plone/plone.restapi && cd plone.restapi
    virtualenv-2.7 . || virtualenv .
    python bootstrap.py
    bin/buildout -Nv -c plone-5.1.x.cfg
    
::

Run an instance of Plone

.. code-block::

    ./bin/instance fg 
 
::


Add plone.restapi as an add-on
------------------------------

**Using Control Panel**

On your system, use the following command to run an instance of Plone

.. code-block::
    
        ./bin/instance fg 

::

You can find Plone here :  http://localhost:8080/ 

The Add-ons section on control panel defines which add-ons are currently installed for the Plone site, you can add plone.restapi as an addon : 

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

