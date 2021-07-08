from datetime import datetime
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.file import NamedBlobImage
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite

import os
import pytz


LOREMIPSUM_HTML_10_PARAGRAPHS = """<p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p><p>Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.</p><p>Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.</p><p>Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p><p>Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.</p><p>At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, At accusam aliquyam diam diam dolore dolores duo eirmod eos erat, et nonumy sed tempor et et invidunt justo labore Stet clita ea et gubergren, kasd magna no rebum. sanctus sea sed takimata ut vero voluptua. est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.</p><p>Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus.</p><p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p><p>Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.</p><p>Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi."""  # noqa

LOREMIPSUM_TEXT_PARAGRAPH = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum."  # noqa


def set_description(obj):
    if IDexterityContent.providedBy(obj):
        obj.description = LOREMIPSUM_TEXT_PARAGRAPH
    else:
        obj.setDescription(LOREMIPSUM_TEXT_PARAGRAPH)


def set_text(obj):
    if IDexterityContent.providedBy(obj):
        obj.text = RichTextValue(
            LOREMIPSUM_HTML_10_PARAGRAPHS, "text/html", "text/x-html-safe"
        )
    else:
        obj.setText(LOREMIPSUM_HTML_10_PARAGRAPHS)


def set_image(obj):
    if IDexterityContent.providedBy(obj):
        from plone.namedfile.file import NamedBlobImage

        filename = os.path.join(os.path.dirname(__file__), "image.png")
        obj.image = NamedBlobImage(data=open(filename, "rb").read(), filename=filename)
    else:
        filename = os.path.join(os.path.dirname(__file__), "image.png")
        obj.setImage(open(filename, "rb").read())


def set_file(obj):
    if IDexterityContent.providedBy(obj):
        from plone.namedfile.file import NamedBlobFile

        filename = os.path.join(os.path.dirname(__file__), "file.pdf")
        obj.file = NamedBlobFile(
            data=open(filename, "rb").read(),
            filename=filename,
            contentType="application/pdf",
        )
    else:
        filename = os.path.join(os.path.dirname(__file__), "file.pdf")
        obj.setFile(open(filename, "rb").read())


def publish(content):
    """Publish the object if it hasn't been published."""
    portal_workflow = getToolByName(getSite(), "portal_workflow")
    if portal_workflow.getInfoFor(content, "review_state") != "published":
        portal_workflow.doActionFor(content, "publish")
        return True
    return False


