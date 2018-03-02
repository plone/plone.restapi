# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl.Permissions import use_mailhost_services
from email.MIMEText import MIMEText
from plone.registry.interfaces import IRegistry
from plone.restapi import _
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from smtplib import SMTPException
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from Products.CMFPlone.interfaces import ISiteSchema

import plone


class EmailSendPost(Service):

    def reply(self):
        data = json_body(self.request)

        send_to_address = data.get('to', None)
        sender_from_address = data.get('from', None)
        message = data.get('message', None)
        sender_fullname = data.get('name', '')
        subject = data.get('subject', '')

        if not send_to_address or not sender_from_address or not message:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Missing "to", "from" or "message" parameters'))

        overview_controlpanel = getMultiAdapter((self.context, self.request),
                                                name='overview-controlpanel')
        if overview_controlpanel.mailhost_warning():
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='MailHost is not configured.'))

        sm = getSecurityManager()
        if not sm.checkPermission(use_mailhost_services, self.context):
            pm = getToolByName(self.context, 'portal_membership')
            if bool(pm.isAnonymousUser()):
                self.request.response.setStatus(401)
                error_type = 'Unauthorized'
            else:
                self.request.response.setStatus(403)
                error_type = 'Forbidden'
            return dict(error=dict(
                type=error_type,
                message=message))

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        from_address = mail_settings.email_from_address
        encoding = registry.get('plone.email_charset', 'utf-8')
        host = getToolByName(self.context, 'MailHost')
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        portal_title = site_settings.site_title

        if not subject:
            if not sender_fullname:
                subject = self.context.translate(
                    _(u'A portal user via ${portal_title}',
                      mapping={'portal_title': portal_title})
                )
            else:
                subject = self.context.translate(
                    _(u'${sender_fullname} via ${portal_title}',
                        mapping={
                            'sender_fullname': sender_fullname,
                            'portal_title': portal_title})
                )

        message_intro = self.context.translate(
            _(u'You are receiving this mail because ${sender_fullname} sent this message via the site ${portal_title}:', # noqa
              mapping={
                'sender_fullname': sender_fullname or 'a portal user',
                'portal_title': portal_title
              })
        )

        message = u'{} \n {}'.format(message_intro, message)

        message = MIMEText(message, 'plain', encoding)
        message['Reply-To'] = sender_from_address
        try:
            host.send(
                message,
                send_to_address,
                from_address,
                subject=subject,
                charset=encoding
            )

        except (SMTPException, RuntimeError):
            plone_utils = getToolByName(self.context, 'plone_utils')
            exception = plone_utils.exceptionString()
            message = 'Unable to send mail: {}'.format(exception)

            self.request.response.setStatus(500)
            return dict(error=dict(
                type='InternalServerError',
                message=message))

        self.request.response.setStatus(204)
        return
