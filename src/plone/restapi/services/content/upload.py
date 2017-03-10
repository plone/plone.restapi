# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from base64 import b64decode
from plone.rest.interfaces import ICORSPolicy
from plone.restapi.services import Service
from plone.restapi.services.content.utils import create
from plone.restapi.services.content.utils import rename
from plone.rfc822.interfaces import IPrimaryFieldInfo
from uuid import uuid4
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

import json
import os

TUS_OPTIONS_RESPONSE_HEADERS = {
    'Tus-Resumable': '1.0.0',
    'Tus-Version': '1.0.0',
    'Tus-Extension': 'creation',
}


class UploadOptions(Service):
    """TUS upload endpoint for handling OPTIONS requests without CORS."""

    def reply(self):
        for name, value in TUS_OPTIONS_RESPONSE_HEADERS.items():
                    self.request.response.setHeader(name, value)
        return super(UploadOptions, self).reply()


class UploadPost(Service):
    """TUS upload endpoint for creating a new upload resource."""

    def __call__(self):
        # We need to add additional TUS headers if this is a CORS preflight
        # request.
        policy = queryMultiAdapter((self.context, self.request), ICORSPolicy)
        if policy is not None:
            if self.request._rest_cors_preflight:
                policy.process_preflight_request()
                # Add TUS options headers in addition to CORS headers
                for name, value in TUS_OPTIONS_RESPONSE_HEADERS.items():
                    self.request.response.setHeader(name, value)
                return
            else:
                policy.process_simple_request()
                self.request.response.setHeader('Tus-Resumable', '1.0.0')

        return self.render()

    def reply(self):
        length = self.request.getHeader('Upload-Length', '')
        try:
            length = int(length)
        except ValueError:
            return {'error': {
                'type': 'Bad Request',
                'message': 'Missing or invalid Upload-Length header'
            }}

        # Parse metadata
        metadata = {}
        for item in self.request.getHeader('Upload-Metadata', '').split(','):
            key_value = item.split()
            if len(key_value) == 2:
                metadata[key_value[0].lower()] = b64decode(key_value[1])
        metadata['length'] = length

        tus_upload = TUSUpload(uuid4().hex)
        tus_upload.initalize(metadata)

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', '{}/@upload/{}'.format(
            self.context.absolute_url(), tus_upload.uid))


class UploadFileBase(Service):
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(UploadFileBase, self).__init__(context, request)
        self.uid = None

    def publishTraverse(self, request, name):
        if self.uid is None:
            self.uid = name
        else:
            raise NotFound(self, name, request)
        return self

    def check_tus_version(self):
        version = self.request.getHeader('Tus-Resumable')
        if version != '1.0.0':
            self.request.response.setHeader('Tus-Version', '1.0.0')
            self.request.response.setStatus(412)
            return False
        return True


class UploadHead(UploadFileBase):
    """TUS upload endpoint for handling HEAD requests"""

    def reply(self):

        if not self.check_tus_version():
            return dict(error=dict(
                type='Precondition Failed',
                message='Unsupported version'))

        tus_upload = TUSUpload(self.uid)

        self.request.response.setHeader('Upload-Offset', '{}'.format(
            tus_upload.offset()))
        self.request.response.setHeader('Tus-Resumable', '1.0.0')
        self.request.response.setHeader('Cache-Control', 'no-store')
        self.request.response.setStatus(200, lock=1)
        return super(UploadHead, self).reply()


class UploadPatch(UploadFileBase):
    """TUS upload endpoint for handling PATCH requests"""

    implements(IPublishTraverse)

    def reply(self):
        if self.uid is None:
            return {'error': {
                'type': 'Bad Request',
                'message': 'Missing UID'
            }}

        if not self.check_tus_version():
            return {'error': {
                'type': 'Precondition Failed',
                'message': 'Unsupported version'
            }}

        content_type = self.request.getHeader('Content-Type')
        if content_type != 'application/offset+octet-stream':
            return {'error': {
                'type': 'Bad Request',
                'message': 'Missing or invalid Content-Type header'
            }}

        offset = self.request.getHeader('Upload-Offset', '')
        try:
            offset = int(offset)
        except ValueError:
            return {'error': {
                'type': 'Bad Request',
                'message': 'Missing or invalid Upload-Offset header'
            }}

        tus_upload = TUSUpload(self.uid)
        tus_upload.write(self.request._file, offset)

        if tus_upload.finished:
            offset = tus_upload.offset()
            metadata = tus_upload.metadata()
            filename = metadata.get('filename', '')
            content_type = metadata.get('content-type',
                                        'application/octet-stream')
            ctr = getToolByName(self.context, 'content_type_registry')
            type_ = ctr.findTypeName(
                filename.lower(), content_type, '') or 'File'

            obj = create(self.context, type_)

            # Get fieldname of file object
            fieldname = metadata.get('fieldname')
            with open(tus_upload.filepath, 'rb') as f:
                if not fieldname:
                    info = IPrimaryFieldInfo(obj, None)
                    if info is not None:
                        field = info.field
                        field.set(obj,
                                  field._type(data=f,
                                              filename=filename,
                                              contentType=content_type))
                    elif base_hasattr(obj, 'getPrimaryField'):
                        field = obj.getPrimaryField()
                        mutator = field.getMutator(obj)
                        mutator(f,
                                content_type=content_type,
                                filename=filename)
                else:
                    # TODO: handle non-primary fields
                    pass

            rename(obj)
            tus_upload.cleanup()
        else:
            offset = tus_upload.offset()

        self.request.response.setHeader('Tus-Resumable', '1.0.0')
        self.request.response.setHeader('Upload-Offset', '{}'.format(offset))
        self.request.response.setStatus(204, lock=1)
        return super(UploadPatch, self).reply()


class TUSUpload(object):

    finished = False

    def __init__(self, uid):
        self.uid = uid

        tmp_dir = os.environ.get('TUS_TMP_FILE_DIR')
        if tmp_dir is None:
            client_home = os.environ.get('CLIENT_HOME')
            tmp_dir = os.path.join(client_home, 'tus-uploads')
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)

        self.filepath = os.path.join(tmp_dir, self.uid)
        self.metadata_path = self.filepath + '.json'
        self._metadata = None

    def initalize(self, metadata):
        with open(self.metadata_path, 'wb') as f:
            json.dump(metadata, f)

    def length(self):
        metadata = self.metadata()
        if 'length' in metadata:
            return metadata['length']
        return 0

    def offset(self):
        """Returns the current offset."""
        if os.path.exists(self.filepath):
            return os.path.getsize(self.filepath)
        return 0

    def write(self, infile, offset=0):
        """Write to uploaded file at the given offset."""
        mode = 'wb'
        if os.path.exists(self.filepath):
            mode = 'ab+'
        with open(self.filepath, mode) as f:
            f.seek(offset)
            while True:
                chunk = infile.read(2 << 16)
                if not chunk:
                    offset = f.tell()
                    break
                f.write(chunk)
        length = self.length()
        if length and offset >= length:
            self.finished = True

    def metadata(self):
        if self._metadata is None:
            with open(self.metadata_path, 'rb') as f:
                self._metadata = json.load(f)
        return self._metadata

    def cleanup(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)
