# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Before request processing for JSON Body enforcement

import flask
from werkzeug import exceptions as werkzeug_exceptions

from keystone import exception
from keystone.i18n import _


def json_body_before_request():
    """Enforce JSON Request Body."""
    # TODO(morgan): Allow other content-types when OpenAPI Doc or improved
    # federation is implemented for known/valid paths. This function should
    # be removed long term.

    # exit if there is nothing to be done, (no body)
    if not flask.request.get_data():
        return None

    try:
        # flask does loading for us for json, use the flask default loader
        # in the case that the data is *not* json or a dict, we should see a
        # raise of werkzeug.exceptions.BadRequest, re-spin this to the keystone
        # ValidationError message (as expected by our contract)

        # Explicitly check if the content is supposed to be json.
        if (flask.request.is_json
                or flask.request.headers['Content-Type'] == ''):
            json_decoded = flask.request.get_json(force=True)
            if not isinstance(json_decoded, dict):
                # In the case that the returned value was not a dict, force
                # a raise that will be caught the same way that a Decode error
                # would be handled.
                raise werkzeug_exceptions.BadRequest(
                    _('resulting JSON load was not a dict'))
        else:
            raise exception.ValidationError(attribute='application/json',
                                            target='Content-Type header')

    except werkzeug_exceptions.BadRequest:
        raise exception.ValidationError(attribute='valid JSON',
                                        target='request body')
