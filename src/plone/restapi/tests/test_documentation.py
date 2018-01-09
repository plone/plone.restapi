# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime
from DateTime import DateTime
from datetime import timedelta
from freezegun import freeze_time
from pkg_resources import parse_version
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.testing import applyProfile
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.locking.interfaces import ITTWLockable
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PAM_INSTALLED
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import register_static_uuid_utility
from plone.restapi.testing import RelativeSession
from plone.testing.z2 import Browser
from zope.component import createObject
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.site.hooks import getSite

import collections
import json
import re
import os
import transaction
import unittest

if PAM_INSTALLED:
    from plone.app.multilingual.interfaces import ITranslationManager


TUS_HEADERS = [
    'upload-offset',
    'upload-length',
    'upload-metadata',
    'tus-version',
    'tus-resumable',
    'tus-extension',
    'tus-max-size',

]

REQUEST_HEADER_KEYS = [
    'accept',
    'authorization',
    'lock-token',
    'prefer',
] + TUS_HEADERS

RESPONSE_HEADER_KEYS = [
    'content-type',
    'allow',
    'location',
] + TUS_HEADERS

base_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    '..',
    '..',
    'docs/source/_json'
)

UPLOAD_DATA = 'abcdefgh'
UPLOAD_MIMETYPE = 'text/plain'
UPLOAD_FILENAME = 'test.txt'
UPLOAD_LENGTH = len(UPLOAD_DATA)

UPLOAD_PDF_MIMETYPE = 'application/pdf'
UPLOAD_PDF_FILENAME = 'file.pdf'

PLONE_VERSION = parse_version(api.env.plone_version())

try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE5 = False
else:
    PLONE5 = True


def pretty_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


def save_request_and_response_for_docs(name, response):
    with open('{}/{}'.format(base_path, '%s.req' % name), 'w') as req:
        req.write('{} {} HTTP/1.1\n'.format(
            response.request.method,
            response.request.path_url
        ))
        ordered_request_headers = collections.OrderedDict(
            sorted(response.request.headers.items())
        )
        for key, value in ordered_request_headers.items():
            if key.lower() in REQUEST_HEADER_KEYS:
                req.write('{}: {}\n'.format(key.title(), value))
        if response.request.body:
            # If request has a body, make sure to set Content-Type header
            if 'content-type' not in REQUEST_HEADER_KEYS:
                content_type = response.request.headers['Content-Type']
                req.write('Content-Type: %s\n' % content_type)

            req.write('\n')

            # Pretty print JSON request body
            if content_type == 'application/json':
                json_body = json.loads(response.request.body)
                body = pretty_json(json_body)
                # Make sure Content-Length gets updated, just in case we
                # ever decide to dump that header
                response.request.prepare_body(data=body, files=None)

            req.write(response.request.body)

    with open('{}/{}'.format(base_path, '%s.resp' % name), 'w') as resp:
        status = response.status_code
        reason = response.reason
        resp.write('HTTP/1.1 {} {}\n'.format(status, reason))
        for key, value in response.headers.items():
            if key.lower() in RESPONSE_HEADER_KEYS:
                resp.write('{}: {}\n'.format(key.title(), value))
        resp.write('\n')
        resp.write(response.content)


