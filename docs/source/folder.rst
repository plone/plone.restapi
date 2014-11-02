Folderish Objects
=================

Folder
------

Minimal, embedded::

  {
    @context: "/@@context.jsonld",
    @id: "/plone/folder1",
    @type: "Folder",
    id: "folder1",
    title: "Folder 1",
    ...

    @graph: [
      "/folder1/my-news-item",
      "/folder1/more-news",
    ]
  }


Folder Listing
--------------

Folder listing with items and layout::

  {
    @context: "/@@context.jsonld",
    @id: "/plone/folder1",
    @type: "Folder",
    id: "folder1",
    title: "Folder 1",
    ...
    layout: "folder_listing",

    @graph: [
      # properties here are those needed for the listing view
      {
        @id: "/plone/folder1/my-news-item",
        @type: "News Item",
        id: "my-news-item",
        title: "My News Item",
        description: "...",
      },
      {
        @id: "/plone/folder1/my-news-item",
        @type: "News Item",
        id: "my-news-item",
        title: "My News Item",
        description: "...",
      }
    ]
  }


Batching
--------

...

