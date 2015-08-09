# Copyright 2015 Huawei.
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

import sys,os
import logging

from django import http
from django import template
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import tables
from horizon import messages
from horizon import workflows
from horizon import exceptions

from openstack_dashboard.api import base
from openstack_dashboard.api import congress
from openstack_dashboard.dashboards.admin.policy import tables \
    as policy_tables
from openstack_dashboard.dashboards.admin.policy import forms \
    as policy_forms
from openstack_dashboard.dashboards.admin.policy import workflows \
    as policy_workflows
from openstack_dashboard.dashboards.admin.flavors import forms \
    as project_forms
from openstack_dashboard.dashboards.admin.policy import objects \
    as policy_objects
from openstack_dashboard.dashboards.admin.policy import utils \
    as policy_utils

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = policy_tables.RuleTable 
    template_name = 'admin/policy/index.html'
    page_title = _("Policy")

    def get_data(self):
        policy = policy_utils.PolicyUI_Model()
        db = policy.PolicyUI_gets()
        rule_list = []
        for rid,i in enumerate(db):
            rule_list.append({u'id':rid,u'rule_id':i.name,'policy_name':i.objects,
                'description':i.vi_condition,'datalog':i.actions,'results':i.data})
        olist = [base.APIDictWrapper(i) for i in rule_list]
        return olist

class CreateView(workflows.WorkflowView):
    workflow_class = policy_workflows.CreateRule 
    page_title = _("Create Rule")
    template_name = 'admin/policy/create_rule.html'

class CreateObject(workflows.WorkflowView):
    workflow_class = policy_workflows.CreateObject
    page_title = _("Create Object")
    template_name = 'admin/policy/create_object.html'


def get_attr_list(request):
    response = http.HttpResponse(content_type='text/plain')
    object_list = request.GET.get('mesg',"").split(',')
    attr_list = policy_objects.get_object_attr(request, object_list)
    data = ""
    for name, lst in attr_list:
        for attr in lst:
            data += (name+"_"+attr+",")
    response.write(data)
    return response