class TestDocumentation(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        if PLONE_VERSION.base_version >= '5.1':
            self.skipTest('Do not run documentation tests for Plone 5')
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        # Register custom UUID generator to produce stable UUIDs during tests
        pushGlobalRegistry(getSite())
        register_static_uuid_utility(prefix='SomeUUID')

        self.time_freezer = freeze_time("2016-10-21 19:00:00")
        self.frozen_time = self.time_freezer.start()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = self.create_document()
        alsoProvides(self.document, ITTWLockable)

        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def create_document(self):
        self.portal.invokeFactory('Document', id='front-page')
        document = self.portal['front-page']
        document.title = u"Welcome to Plone"
        document.description = \
            u"Congratulations! You have successfully installed Plone."
        document.text = RichTextValue(
            u"If you're seeing this instead of the web site you were " +
            u"expecting, the owner of this web site has just installed " +
            u"Plone. Do not contact the Plone Team or the Plone mailing " +
            u"lists about this.",
            'text/plain',
            'text/html'
        )
        document.creation_date = DateTime('2016-01-21T01:14:48+00:00')
        document.reindexObject()
        document.modification_date = DateTime('2016-01-21T01:24:11+00:00')
        return document

    def create_folder(self):
        self.portal.invokeFactory('Folder', id='folder')
        folder = self.portal['folder']
        folder.title = 'My Folder'
        folder.description = u'This is a folder with two documents'
        folder.invokeFactory(
            'Document',
            id='doc1',
            title='A document within a folder'
        )
        folder.invokeFactory(
            'Document',
            id='doc2',
            title='A document within a folder'
        )
        folder.creation_date = DateTime(
            '2016-01-21T07:14:48+00:00')
        folder.modification_date = DateTime(
            '2016-01-21T07:24:11+00:00')
        return folder

    def tearDown(self):
        self.time_freezer.stop()
        popGlobalRegistry(getSite())

    def test_documentation_content_crud(self):
        folder = self.create_folder()
        transaction.commit()

        response = self.api_session.post(
            folder.absolute_url(),
            json={
                '@type': 'Document',
                'title': 'My Document',
            }
        )
        save_request_and_response_for_docs('content_post', response)

        transaction.commit()
        document = folder['my-document']
        response = self.api_session.get(document.absolute_url())
        save_request_and_response_for_docs('content_get', response)

        response = self.api_session.patch(
            document.absolute_url(),
            json={
                'title': 'My New Document Title',
            }
        )
        save_request_and_response_for_docs('content_patch', response)

        response = self.api_session.patch(
            document.absolute_url(),
            headers={'Prefer': 'return=representation'},
            json={
                'title': 'My New Document Title',
            }
        )
        save_request_and_response_for_docs(
            'content_patch_representation',
            response
        )

        transaction.commit()
        response = self.api_session.delete(document.absolute_url())
        save_request_and_response_for_docs('content_delete', response)

    def test_documentation_document(self):
        response = self.api_session.get(self.document.absolute_url())
        save_request_and_response_for_docs('document', response)

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
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.newsitem.absolute_url())
        save_request_and_response_for_docs('newsitem', response)

    def test_documentation_event(self):
        self.portal.invokeFactory('Event', id='event')
        self.portal.event.title = 'Event'
        self.portal.event.description = u'This is an event'
        self.portal.event.start = datetime(2013, 1, 1, 10, 0)
        self.portal.event.end = datetime(2013, 1, 1, 12, 0)
        self.portal.event.creation_date = DateTime('2016-01-21T03:14:48+00:00')
        self.portal.event.modification_date = DateTime(
            '2016-01-21T03:24:11+00:00')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.event.absolute_url())
        save_request_and_response_for_docs('event', response)

    def test_documentation_link(self):
        self.portal.invokeFactory('Link', id='link')
        self.portal.link.title = 'My Link'
        self.portal.link.description = u'This is a link'
        self.portal.remoteUrl = 'http://plone.org'
        self.portal.link.creation_date = DateTime('2016-01-21T04:14:48+00:00')
        self.portal.link.modification_date = DateTime(
            '2016-01-21T04:24:11+00:00')
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.link.absolute_url())
        save_request_and_response_for_docs('link', response)

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
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.file.absolute_url())
        save_request_and_response_for_docs('file', response)

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
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.image.absolute_url())
        save_request_and_response_for_docs('image', response)

    def test_documentation_folder(self):
        folder = self.create_folder()
        import transaction
        transaction.commit()
        response = self.api_session.get(folder.absolute_url())
        save_request_and_response_for_docs('folder', response)

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
        import transaction
        transaction.commit()
        response = self.api_session.get(self.portal.collection.absolute_url())
        save_request_and_response_for_docs('collection', response)

    def test_documentation_siteroot(self):
        response = self.api_session.get(self.portal.absolute_url())
        save_request_and_response_for_docs('siteroot', response)

    def test_documentation_404_not_found(self):
        response = self.api_session.get('non-existing-resource')
        save_request_and_response_for_docs('404_not_found', response)

    def test_documentation_search(self):
        query = {'sort_on': 'path'}
        response = self.api_session.get('/@search', params=query)
        save_request_and_response_for_docs('search', response)

    def test_documentation_workflow(self):
        response = self.api_session.get(
            '{}/@workflow'.format(self.document.absolute_url()))
        save_request_and_response_for_docs('workflow_get', response)

    def test_documentation_workflow_transition(self):
        self.frozen_time.tick(timedelta(minutes=5))
        response = self.api_session.post(
            '{}/@workflow/publish'.format(self.document.absolute_url()))
        save_request_and_response_for_docs('workflow_post', response)

    def test_documentation_registry_get(self):
        response = self.api_session.get(
            '/@registry/plone.app.querystring.field.path.title')
        save_request_and_response_for_docs('registry_get', response)

    def test_documentation_registry_update(self):
        response = self.api_session.patch(
            '/@registry/',
            json={'plone.app.querystring.field.path.title': 'Value'})
        save_request_and_response_for_docs('registry_update', response)

    def test_documentation_registry_get_list(self):
        response = self.api_session.get('/@registry')
        save_request_and_response_for_docs('registry_get_list', response)

    def test_documentation_types(self):
        response = self.api_session.get('/@types')
        save_request_and_response_for_docs('types', response)

    def test_documentation_types_document(self):
        response = self.api_session.get('@types/Document')
        save_request_and_response_for_docs('types_document', response)

    def test_documentation_jwt_login(self):
        self.portal.acl_users.jwt_auth._secret = 'secret'
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        import transaction
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            '{}/@login'.format(self.portal.absolute_url()),
            json={'login': SITE_OWNER_NAME, 'password': SITE_OWNER_PASSWORD})
        save_request_and_response_for_docs('jwt_login', response)

    def test_documentation_jwt_logged_in(self):
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
        response = self.api_session.get(
            '/',
            headers={'Authorization': 'Bearer {}'.format(token)})
        save_request_and_response_for_docs('jwt_logged_in', response)

    def test_documentation_jwt_login_renew(self):
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
        save_request_and_response_for_docs('jwt_login_renew', response)

    def test_documentation_jwt_logout(self):
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
        save_request_and_response_for_docs('jwt_logout', response)

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
        save_request_and_response_for_docs('batching', response)

    def test_documentation_users(self):
        test_user = api.user.get(username=TEST_USER_ID)
        properties = {
            "description": "This is a test user",
            "email": "test@example.com",
            "fullname": "Test User",
            "home_page": "http://www.example.com",
            "location": "Bonn",
            "username": "test-user"
        }
        test_user.setMemberProperties(mapping=properties)
        admin = api.user.get(username='admin')
        properties = {
            "description": "This is an admin user",
            "email": "admin@example.com",
            "fullname": "Administrator",
            "home_page": "http://www.example.com",
            "location": "Berlin",
            "username": "admin"
        }
        admin.setMemberProperties(mapping=properties)
        transaction.commit()
        response = self.api_session.get('/@users')
        save_request_and_response_for_docs('users', response)

    def test_documentation_users_as_anonymous(self):
        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({'Accept': 'application/json'})

        response = logged_out_api_session.get('@users')
        save_request_and_response_for_docs('users_anonymous', response)
        self.assertEqual(response.status_code, 401)

    def test_documentations_users_as_unauthorized_user(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            password='password',
            properties=properties
        )
        transaction.commit()

        standard_api_session = RelativeSession(self.portal_url)
        standard_api_session.headers.update({'Accept': 'application/json'})
        standard_api_session.auth = ('noam', 'password')

        response = standard_api_session.get('@users')
        save_request_and_response_for_docs('users_unauthorized', response)
        self.assertEqual(response.status_code, 401)

    def test_documentation_users_get(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )
        transaction.commit()
        response = self.api_session.get('@users/noam')
        save_request_and_response_for_docs('users_get', response)

    def test_documentation_users_anonymous_get(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )
        transaction.commit()

        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({'Accept': 'application/json'})

        response = logged_out_api_session.get('@users/noam')
        save_request_and_response_for_docs('users_anonymous_get', response)

    def test_documentation_users_unauthorized_get(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            password='secret',
            properties=properties
        )

        api.user.create(
            email='noam.chomsky@example.com',
            username='noam-fake',
            password='secret',
            properties=properties
        )

        transaction.commit()

        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({'Accept': 'application/json'})
        logged_out_api_session.auth = ('noam-fake', 'secret')

        response = logged_out_api_session.get('@users/noam')
        save_request_and_response_for_docs('users_unauthorized_get', response)

    def test_documentation_users_authorized_get(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            password='secret',
            properties=properties
        )
        transaction.commit()

        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({'Accept': 'application/json'})
        logged_out_api_session.auth = ('noam', 'secret')
        response = logged_out_api_session.get('@users/noam')
        save_request_and_response_for_docs('users_authorized_get', response)

    def test_documentation_users_filtered_get(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )
        transaction.commit()
        response = self.api_session.get('@users', params={'query': 'noa'})
        save_request_and_response_for_docs('users_filtered_by_username', response)  # noqa

    def test_documentation_users_created(self):
        response = self.api_session.post(
            '/@users',
            json={
                'email': 'noam.chomsky@example.com',
                'password': 'colorlessgreenideas',
                'username': 'noamchomsky',
                'fullname': 'Noam Avram Chomsky',
                'home_page': 'web.mit.edu/chomsky',
                'description': 'Professor of Linguistics',
                'location': 'Cambridge, MA',
                'roles': ['Contributor', ],
            },
        )
        save_request_and_response_for_docs('users_created', response)

    def test_documentation_users_update(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )
        transaction.commit()

        response = self.api_session.patch(
            '/@users/noam',
            json={
                'email': 'avram.chomsky@example.com',
                'roles': {'Contributor': False, },
            },
        )
        save_request_and_response_for_docs('users_update', response)

    def test_documentation_users_delete(self):
        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )
        transaction.commit()

        response = self.api_session.delete(
            '/@users/noam')
        save_request_and_response_for_docs('users_delete', response)

    def test_documentation_groups(self):
        gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        gtool.addGroup('ploneteam', (), (),
                       properties=properties,
                       title=properties['title'],
                       description=properties['description'])
        transaction.commit()
        response = self.api_session.get('/@groups')
        save_request_and_response_for_docs('groups', response)

    def test_documentation_groups_get(self):
        gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        gtool.addGroup('ploneteam', (), (),
                       properties=properties,
                       title=properties['title'],
                       description=properties['description'])
        transaction.commit()
        response = self.api_session.get('@groups/ploneteam')
        save_request_and_response_for_docs('groups_get', response)

    def test_documentation_groups_filtered_get(self):
        gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        gtool.addGroup('ploneteam', (), (),
                       properties=properties,
                       title=properties['title'],
                       description=properties['description'])
        transaction.commit()
        response = self.api_session.get('@groups', params={'query': 'plo'})
        save_request_and_response_for_docs('groups_filtered_by_groupname', response)  # noqa

    def test_documentation_groups_created(self):
        response = self.api_session.post(
            '/@groups',
            json={
                'groupname': 'fwt',
                'email': 'fwt@plone.org',
                'title': 'Framework Team',
                'description': 'The Plone Framework Team',
                'roles': ['Manager'],
                'groups': ['Administrators'],
                'users': [SITE_OWNER_NAME, TEST_USER_ID]
            },
        )
        save_request_and_response_for_docs('groups_created', response)

    def test_documentation_groups_update(self):
        gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        gtool.addGroup('ploneteam', (), (),
                       properties=properties,
                       title=properties['title'],
                       description=properties['description'])
        transaction.commit()

        response = self.api_session.patch(
            '/@groups/ploneteam',
            json={
                'email': 'ploneteam2@plone.org',
                'users': {TEST_USER_ID: False}
            },
        )
        save_request_and_response_for_docs('groups_update', response)

    def test_documentation_groups_delete(self):
        gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        gtool.addGroup('ploneteam', (), (),
                       properties=properties,
                       title=properties['title'],
                       description=properties['description'])
        transaction.commit()

        response = self.api_session.delete(
            '/@groups/ploneteam')
        save_request_and_response_for_docs('groups_delete', response)

    def test_documentation_breadcrumbs(self):
        response = self.api_session.get(
            '{}/@breadcrumbs'.format(self.document.absolute_url()))
        save_request_and_response_for_docs('breadcrumbs', response)

    def test_documentation_navigation(self):
        response = self.api_session.get(
            '{}/@navigation'.format(self.document.absolute_url()))
        save_request_and_response_for_docs('navigation', response)

    def test_documentation_principals(self):
        gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        gtool.addGroup('ploneteam', (), (),
                       properties=properties,
                       title=properties['title'],
                       description=properties['description'])
        transaction.commit()
        response = self.api_session.get(
            '/@principals',
            params={
                "search": "ploneteam"
            }
        )
        save_request_and_response_for_docs('principals', response)

    def test_documentation_copy(self):
        response = self.api_session.post(
            '/@copy',
            json={
                'source': self.document.absolute_url(),
            },
        )
        save_request_and_response_for_docs('copy', response)

    def test_documentation_copy_multiple(self):
        newsitem = self.portal[self.portal.invokeFactory(
            'News Item', id='newsitem')]
        newsitem.title = 'My News Item'
        transaction.commit()

        response = self.api_session.post(
            '/@copy',
            json={
                'source': [
                    self.document.absolute_url(),
                    newsitem.absolute_url(),
                ],
            },
        )
        save_request_and_response_for_docs('copy_multiple', response)

    def test_documentation_move(self):
        self.portal.invokeFactory('Folder', id='folder')
        transaction.commit()
        response = self.api_session.post(
            '/folder/@move',
            json={
                'source': self.document.absolute_url(),
            },
        )
        save_request_and_response_for_docs('move', response)

    def test_documentation_vocabularies_all(self):
        response = self.api_session.get('/@vocabularies')
        save_request_and_response_for_docs('vocabularies', response)

    def test_documentation_vocabularies_get(self):
        response = self.api_session.get(
            '/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes'
        )
        save_request_and_response_for_docs('vocabularies_get', response)

    def test_documentation_sharing_folder_get(self):
        self.portal.invokeFactory('Folder', id='folder')
        transaction.commit()
        response = self.api_session.get(
            '/folder/@sharing'
        )
        save_request_and_response_for_docs('sharing_folder_get', response)

    def test_documentation_sharing_folder_post(self):
        self.portal.invokeFactory('Folder', id='folder')
        transaction.commit()
        payload = {
            "inherit": True,
            "entries": [
                {
                    "id": "test_user_1_",
                    "roles": {
                        "Reviewer": True,
                        "Editor": False,
                        "Reader": True,
                        "Contributor": False
                    },
                    "type": "user"
                }
            ]
        }
        response = self.api_session.post(
            '/folder/@sharing',
            json=payload
        )
        save_request_and_response_for_docs('sharing_folder_post', response)

    def test_documentation_sharing_search(self):
        self.portal.invokeFactory('Folder', id='folder')
        self.portal.folder.invokeFactory('Document', id='doc')
        api.user.grant_roles('admin', roles=['Contributor'])
        api.user.grant_roles(
            'admin', roles=['Editor'], obj=self.portal.folder
        )
        transaction.commit()
        response = self.api_session.get(
            '/folder/doc/@sharing?search=admin'
        )
        save_request_and_response_for_docs('sharing_search', response)

    def test_documentation_expansion(self):
        response = self.api_session.get(
            '/front-page'
        )
        save_request_and_response_for_docs('expansion', response)

    def test_documentation_expansion_expanded(self):
        response = self.api_session.get(
            '/front-page?expand=breadcrumbs'
        )
        save_request_and_response_for_docs('expansion_expanded', response)

    def test_documentation_expansion_expanded_full(self):
        response = self.api_session.get(
            '/front-page?expand=breadcrumbs,navigation,schema,workflow'
        )
        save_request_and_response_for_docs('expansion_expanded_full', response)

    def test_history_get(self):
        self.document.setTitle('My new title')
        url = '{}/@history'.format(self.document.absolute_url())
        response = self.api_session.get(url)
        save_request_and_response_for_docs('history_get', response)

    def test_history_revert(self):
        url = '{}/@history'.format(self.document.absolute_url())
        response = self.api_session.patch(url, json={'version': 0})
        save_request_and_response_for_docs('history_revert', response)

    def test_tusupload_options(self):
        self.portal.invokeFactory('Folder', id='folder')
        transaction.commit()
        response = self.api_session.options('/folder/@tus-upload')
        save_request_and_response_for_docs('tusupload_options', response)

    def test_tusupload_post_head_patch(self):
        # We create both the POST and PATCH example here, because we need the
        # temporary id

        def clean_upload_url(response, _id='032803b64ad746b3ab46d9223ea3d90f'):
            pattern = r'@tus-upload/(\w+)'
            repl = '@tus-upload/' + _id

            # Replaces the dynamic part in the headers with a stable id
            for target in [response, response.request]:
                for key, val in target.headers.items():
                    target.headers[key] = re.sub(pattern, repl, val)

                target.url = re.sub(pattern, repl, target.url)

        def clean_final_url(response, _id='document-2016-10-21'):
            url = self.portal.folder.absolute_url() + '/' + _id
            response.headers['Location'] = url

        self.portal.invokeFactory('Folder', id='folder')
        transaction.commit()

        # POST create an upload
        metadata = 'filename {},content-type {}'.format(
            b64encode(UPLOAD_FILENAME),
            b64encode(UPLOAD_MIMETYPE)
        )
        response = self.api_session.post(
            '/folder/@tus-upload',
            headers={'Tus-Resumable': '1.0.0',
                     'Upload-Length': str(UPLOAD_LENGTH),
                     'Upload-Metadata': metadata}
        )

        upload_url = response.headers['location']

        clean_upload_url(response)
        save_request_and_response_for_docs('tusupload_post', response)

        # PATCH upload a partial document
        response = self.api_session.patch(
            upload_url,
            headers={'Tus-Resumable': '1.0.0',
                     'Content-Type': 'application/offset+octet-stream',
                     'Upload-Offset': '0'},
            data=UPLOAD_DATA[:3]
        )
        clean_upload_url(response)
        save_request_and_response_for_docs('tusupload_patch', response)

        # HEAD ask for much the server has
        response = self.api_session.head(
            upload_url,
            headers={'Tus-Resumable': '1.0.0'}
        )
        clean_upload_url(response)
        save_request_and_response_for_docs('tusupload_head', response)

        # Finalize the upload
        response = self.api_session.patch(
            upload_url,
            headers={'Tus-Resumable': '1.0.0',
                     'Content-Type': 'application/offset+octet-stream',
                     'Upload-Offset': response.headers['Upload-Offset']},
            data=UPLOAD_DATA[3:]
        )
        clean_upload_url(response)
        clean_final_url(response)
        save_request_and_response_for_docs(
            'tusupload_patch_finalized',
            response
        )

    def test_tusreplace_post_patch(self):
        self.portal.invokeFactory('File', id='myfile')
        transaction.commit()

        # POST create an upload
        metadata = 'filename {},content-type {}'.format(
            b64encode(UPLOAD_FILENAME),
            b64encode(UPLOAD_MIMETYPE)
        )
        response = self.api_session.post(
            '/myfile/@tus-replace',
            headers={'Tus-Resumable': '1.0.0',
                     'Upload-Length': str(UPLOAD_LENGTH),
                     'Upload-Metadata': metadata}
        )
        upload_url = response.headers['location']
        # Replace dynamic uuid with a static one
        response.headers['location'] = '/'.join(
            upload_url.split('/')[:-1] + ['4e465958b24a46ec8657e6f3be720991'])
        save_request_and_response_for_docs('tusreplace_post', response)

        # PATCH upload file data
        response = self.api_session.patch(
            upload_url,
            headers={'Tus-Resumable': '1.0.0',
                     'Content-Type': 'application/offset+octet-stream',
                     'Upload-Offset': '0'},
            data=UPLOAD_DATA,
        )
        # Replace dynamic uuid with a static one
        response.request.url = '/'.join(
            upload_url.split('/')[:-1] + ['4e465958b24a46ec8657e6f3be720991'])
        save_request_and_response_for_docs('tusreplace_patch', response)

    def test_locking_lock(self):
        url = '{}/@lock'.format(self.document.absolute_url())
        response = self.api_session.post(url)
        # Replace dynamic lock token with a static one
        response._content = re.sub(
            r'"token": "[^"]+"',
            '"token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"',  # noqa
            response.content)
        save_request_and_response_for_docs('lock', response)

    def test_locking_lock_nonstealable_and_timeout(self):
        url = '{}/@lock'.format(self.document.absolute_url())
        response = self.api_session.post(
            url,
            json={
                'stealable': False,
                'timeout': 3600,
            },
        )
        # Replace dynamic lock token with a static one
        response._content = re.sub(
            r'"token": "[^"]+"',
            '"token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"',  # noqa
            response.content)
        save_request_and_response_for_docs(
            'lock_nonstealable_timeout', response)

    def test_locking_unlock(self):
        url = '{}/@lock'.format(self.document.absolute_url())
        response = self.api_session.post(url)
        url = '{}/@unlock'.format(self.document.absolute_url())
        response = self.api_session.post(url)
        save_request_and_response_for_docs('unlock', response)

    def test_locking_refresh_lock(self):
        url = '{}/@lock'.format(self.document.absolute_url())
        response = self.api_session.post(url)
        url = '{}/@refresh-lock'.format(self.document.absolute_url())
        response = self.api_session.post(url)
        # Replace dynamic lock token with a static one
        response._content = re.sub(
            r'"token": "[^"]+"',
            '"token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"',  # noqa
            response.content)
        save_request_and_response_for_docs('refresh_lock', response)

    def test_locking_lockinfo(self):
        url = '{}/@lock'.format(self.document.absolute_url())
        response = self.api_session.get(url)
        save_request_and_response_for_docs('lock_get', response)

    def test_update_with_lock(self):
        url = '{}/@lock'.format(self.document.absolute_url())
        response = self.api_session.post(url)
        token = response.json()['token']
        response = self.api_session.patch(
            self.document.absolute_url(),
            headers={'Lock-Token': token},
            json={'title': 'New Title'})
        response.request.headers['Lock-Token'] = u"0.684672730996-0.25195226375-00105A989226:1477076400.000"  # noqa
        save_request_and_response_for_docs('lock_update', response)


