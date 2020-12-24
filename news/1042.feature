A new service endpoint and expand is available, a Navigation Portlet exposed as
``@navportlet``. It uses the same semantics as the classic Plone navigation
portlet, largely through reusing the same code. Instead of storing the
"portlet" configuration in a portlet assignment storage, you can pass these as
parameters to the service or expand component.

You can provide these as parameters:

- ``name`` - The title of the navigation tree.
- ``root_path`` - Root node path, can be "frontend path", derived from router
- ``includeTop`` - Bool, Include top nodeschema
- ``currentFolderOnly`` - Bool, Only show the contents of the current folder.
- ``topLevel`` - Int, Start level
- ``bottomLevel`` - Int, Navigation tree depth
- ``no_icons`` - Bool, Suppress Icons
- ``thumb_scale`` - String, Override thumb scale
- ``no_thumbs`` = Bool, Suppress thumbs

You should prefix these parameters with ``expand.navportlet.``, so a request
would look like:

``http://localhost:55001/plone/?expand.navportlet.topLevel=1&expand.navportlet.name=Custom+name``
