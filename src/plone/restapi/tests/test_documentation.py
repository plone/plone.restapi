# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from DateTime import DateTime
from datetime import timedelta
from freezegun import freeze_time
from plone import api
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import register_static_uuid_utility
from plone.restapi.testing import RelativeSession
from plone.restapi.testing import PAM_INSTALLED
from plone.restapi.testing import LP_INSTALLED
from plone.testing.z2 import Browser
from zope.site.hooks import getSite

import collections
import json
import os
import transaction
import unittest2 as unittest

REQUEST_HEADER_KEYS = [
    'accept',
    'authorization',
]

RESPONSE_HEADER_KEYS = [
    'content-type',
    'allow',
    'location',
]

base_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    '..',
    '..',
    'docs/source/_json'
)


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


class TestTraversal(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
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
                'location': 'Cambridge, MA'
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
                'groups': ['Administrators']
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
            '{}/@components/breadcrumbs'.format(self.document.absolute_url()))
        save_request_and_response_for_docs('breadcrumbs', response)

    def test_documentation_navigation(self):
        response = self.api_session.get(
            '{}/@components/navigation'.format(self.document.absolute_url()))
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


if PAM_INSTALLED:
    from plone.app.multilingual.interfaces import ITranslationManager
    from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    class TestPAMDocumentation(unittest.TestCase):

        layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

        def setUp(self):
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

            language_tool = getToolByName(self.portal, 'portal_languages')
            language_tool.addSupportedLanguage('en')
            language_tool.addSupportedLanguage('es')
            applyProfile(self.portal, 'plone.app.multilingual:default')
            self.en_content = createContentInContainer(
                self.portal['en'], 'Document', title='Test document')
            self.es_content = createContentInContainer(
                self.portal['es'], 'Document', title='Test document')

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


if LP_INSTALLED:
    from plone.restapi.testing import PLONE_RESTAPI_AT_LP_FUNCTIONAL_TESTING

    class TestLPDocumentation(unittest.TestCase):

        layer = PLONE_RESTAPI_AT_LP_FUNCTIONAL_TESTING

        def setUp(self):
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

            login(self.portal, SITE_OWNER_NAME)
            lsf = getMultiAdapter(
                (self.portal, self.request),
                name='language-setup-folders'
            )
            lsf()

            en_id = self.portal.en.invokeFactory(
                id='test-document',
                type_name='Document',
                title='Test document'
            )
            self.en_content = self.portal.en.get(en_id)
            es_id = self.portal.es.invokeFactory(
                id='test-document',
                type_name='Document',
                title='Test document'
            )
            self.es_content = self.portal.es.get(es_id)

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
            self.en_content.addTranslationReference(self.es_content)
            import transaction
            transaction.commit()
            response = self.api_session.get(
                '{}/@translations'.format(self.en_content.absolute_url()))

            save_request_and_response_for_docs('translations_get', response)

        def test_documentation_translations_delete(self):
            self.en_content.addTranslationReference(self.es_content)
            import transaction
            transaction.commit()
            response = self.api_session.delete(
                '{}/@translations'.format(self.en_content.absolute_url()),
                json={
                    "language": "es"
                })
            save_request_and_response_for_docs(
                'translations_delete', response)
