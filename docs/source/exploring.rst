.. _exploring:

Explore the API using Postman
=============================

To discover the API interactively, the Chrome-Extension Postman_ is a suitable solution.


Configuration
-------------

To easily follow links returned by request based on the API, 

* go to the menu under the wrench icon on the top right
* choose Settings 
* activate the option **"Retain headers on clicking on links"** :

|postman-retain-headers|


This option makes sure, once a HTTP-Header is configured, it will be reused during following requests, if these are initiated by clicking on links resulting from the initial request. This way navigating the structure using the API becomes a snap.

The option **"Send anonymous usage data to Postman"** should be deactivatet.

Usage
-----

Choose the suitable **HTTP verb** to be used for your request. This can be selected using the :gui-label:`Postman Drop-Down Menu`. 

Enter the **object URL** of the object that should be the target of a request into the :gui-label:`field` right to the HTTP verb:

|postman-request|


Now set the appropriate HTTP headers. 

* The ``Authorization`` header for the authentication related to the right user
* The ``Accept`` header to initiate the right behaviour by the API related to this request.

----------

To set the ``Authorization`` header, there is a reserved tab, that is responsible to generate the final header based on the authentication method and username + password.

You have to select 
* *"Basic Auth"** as the authentication method
* A valid existing user with appropriate permissions 

After providing these parameters angegeben wurde, kann mittels Klick auf **"Update Request"** der entsprechende ``Authorization`` Header erzeugt und in den vorbereiteten Request übernommen werden.

After providing these parameters you can create the resulting ``Authorization`` Header and insert it into the prepared request by clicking on **"Update Request"**.

|postman-basic-auth|

----------

In the  **"Headers"** tab you now need to insert the ``Accept: application/json`` header as well:

|postman-headers|


The request is now ready and can be send by clicking on **"Send"** button.

The **response** of the server is now displayed below the request. You can easily follow the links on the ``@id`` attributes by clicking on them. For every link Postman has prepared another request sharing the same headers that can be send again by licking on the  **"Send"** button.

You can now explore the whole stucture of your application easily via the API using ``GET`` requests.


.. _Postman: http://www.getpostman.com/

.. |postman-retain-headers| image:: ../_static/img/postman_retain_headers.png
.. |postman-request| image:: ../_static/img/postman_request.png
.. |postman-basic-auth| image:: ../_static/img/postman_basic_auth.png
.. |postman-headers| image:: ../_static/img/postman_headers.png

.. disqus::