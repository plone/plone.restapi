# -*- coding: utf-8 -*-
from datetime import datetime
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IMutableUUID

import json
import os
import transaction
import unittest2 as unittest


REQUEST_HEADER_KEYS = [
    'accept'
]

RESPONSE_HEADER_KEYS = [
    'content-type',
    'allow',
]

base_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    '..',
    '..',
    'docs/source/_json'
)


def save_response_for_documentation(filename, response):
    f = open('{}/{}'.format(base_path, filename), 'w')
    f.write('{} {}\n'.format(
        response.request.method,
        response.request.path_url
    ))
    for key, value in response.request.headers.items():
        if key.lower() in REQUEST_HEADER_KEYS:
            f.write('{}: {}\n'.format(key, value))
    f.write('\n')
    f.write('HTTP {} {}\n'.format(response.status_code, response.reason))
    for key, value in response.headers.items():
        if key.lower() in RESPONSE_HEADER_KEYS:
            f.write('{}: {}\n'.format(key.lower(), value))
    f.write('\n')
    f.write(response.content)
    f.close()


class TestTraversal(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document', id='front-page')
        self.document = self.portal['front-page']
        self.document.title = u"Welcome to Plone"
        self.document.description = \
            u"Congratulations! You have successfully installed Plone."
        self.document.text = RichTextValue(
            u"If you're seeing this instead of the web site you were " +
            u"expecting, the owner of this web site has just installed " +
            u"Plone. Do not contact the Plone Team or the Plone mailing " +
            u"lists about this.",
            'text/plain',
            'text/html'
        )
        self.document.creation_date = DateTime('2016-01-21T01:14:48+00:00')
        IMutableUUID(self.document).set('1f699ffa110e45afb1ba502f75f7ec33')
        self.document.reindexObject()
        self.document.modification_date = DateTime('2016-01-21T01:24:11+00:00')
        import transaction
        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_documentation_document(self):
        response = self.api_session.get(self.document.absolute_url())
        save_response_for_documentation('document.json', response)

    def test_documentation_news_item(self):
        self.portal.invokeFactory('News Item', id='newsitem')
        self.portal.newsitem.title = 'My News Item'
        self.portal.newsitem.description = u'This is a news item'
        self.portal.newsitem.text = RichTextValue(
            u"Lorem ipsum",
            'text/plain',
            'text/html'
        )
        image_file = os.path.join(os.path.dirname(__file__), u'image.png')
        self.portal.newsitem.image = NamedBlobImage(
            data=open(image_file, 'r').read(),
            contentType='image/png',
            filename=u'image.png'
        )
        self.portal.newsitem.image_caption = u'This is an image caption.'
        self.portal.newsitem.creation_date = DateTime(
            '2016-01-21T02:14:48+00:00')
        self.portal.newsitem.modification_date = DateTime(
            '2016-01-21T02:24:11+00:00')
        IMutableUUID(self.portal.newsitem).set(
            '80c2a074cb4240d08c9a129e3a834c74')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.newsitem.absolute_url())
        save_response_for_documentation('newsitem.json', response)

    def test_documentation_event(self):
        self.portal.invokeFactory('Event', id='event')
        self.portal.event.title = 'Event'
        self.portal.event.description = u'This is an event'
        self.portal.event.start = datetime(2013, 1, 1, 10, 0)
        self.portal.event.end = datetime(2013, 1, 1, 12, 0)
        self.portal.event.creation_date = DateTime('2016-01-21T03:14:48+00:00')
        self.portal.event.modification_date = DateTime(
            '2016-01-21T03:24:11+00:00')
        IMutableUUID(self.portal.event).set('846d632bc0854c5aa6d3dcae171ed2db')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.event.absolute_url())
        save_response_for_documentation('event.json', response)

    def test_documentation_link(self):
        self.portal.invokeFactory('Link', id='link')
        self.portal.link.title = 'My Link'
        self.portal.link.description = u'This is a link'
        self.portal.remoteUrl = 'http://plone.org'
        self.portal.link.creation_date = DateTime('2016-01-21T04:14:48+00:00')
        self.portal.link.modification_date = DateTime(
            '2016-01-21T04:24:11+00:00')
        IMutableUUID(self.portal.link).set('6ff48d27762143a0ae8d63cee73d9fc2')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.link.absolute_url())
        save_response_for_documentation('link.json', response)

    def test_documentation_file(self):
        self.portal.invokeFactory('File', id='file')
        self.portal.file.title = 'My File'
        self.portal.file.description = u'This is a file'
        pdf_file = os.path.join(
            os.path.dirname(__file__), u'file.pdf'
        )
        self.portal.file.file = NamedBlobFile(
            data=open(pdf_file, 'r').read(),
            contentType='application/pdf',
            filename=u'file.pdf'
        )
        self.portal.file.creation_date = DateTime('2016-01-21T05:14:48+00:00')
        self.portal.file.modification_date = DateTime(
            '2016-01-21T05:24:11+00:00')
        IMutableUUID(self.portal.file).set('9b6a4eadb9074dde97d86171bb332ae9')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.file.absolute_url())
        save_response_for_documentation('file.json', response)

    def test_documentation_image(self):
        self.portal.invokeFactory('Image', id='image')
        self.portal.image.title = 'My Image'
        self.portal.image.description = u'This is an image'
        image_file = os.path.join(os.path.dirname(__file__), u'image.png')
        self.portal.image.image = NamedBlobImage(
            data=open(image_file, 'r').read(),
            contentType='image/png',
            filename=u'image.png'
        )
        self.portal.image.creation_date = DateTime('2016-01-21T06:14:48+00:00')
        self.portal.image.modification_date = DateTime(
            '2016-01-21T06:24:11+00:00')
        IMutableUUID(self.portal.image).set('2166e81a0c224fe3b62e197c7fdc9c3e')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.image.absolute_url())
        save_response_for_documentation('image.json', response)

    def test_documentation_folder(self):
        self.portal.invokeFactory('Folder', id='folder')
        self.portal.folder.title = 'My Folder'
        self.portal.folder.description = u'This is a folder with two documents'
        self.portal.folder.invokeFactory(
            'Document',
            id='doc1',
            title='A document within a folder'
        )
        self.portal.folder.invokeFactory(
            'Document',
            id='doc2',
            title='A document within a folder'
        )
        self.portal.folder.creation_date = DateTime(
            '2016-01-21T07:14:48+00:00')
        self.portal.folder.modification_date = DateTime(
            '2016-01-21T07:24:11+00:00')
        IMutableUUID(self.portal.folder).set(
            'fc7881c46d61452db4177bc059d9dcb5')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.folder.absolute_url())
        save_response_for_documentation('folder.json', response)

    def test_documentation_collection(self):
        self.portal.invokeFactory('Collection', id='collection')
        self.portal.collection.title = 'My Collection'
        self.portal.collection.description = \
            u'This is a collection with two documents'
        self.portal.collection.query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Document',
        }]
        self.portal.invokeFactory(
            'Document',
            id='doc1',
            title='Document 1'
        )
        self.portal.invokeFactory(
            'Document',
            id='doc2',
            title='Document 2'
        )
        self.portal.collection.creation_date = DateTime(
            '2016-01-21T08:14:48+00:00')
        self.portal.collection.modification_date = DateTime(
            '2016-01-21T08:24:11+00:00')
        IMutableUUID(self.portal.collection).set(
            'd0c89bc77f874ce1aad5720921d875c0')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.collection.absolute_url())
        save_response_for_documentation('collection.json', response)

    def test_documentation_siteroot(self):
        response = self.api_session.get(self.portal.absolute_url())
        save_response_for_documentation('siteroot.json', response)

    def test_documentation_404_not_found(self):
        response = self.api_session.get('non-existing-resource')
        save_response_for_documentation('404_not_found.json', response)

    def test_documentation_search(self):
        query = {'sort_on': 'path'}
        response = self.api_session.get('/@search', params=query)
        save_response_for_documentation('search.json', response)

    def test_documentation_workflow(self):
        response = self.api_session.get(
            '{}/@workflow'.format(self.document.absolute_url()))
        save_response_for_documentation('workflow_get.json', response)

    def test_documentation_workflow_transition(self):
        response = self.api_session.post(
            '{}/@workflow/publish'.format(self.document.absolute_url()))
        save_response_for_documentation('workflow_post.json', response)

    def test_documentation_registry_get(self):
        response = self.api_session.get(
            '/@registry/plone.app.querystring.field.path.title')
        save_response_for_documentation('registry_get.json', response)

    def test_documentation_registry_update(self):
        response = self.api_session.patch(
            '/@registry/',
            json={'plone.app.querystring.field.path.title': 'Value'})
        save_response_for_documentation('registry_update.json', response)

    def test_documentation_types(self):
        response = self.api_session.get('/@types')
        save_response_for_documentation('types.json', response)

    def test_documentation_types_document(self):
        response = self.api_session.get('@types/Document')
        save_response_for_documentation('types_document.json', response)

    def test_documentation_login(self):
        self.portal.acl_users.jwt_auth._secret = 'secret'
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        import transaction
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            '{}/@login'.format(self.portal.absolute_url()),
            json={'login': SITE_OWNER_NAME, 'password': SITE_OWNER_PASSWORD})
        save_response_for_documentation('login.json', response)

    def test_documentation_login_renew(self):
        self.portal.acl_users.jwt_auth._secret = 'secret'
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        import transaction
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            '{}/@login'.format(self.portal.absolute_url()),
            json={'login': SITE_OWNER_NAME, 'password': SITE_OWNER_PASSWORD})
        token = json.loads(response.content)['token']
        response = self.api_session.post(
            '{}/@login-renew'.format(self.portal.absolute_url()),
            headers={'Authorization': 'Bearer {}'.format(token)})
        save_response_for_documentation('login_renew.json', response)

    def test_documentation_logout(self):
        self.portal.acl_users.jwt_auth._secret = 'secret'
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        self.portal.acl_users.jwt_auth.store_tokens = True
        import transaction
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            '{}/@login'.format(self.portal.absolute_url()),
            json={'login': SITE_OWNER_NAME, 'password': SITE_OWNER_PASSWORD})
        token = json.loads(response.content)['token']
        response = self.api_session.post(
            '{}/@logout'.format(self.portal.absolute_url()),
            headers={'Authorization': 'Bearer {}'.format(token)})
        save_response_for_documentation('logout.json', response)

    def test_documentation_batching(self):
        folder = self.portal[self.portal.invokeFactory(
            'Folder',
            id='folder',
            title='Folder'
        )]
        for i in range(7):
            folder.invokeFactory(
                'Document',
                id='doc-%s' % str(i + 1),
                title='Document %s' % str(i + 1)
            )
        transaction.commit()

        query = {'sort_on': 'path'}
        response = self.api_session.get(
            '/folder/@search?b_size=5', params=query)
        save_response_for_documentation('batching.json', response)
