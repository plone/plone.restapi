Getting started with plone.restapi
==================================

Install Plone on your system , follow the steps `here <https://docs.plone.org/manage/installing/installation.html>`_. 
You can also use the `simple plone buildout. <https://github.com/plone/simple-plone-buildout/blob/5.0.6/README.rst>`_.

On your system, use the following command to run an instance of Plone

.. code-block::
    
        ./bin/instance fg 

::

Add plone.restapi as an add-on
------------------------------

**Using Control Panel**

The Add-ons section on control panel defines which add-ons are currently installed for the Plone site, you can add plone.restapi as an addon : 

You can find Plone here :  http://localhost:8080/ 

.. image :: https://user-images.githubusercontent.com/25117249/37034887-c750067a-2170-11e8-9bdf-318cace2fdb7.png
Go to Plone site setup

.. image :: https://user-images.githubusercontent.com/25117249/37034888-c788f85e-2170-11e8-927b-12a9dac11ffa.png
Navigate to Add ons in control panel 

.. image :: https://user-images.githubusercontent.com/25117249/37034889-c7befc4c-2170-11e8-8860-9b7ce7f8a095.png
Install plone.restapi

.. image :: https://user-images.githubusercontent.com/25117249/37034890-c7f95266-2170-11e8-9a48-61447346364e.png

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