class TestCommenting(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        if PLONE_VERSION.base_version >= '5.1':
            self.skipTest('Do not run documentation tests for Plone 5')
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        self.time_freezer = freeze_time("2016-10-21 19:00:00")
        self.frozen_time = self.time_freezer.start()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        settings.edit_comment_enabled = True
        settings.delete_own_comment_enabled = True

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = self.create_document_with_comments()

        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def tearDown(self):
        self.time_freezer.stop()

    def create_document_with_comments(self):
        self.portal.invokeFactory('Document', id='front-page')
        document = self.portal['front-page']
        document.allow_discussion = True
        document.title = u"Welcome to Plone"
        document.description = \
            u"Congratulations! You have successfully installed Plone."
        document.text = RichTextValue(
            u"If you're seeing this instead of the web site you were " +
            u"expecting, the owner of this web site has just installed " +
            u"Plone. Do not contact the Plone Team or the Plone mailing " +
            u"lists about this.",
            'text/plain',
            'text/html'
        )
        document.creation_date = DateTime('2016-01-21T01:14:48+00:00')
        document.reindexObject()
        document.modification_date = DateTime('2016-01-21T01:24:11+00:00')

        # Add a bunch of comments to the default conversation so we can do
        # batching
        self.conversation = conversation = IConversation(document)
        self.replies = replies = IReplies(conversation)
        for x in range(1, 2):
            comment = createObject('plone.Comment')
            comment.text = 'Comment %d' % x
            comment = replies[replies.addComment(comment)]

            comment_replies = IReplies(comment)
            for y in range(1, 2):
                comment = createObject('plone.Comment')
                comment.text = 'Comment %d.%d' % (x, y)
                comment_replies.addComment(comment)
        self.comment_id, self.comment = replies.items()[0]

        return document

    @staticmethod
    def clean_comment_id(response, _id='123456'):
        pattern = r'@comments/(\w+)'
        repl = '@comments/' + _id

        # Replaces the dynamic part in the headers with a stable id
        for target in [response, response.request]:
            for key, val in target.headers.items():
                target.headers[key] = re.sub(pattern, repl, val)

            target.url = re.sub(pattern, repl, target.url)

        # and the body
        if response.request.body:
            response.request.body = re.sub(
                pattern, repl, response.request.body
            )

        # and the response
        if response.content:
            response._content = re.sub(pattern, repl, response._content)

    def test_comments_get(self):
        url = '{}/@comments'.format(self.document.absolute_url())
        response = self.api_session.get(url)
        save_request_and_response_for_docs('comments_get', response)

    def test_comments_add_root(self):
        url = '{}/@comments/'.format(
            self.document.absolute_url()
        )
        payload = {'text': 'My comment'}
        response = self.api_session.post(url, json=payload)
        self.clean_comment_id(response)
        save_request_and_response_for_docs(
            'comments_add_root', response
        )

    def test_comments_add_sub(self):
        # Add a reply
        url = '{}/@comments/{}'.format(
            self.document.absolute_url(),
            self.comment_id
        )
        payload = {'text': 'My reply'}
        response = self.api_session.post(url, json=payload)

        self.clean_comment_id(response)
        save_request_and_response_for_docs(
            'comments_add_sub', response
        )

    def test_comments_update(self):
        url = '{}/@comments/{}'.format(
            self.document.absolute_url(),
            self.comment_id
        )
        payload = {'text': 'My NEW comment'}
        response = self.api_session.patch(url, json=payload)
        self.clean_comment_id(response)
        save_request_and_response_for_docs(
            'comments_update', response
        )

    def test_comments_delete(self):
        url = '{}/@comments/{}'.format(
            self.document.absolute_url(),
            self.comment_id
        )
        response = self.api_session.delete(url)
        self.clean_comment_id(response)
        save_request_and_response_for_docs(
            'comments_delete', response
        )

    def test_roles_get(self):
        url = '{}/@roles'.format(self.portal_url)
        response = self.api_session.get(url)
        save_request_and_response_for_docs('roles', response)

    def test_documentation_expansion(self):
        response = self.api_session.get(
            '/front-page?expand=breadcrumbs,workflow'
        )
        save_request_and_response_for_docs('expansion', response)

    @unittest.skipIf(not PLONE5, 'Just Plone 5 currently.')
    def test_controlpanels_get_listing(self):
        response = self.api_session.get(
            '/@controlpanels'
        )
        save_request_and_response_for_docs('controlpanels_get', response)

    @unittest.skipIf(not PLONE5, 'Just Plone 5 currently.')
    def test_controlpanels_get_item(self):
        response = self.api_session.get(
            '/@controlpanels/editing'
        )
        save_request_and_response_for_docs('controlpanels_get_item', response)


@unittest.skipUnless(PAM_INSTALLED, 'plone.app.multilingual is installed by default only in Plone 5')  # NOQA
class TestPAMDocumentation(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        if PLONE_VERSION.base_version >= '5.1':
            self.skipTest('Do not run documentation tests for Plone 5')
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        self.time_freezer = freeze_time("2016-10-21 19:00:00")
        self.frozen_time = self.time_freezer.start()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('en')
        language_tool.addSupportedLanguage('es')
        applyProfile(self.portal, 'plone.app.multilingual:default')
        en_id = self.portal['en'].invokeFactory(
            'Document',
            id='test-document',
            title='Test document'
        )
        self.en_content = self.portal['en'].get(en_id)
        es_id = self.portal['es'].invokeFactory(
            'Document',
            id='test-document',
            title='Test document'
        )
        self.es_content = self.portal['es'].get(es_id)

        import transaction
        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def tearDown(self):
        self.time_freezer.stop()

    def test_documentation_translations_post(self):
        response = self.api_session.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            json={
                'id': self.es_content.absolute_url()
            }
        )
        save_request_and_response_for_docs('translations_post', response)

    def test_documentation_translations_get(self):
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)
        transaction.commit()
        response = self.api_session.get(
            '{}/@translations'.format(self.en_content.absolute_url()))

        save_request_and_response_for_docs('translations_get', response)

    def test_documentation_translations_delete(self):
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)
        transaction.commit()
        response = self.api_session.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            json={
                "language": "es"
            })
        save_request_and_response_for_docs('translations_delete', response)
