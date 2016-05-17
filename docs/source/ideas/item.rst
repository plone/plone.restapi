Standard Item Display
=====================

Document, News Item, File, Image, Link.

JSON-LD Representation of a News Item::

  {
    # JSON-LD
    '@context': '/@@context.jsonld',  # needs to be generated
    '@id': '/plone/my-news-item',
    '@type': 'News Item',

    # Schema Fields
    'id': 'my-news-item',  # or '__name__'?
    'title': 'My News Item',
    ...

    # Additional Fields
    'portal': '/plone',  # not sure if this is useful, similar to entrypoint
    'parent': '/plone',  # or '__parent__' or 'container'
    # change note field?
    'review_state': 'published',
    'uuid': ..., # or is this UID?
    'layout': 'atct_album_view',

    # Image
    image: {
      @type: 'NamedBlobImage',
      contentType: 'image/png',
      filename: 'myimage.png',  # or download because of <a download='filename.png' href='/url/to/filename.png'>
      width: 500,
      height: 300,
      # @id/href/data/...
      data: '/plone/folder1/my-news-item/@@display-file/image/myimage.png',
    },
    image_caption: 'My lovely picture',

    # Text
    text: '<p>Hello world!</p>', # Or should it be an object like the edit use case?
    # Alternative (expanded) text representation. See https://github.com/plone/plone.app.textfield/blob/master/plone/app/textfield/interfaces.py#L39
    # text: {
    #  @type:
    #  'contentType': 'text/html',  # also rst/ plain text...
    #  'raw'
    #}

    # References: Potentially embedded with minimal info from catalog
    references: [
      '/plone/path/to/a',
      '/plone/path/to/b',
    ],
  }
