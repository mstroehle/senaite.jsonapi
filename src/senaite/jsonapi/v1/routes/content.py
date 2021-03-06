# -*- coding: utf-8 -*-

from senaite.jsonapi import api
from senaite.jsonapi.v1 import add_route
from senaite.jsonapi.exceptions import APIError

ACTIONS = "create,update,delete"


# /<resource (portal_type)>
@add_route("/<string:resource>",
           "senaite.jsonapi.v1.get", methods=["GET"])
#
# /<resource (portal_type)>/<uid>
@add_route("/<string:resource>/<string(maxlength=32):uid>",
           "senaite.jsonapi.v1.get", methods=["GET"])
@add_route("/<string:resource>/<string(length=32):uid>",
           "senaite.jsonapi.v1.get", methods=["GET"])
@add_route("/<string(length=32):uid>",
           "senaite.jsonapi.v1.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """GET
    """

    # We have a UID, return the record
    if uid and not resource:
        return api.get_record(uid)

    # we have a UID as resource, return the record
    if api.is_uid(resource):
        return api.get_record(resource)

    portal_type = api.resource_to_portal_type(resource)
    if portal_type is None:
        raise APIError(404, "Not Found")

    return api.get_batched(portal_type=portal_type, uid=uid, endpoint="senaite.jsonapi.v1.get")


# http://werkzeug.pocoo.org/docs/0.11/routing/#builtin-converters
# http://werkzeug.pocoo.org/docs/0.11/routing/#custom-converters
@add_route("/<any(" + ACTIONS + "):action>",
           "senaite.jsonapi.v1.action", methods=["POST"])
@add_route("/<string:resource>",
           "senaite.jsonapi.v1.action", methods=["POST"])
@add_route("/<string:resource>/<string(maxlength=32):uid>",
           "senaite.jsonapi.v1.action", methods=["POST"])
@add_route("/<any(" + ACTIONS + "):action>/<string(maxlength=32):uid>",
           "senaite.jsonapi.v1.action", methods=["POST"])
@add_route("/<string(length=32):uid>",
           "senaite.jsonapi.v1.action", methods=["POST"])
@add_route("/<string:resource>/<any(" + ACTIONS + "):action>",
           "senaite.jsonapi.v1.action", methods=["POST"])
@add_route("/<string:resource>/<any(" + ACTIONS + "):action>/<string(maxlength=32):uid>",
           "senaite.jsonapi.v1.action", methods=["POST"])
def action(context, request, action=None, resource=None, uid=None):
    """Various HTTP POST actions
    """

    # allow to set the method via the header
    if action is None:
        action = request.get_header("HTTP_X_HTTP_METHOD_OVERRIDE", "CREATE").lower()

    # Fetch and call the action function of the API
    func_name = "{}_items".format(action)
    action_func = getattr(api, func_name, None)
    if action_func is None:
        api.fail(500, "API has no member named '{}'".format(func_name))

    portal_type = api.resource_to_portal_type(resource)
    items = action_func(portal_type=portal_type, uid=uid)

    return {
        "count": len(items),
        "items": items,
        "url": api.url_for("senaite.jsonapi.v1.action", action=action),
    }


@add_route("/search",
           "senaite.jsonapi.v1.search", methods=["GET"])
def search(context, request):
    """Generic search add_route

    <Plonesite>/@@API/v2/search -> returns all contents of the portal
    <Plonesite>/@@API/v2/search?portal_type=Folder -> returns only folders
    ...
    """
    return api.get_batched()