def step_setup_content(context):
    marker_file = "plone.restapi_performance_testing.txt"
    if context.readDataFile(marker_file) is None:
        return
    portal = getSite()

    # Testfolder WRITE
    portal.invokeFactory("Folder", id="testfolder-write", title="Testfolder Write")
    publish(portal["testfolder-write"])

    # Testfolder READ
    portal.invokeFactory("Folder", id="testfolder-read", title="Testfolder Read")
    publish(portal["testfolder-read"])
    portal = portal["testfolder-read"]

    # Document
    portal.invokeFactory("Document", id="document", title="Document")
    portal.document.description = LOREMIPSUM_TEXT_PARAGRAPH
    set_description(portal.document)
    set_text(portal.document)
    publish(portal.document)
    portal.document.reindexObject()

    # News Item
    portal.invokeFactory("News Item", id="newsitem", title="NewsItem")
    set_description(portal.newsitem)
    set_text(portal.newsitem)
    set_image(portal.newsitem)
    publish(portal.newsitem)
    portal.newsitem.reindexObject()

    # Folder
    portal.invokeFactory("Folder", id="folder", title="Folder")
    set_description(portal.folder)
    publish(portal.folder)

    # Folder with 10 Items
    portal.invokeFactory("Folder", id="folder-with-10-items", title="Folder 10")
    folder10 = portal["folder-with-10-items"]
    set_description(folder10)
    publish(folder10)
    for i in range(1, 11):
        folder10.invokeFactory("Document", id=f"doc{i}", title=f"Doc {i}")
        publish(folder10[f"doc{i}"])

    # Folder with 100 Items
    portal.invokeFactory("Folder", id="folder-with-100-items", title="Folder 100")
    folder100 = portal["folder-with-100-items"]
    set_description(folder100)
    publish(folder100)
    for i in range(1, 101):
        folder100.invokeFactory("Document", id=f"doc{i}", title=f"Doc {i}")
        publish(folder100[f"doc{i}"])

    # Folder with 1000 Items
    portal.invokeFactory("Folder", id="folder-with-1000-items", title="Folder 1000")
    folder1000 = portal["folder-with-1000-items"]
    set_description(folder1000)
    publish(folder1000)
    for i in range(1, 1001):
        folder1000.invokeFactory("Document", id=f"doc{i}", title=f"Doc {i}")
        publish(folder1000[f"doc{i}"])

    # Folder with 10 Items and next/previous enabled
    portal.invokeFactory(
        "Folder",
        id="folder-with-10-items-next-prev-enabled",
        title="Folder 10 (next/prev enabled)",
    )
    folder10np = portal["folder-with-10-items-next-prev-enabled"]
    folder10np.nextPreviousEnabled = True
    set_description(folder10np)
    publish(folder10np)
    for i in range(1, 11):
        folder10np.invokeFactory("Document", id=f"doc{i}", title=f"Doc {i}")
        publish(folder10np[f"doc{i}"])

    # Collection
    portal.invokeFactory("Collection", id="collection", title="Collection")
    set_description(portal.collection)
    set_text(portal.collection)
    publish(portal.collection)
    portal.collection.reindexObject()

    # Collection with Items
    portal.invokeFactory(
        "Collection", id="collectionitems", title="Collection with Items"
    )
    set_description(portal.collectionitems)
    set_text(portal.collectionitems)
    if IDexterityContent.providedBy(portal.collectionitems):
        portal.collectionitems.query = [
            {
                "i": "Type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            }
        ]
    publish(portal.collectionitems)
    portal.collectionitems.reindexObject()

    # Event
    portal.invokeFactory("Event", id="event", title="Event")
    set_description(portal.event)
    publish(portal.event)
    if IDexterityContent.providedBy(portal.event):
        portal.event.timezone = "Europe/Vienna"
        tz = pytz.timezone("Europe/Vienna")
        portal.event.start = tz.localize(datetime(2010, 10, 10, 12, 12))
        portal.event.end = tz.localize(datetime(2010, 10, 10, 13, 13))

    # Link
    portal.invokeFactory("Link", id="link", title="Link")
    set_description(portal.link)
    portal.link.remoteUrl = "http://plone.org"
    publish(portal.link)

    # Image
    portal.invokeFactory("Image", id="image", title="Image")
    set_description(portal.image)
    set_image(portal.image)

    # File
    portal.invokeFactory("File", id="file", title="File")
    set_description(portal.file)
    set_file(portal.file)

    # Image 1 MB
    portal.invokeFactory("Image", id="image-1mb", title="Image 1 MB")
    filename = os.path.join(os.path.dirname(__file__), "images", "image-1mb.jpg")
    portal.get("image-1mb").image = NamedBlobImage(
        data=open(filename, "rb").read(), filename=filename
    )

    # Image 2 MB
    portal.invokeFactory("Image", id="image-2mb", title="Image 2 MB")
    filename = os.path.join(os.path.dirname(__file__), "images", "image-2mb.jpg")
    portal.get("image-2mb").image = NamedBlobImage(
        data=open(filename, "rb").read(), filename=filename
    )

    # Image 3 MB
    portal.invokeFactory("Image", id="image-3mb", title="Image 3 MB")
    filename = os.path.join(os.path.dirname(__file__), "images", "image-3mb.jpg")
    portal.get("image-3mb").image = NamedBlobImage(
        data=open(filename, "rb").read(), filename=filename
    )

    # Image 10 MB
    portal.invokeFactory("Image", id="image-10mb", title="Image 10 MB")
    filename = os.path.join(os.path.dirname(__file__), "images", "image-10mb.jpg")
    portal.get("image-10mb").image = NamedBlobImage(
        data=open(filename, "rb").read(), filename=filename
    )

    # Volto Page with images and news items
    portal.invokeFactory("Folder", id="volto-page", title="Volto Page")
    volto_page = portal.get("volto-page")
    publish(volto_page)

    for i in range(1, 31):
        volto_page.invokeFactory("News Item", id=f"newsitem{i}", title=f"NewsItem {i}")
        newsitem = volto_page.get(f"newsitem{i}")
        set_description(newsitem)
        set_text(newsitem)
        image_file = os.path.join(os.path.dirname(__file__), "image.jpeg")
        with open(image_file, "rb") as f:
            image_data = f.read()
        newsitem.image = NamedBlobImage(
            data=image_data, contentType="image/jpeg", filename="image.jpeg"
        )
        publish(newsitem)
        newsitem.reindexObject()

    for i in range(1, 31):
        volto_page.invokeFactory("Image", id=f"image{i}", title=f"Image {i}")
        image_file = os.path.join(os.path.dirname(__file__), "image.jpeg")
        with open(image_file, "rb") as f:
            image_data = f.read()
        volto_page.get(f"image{i}").image = NamedBlobImage(
            data=image_data, contentType="image/jpeg", filename="image.jpeg"
        )

    # Volto
    # portal.invokeFactory("Document", id="volto", title="Volto")
    # portal.volto.description = LOREMIPSUM_TEXT_PARAGRAPH
    volto_page.blocks = {
        "0d57ccc7-8ceb-4b8f-bf95-5919eb859925": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "4q33c",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "2172b929-70de-416b-b345-b98916a9726f": {
            "@type": "image",
            "alt": "jamie-street-PzGiZBpv72Y-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/jamie-street-pzgizbpv72y-unsplash.jpg",
        },
        "23dd130c-d90e-48d8-ab5a-9fb85a2136a4": {
            "@type": "image",
            "alt": "anastasia-petrova-xu2WYJek5AI-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/anastasia-petrova-xu2wyjek5ai-unsplash.jpg",
        },
        "23e99d38-da30-441b-8713-bbbad4344a85": {
            "@type": "image",
            "alt": "matt-artz-oSly6rQh7YA-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/matt-artz-osly6rqh7ya-unsplash.jpg",
        },
        "24b5b799-d755-4e43-97f5-e240d6b3b7df": {
            "@type": "image",
            "alt": "christopher-windus-ys_PVhkEC6c-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/christopher-windus-ys_pvhkec6c-unsplash.jpg",
        },
        "28b1c856-4ecd-4c43-bce5-9be127f29a34": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "c0mrv",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "2e005fdb-a109-4148-b78c-855dab1e83a9": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "b6u11",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "367aacb2-8124-43ce-8989-c9394b71ba97": {
            "@type": "image",
            "alt": "hector-j-rivas-QNc9tTNHRyI-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/hector-j-rivas-qnc9ttnhryi-unsplash.jpg",
        },
        "374bcb3f-d6c7-4ec0-9a26-aa9ee148a22a": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "6o8vv",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "38076104-d93a-4e25-b2b6-7917be41dd48": {
            "@type": "image",
            "alt": "jukan-tateisi-bJhT_8nbUA0-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/jukan-tateisi-bjht_8nbua0-unsplash.jpg",
        },
        "4664c4dc-89a2-4dd0-9267-ab4ff65af757": {
            "@type": "image",
            "alt": "max-kukurudziak-MedRVIJX2P0-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/max-kukurudziak-medrvijx2p0-unsplash.jpg",
        },
        "4b07582a-771a-4ce9-92bf-456e33134dd3": {
            "@type": "image",
            "alt": "daniel-cheung-cPF2nlWcMY4-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/daniel-cheung-cpf2nlwcmy4-unsplash.jpg",
        },
        "5c4e9474-0ccb-45a4-a91d-5eba411e43ef": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "98gs2",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "6ab1e289-f46a-495f-b07d-6967c436e369": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "f0er1",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "7471143d-70da-493c-b3c5-56a021407bed": {"@type": "title"},
        "7550e1c3-03b9-432a-bdd1-2d2f33ef6d68": {
            "@type": "image",
            "alt": "clem-onojeghuo-RfAEjh_J6e0-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/clem-onojeghuo-rfaejh_j6e0-unsplash.jpg",
        },
        "828b9212-2b98-4192-92bd-ac6acc08b01f": {
            "@type": "image",
            "alt": "daniel-von-appen-tb4heMa-ZRo-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/daniel-von-appen-tb4hema-zro-unsplash.jpg",
        },
        "82b244cc-25fd-41c7-91bd-d8aea6540b61": {
            "@type": "image",
            "alt": "cristina-gottardi-Pl8ZMtFiyi8-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/cristina-gottardi-pl8zmtfiyi8-unsplash.jpg",
        },
        "976bea21-fe53-477f-b1a8-47fd51d88492": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "3m6c5",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "9d1f39db-dfe5-4315-9306-1be2738e0068": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "4q22n",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "a1fafe33-f85f-46fa-919a-19111a8bde52": {
            "@type": "image",
            "alt": "doug-linstedt-q07oPCdhPlw-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/doug-linstedt-q07opcdhplw-unsplash.jpg",
        },
        "c513539d-3b75-4f36-baa3-7145324f79ff": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "1l2bg",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "cce67a5b-3dae-4e78-9352-7ccb24bb16a5": {
            "@type": "image",
            "alt": "christian-regg-jOicNGJIwZA-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/christian-regg-joicngjiwza-unsplash.jpg",
        },
        "d43abdc7-29c4-4cae-b3ed-443c87c449cd": {
            "@type": "text",
            "text": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "8iog5",
                        "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. ",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
        },
        "dc517784-5cfc-4cf8-8fad-15fd154cd43a": {
            "@type": "image",
            "alt": "john-barkiple-l090uFWoPaI-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/john-barkiple-l090ufwopai-unsplash.jpg",
        },
        "e44ec113-a62d-4913-89d0-ba8d7e50d248": {
            "@type": "image",
            "alt": "denny-muller-jLjfAWwHdB8-unsplash.jpg",
            "url": "http://localhost:8080/Plone/page/denny-muller-jljfawwhdb8-unsplash.jpg",
        },
    }
    volto_page.blocks_layout = {
        "items": [
            "7471143d-70da-493c-b3c5-56a021407bed",
            "7550e1c3-03b9-432a-bdd1-2d2f33ef6d68",
            "23dd130c-d90e-48d8-ab5a-9fb85a2136a4",
            "cce67a5b-3dae-4e78-9352-7ccb24bb16a5",
            "24b5b799-d755-4e43-97f5-e240d6b3b7df",
            "82b244cc-25fd-41c7-91bd-d8aea6540b61",
            "4b07582a-771a-4ce9-92bf-456e33134dd3",
            "828b9212-2b98-4192-92bd-ac6acc08b01f",
            "e44ec113-a62d-4913-89d0-ba8d7e50d248",
            "a1fafe33-f85f-46fa-919a-19111a8bde52",
            "367aacb2-8124-43ce-8989-c9394b71ba97",
            "2172b929-70de-416b-b345-b98916a9726f",
            "dc517784-5cfc-4cf8-8fad-15fd154cd43a",
            "38076104-d93a-4e25-b2b6-7917be41dd48",
            "23e99d38-da30-441b-8713-bbbad4344a85",
            "4664c4dc-89a2-4dd0-9267-ab4ff65af757",
            "374bcb3f-d6c7-4ec0-9a26-aa9ee148a22a",
            "c513539d-3b75-4f36-baa3-7145324f79ff",
            "28b1c856-4ecd-4c43-bce5-9be127f29a34",
            "6ab1e289-f46a-495f-b07d-6967c436e369",
            "2e005fdb-a109-4148-b78c-855dab1e83a9",
            "d43abdc7-29c4-4cae-b3ed-443c87c449cd",
            "5c4e9474-0ccb-45a4-a91d-5eba411e43ef",
            "976bea21-fe53-477f-b1a8-47fd51d88492",
            "9d1f39db-dfe5-4315-9306-1be2738e0068",
            "0d57ccc7-8ceb-4b8f-bf95-5919eb859925",
        ]
    }
    publish(volto_page)
    volto_page.reindexObject()

    # # add images
    # from os import listdir
    # from os.path import isfile, join

    # currentdir = os.path.dirname(__file__)
    # base_image_path = os.path.join(currentdir, "performance")
    # filenames = [
    #     f for f in listdir(base_image_path) if isfile(join(base_image_path, f))
    # ]
    # for filename in filenames:
    #     imagepath = os.path.join(base_image_path, filename)
    #     volto_page.invokeFactory("Image", id=filename, title=filename)
    #     import sys
    #     import pdb

    #     for attr in ("stdin", "stdout", "stderr"):
    #         setattr(sys, attr, getattr(sys, "__%s__" % attr))
    #     pdb.set_trace()
    #     portal.volto[filename].image = NamedBlobImage(
    #         data=open(filename, "r").read(),
    #         filename=imagepath,
    #         contentType="image/jpeg",
    #     )
