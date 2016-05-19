# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityContent

import os

LOREMIPSUM_HTML_10_PARAGRAPHS = '''<p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p><p>Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.</p><p>Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.</p><p>Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p><p>Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.</p><p>At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, At accusam aliquyam diam diam dolore dolores duo eirmod eos erat, et nonumy sed tempor et et invidunt justo labore Stet clita ea et gubergren, kasd magna no rebum. sanctus sea sed takimata ut vero voluptua. est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.</p><p>Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus.</p><p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p><p>Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.</p><p>Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.'''  # noqa

LOREMIPSUM_TEXT_PARAGRAPH = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.'  # noqa


def set_description(obj):
    if IDexterityContent.providedBy(obj):
        obj.description = LOREMIPSUM_TEXT_PARAGRAPH
    else:
        obj.setDescription(LOREMIPSUM_TEXT_PARAGRAPH)


def set_text(obj):
    if IDexterityContent.providedBy(obj):
        obj.text = RichTextValue(
            LOREMIPSUM_HTML_10_PARAGRAPHS,
            'text/html',
            'text/x-html-safe'
        )
    else:
        obj.setText(LOREMIPSUM_HTML_10_PARAGRAPHS)


def set_image(obj):
    if IDexterityContent.providedBy(obj):
        from plone.namedfile.file import NamedBlobImage
        filename = os.path.join(os.path.dirname(__file__), u'image.png')
        obj.image = NamedBlobImage(
            data=open(filename, 'r').read(),
            filename=filename
        )
    else:
        filename = os.path.join(os.path.dirname(__file__), u'image.png')
        obj.setImage(open(filename, 'r').read())


def set_file(obj):
    if IDexterityContent.providedBy(obj):
        from plone.namedfile.file import NamedBlobFile
        filename = os.path.join(os.path.dirname(__file__), u'file.pdf')
        obj.file = NamedBlobFile(
            data=open(filename, 'r').read(),
            filename=filename
        )
    else:
        filename = os.path.join(os.path.dirname(__file__), u'file.pdf')
        obj.setFile(open(filename, 'r').read())


def publish(content):
    """Publish the object if it hasn't been published."""
    portal_workflow = getToolByName(getSite(), "portal_workflow")
    if portal_workflow.getInfoFor(content, 'review_state') != 'published':
        portal_workflow.doActionFor(content, 'publish')
        return True
    return False


def step_setup_content(context):
    marker_file = 'plone.restapi_performance_testing.txt'
    if context.readDataFile(marker_file) is None:
        return
    portal = getSite()

    # Document
    portal.invokeFactory('Document', id='document', title='Document')
    portal.document.description = LOREMIPSUM_TEXT_PARAGRAPH
    set_description(portal.document)
    set_text(portal.document)
    publish(portal.document)
    portal.document.reindexObject()

    # News Item
    portal.invokeFactory('News Item', id='newsitem', title='NewsItem')
    set_description(portal.newsitem)
    set_text(portal.newsitem)
    publish(portal.newsitem)
    portal.newsitem.reindexObject()

    # Collection
    portal.invokeFactory('Collection', id='collection', title='Collection')
    set_description(portal.collection)
    set_text(portal.collection)
    publish(portal.collection)
    portal.collection.reindexObject()

    # Folder
    portal.invokeFactory('Folder', id='folder', title='Folder')
    set_description(portal.folder)
    publish(portal.folder)

    # Folder with 10 Items
    portal.invokeFactory(
        'Folder',
        id='folder-with-10-items',
        title='Folder 10'
    )
    folder10 = portal['folder-with-10-items']
    set_description(folder10)
    publish(folder10)
    for i in range(1, 11):
        folder10.invokeFactory(
            'Document',
            id='doc{}'.format(i),
            title='Doc {}'.format(i)
        )
        publish(folder10['doc{}'.format(i)])

    # Folder with 100 Items
    portal.invokeFactory(
        'Folder',
        id='folder-with-100-items',
        title='Folder 100'
    )
    folder100 = portal['folder-with-100-items']
    set_description(folder100)
    publish(folder100)
    for i in range(1, 101):
        folder100.invokeFactory(
            'Document',
            id='doc{}'.format(i),
            title='Doc {}'.format(i)
        )
        publish(folder100['doc{}'.format(i)])

    # Folder with 1000 Items
    portal.invokeFactory(
        'Folder',
        id='folder-with-1000-items',
        title='Folder 1000'
    )
    folder1000 = portal['folder-with-1000-items']
    set_description(folder1000)
    publish(folder1000)
    for i in range(1, 1001):
        folder1000.invokeFactory(
            'Document',
            id='doc{}'.format(i),
            title='Doc {}'.format(i)
        )
        publish(folder1000['doc{}'.format(i)])

    # Event
    portal.invokeFactory('Event', id='event', title='Event')
    set_description(portal.event)
    publish(portal.event)

    # Link
    portal.invokeFactory('Link', id='link', title='Link')
    set_description(portal.link)
    portal.link.remoteUrl = 'http://plone.org'
    publish(portal.link)

    # Image
    portal.invokeFactory('Image', id='image', title='Image')
    set_description(portal.image)
    set_image(portal.image)

    # File
    portal.invokeFactory('File', id='file', title='File')
    set_description(portal.file)
    set_file(portal.file)
