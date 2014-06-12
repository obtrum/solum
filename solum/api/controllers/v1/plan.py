# Copyright 2013 - Rackspace US, Inc.
#
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

import pecan
from pecan import rest
import sys
import wsmeext.pecan as wsme_pecan
import yaml

from solum.api.controllers.v1.datamodel import plan
from solum.api.handlers import plan_handler
from solum.common import exception
from solum.common import yamlutils
from solum import objects


def init_plan_v1(yml_input_plan):
    plan_handler_v1 = plan_handler.PlanHandler(
        pecan.request.security_context)
    plan_v1 = plan.Plan(**yml_input_plan)
    return plan_handler_v1, plan_v1


def init_plan_by_version(yml_input_plan):
    version = yml_input_plan.get('version')
    if version is None:
        raise exception.BadRequest(
            reason='Version attribute is missing in Plan')
    mod = sys.modules[__name__]
    if not hasattr(mod, 'init_plan_v%s' % version):
        raise exception.BadRequest(reason='Plan version %s is invalid.'
                                          % version)
    return getattr(mod, 'init_plan_v%s' % version)(yml_input_plan)


class PlanController(rest.RestController):
    """Manages operations on a single plan."""

    def __init__(self, plan_id):
        super(PlanController, self).__init__()
        self._id = plan_id

    @exception.wrap_pecan_controller_exception
    @pecan.expose(content_type='application/x-yaml')
    def get(self):
        """Return this plan."""
        handler = plan_handler.PlanHandler(pecan.request.security_context)
        plan_yml = yaml.dump(handler.get(self._id).refined_content())
        pecan.response.status = 200
        return plan_yml

    @exception.wrap_pecan_controller_exception
    @pecan.expose(content_type='application/x-yaml')
    def put(self):
        """Modify this plan."""
        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest
        try:
            yml_input_plan = yamlutils.load(pecan.request.body)
        except ValueError as excp:
            raise exception.BadRequest('Plan is invalid. ' + excp.message)
        handler, data = init_plan_by_version(yml_input_plan)
        updated_plan_yml = yaml.dump(handler.update(
            self._id, data.as_dict(objects.registry.Plan)).refined_content())
        pecan.response.status = 200
        return updated_plan_yml

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(status_code=204)
    def delete(self):
        """Delete this plan."""
        handler = plan_handler.PlanHandler(pecan.request.security_context)
        handler.delete(self._id)


class PlansController(rest.RestController):
    """Manages operations on the plans collection."""

    @pecan.expose()
    def _lookup(self, plan_id, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return PlanController(plan_id), remainder

    @exception.wrap_pecan_controller_exception
    @pecan.expose(content_type='application/x-yaml')
    def post(self):
        """Create a new plan."""
        if not pecan.request.body or len(pecan.request.body) < 1:
            raise exception.BadRequest
        try:
            yml_input_plan = yamlutils.load(pecan.request.body)
        except ValueError as excp:
            raise exception.BadRequest('Plan is invalid. ' + excp.message)
        handler, data = init_plan_by_version(yml_input_plan)
        create_plan_yml = yaml.dump(handler.create(
            data.as_dict(objects.registry.Plan)).refined_content())
        pecan.response.status = 201
        return create_plan_yml

    @exception.wrap_pecan_controller_exception
    @pecan.expose(content_type='application/x-yaml')
    def get_all(self):
        """Return all plans, based on the query provided."""
        handler = plan_handler.PlanHandler(pecan.request.security_context)
        plan_yml = yaml.dump([obj.refined_content()
                              for obj in handler.get_all()
                              if obj and obj.raw_content])
        pecan.response.status = 200
        return plan_yml
