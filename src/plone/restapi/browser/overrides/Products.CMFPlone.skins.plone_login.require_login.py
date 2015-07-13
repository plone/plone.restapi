## Script (Python) "require_login"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Login

# plone.restapi customization START
request = context.REQUEST

if request.getHeader('Accept') == 'application/json':
    request.response.setHeader('Content-Type', 'application/json')
    request.response.setStatus(401)
    import json
    return json.dumps(
        {
            'type': 'Unauthorized',
            'message': 'You are not authorized to access this resource.',
        },
        indent=2,
        sort_keys=True
    )
# plone.restapi customization END

login = 'login'

portal = context.portal_url.getPortalObject()
# if cookie crumbler did a traverse instead of a redirect,
# this would be the way to get the value of came_from
#url = portal.getCurrentUrl()
#context.REQUEST.set('came_from', url)

if context.portal_membership.isAnonymousUser():
    return portal.restrictedTraverse(login)()
else:
    return portal.restrictedTraverse('insufficient_privileges')()
