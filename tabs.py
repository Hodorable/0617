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

from django.utils.translation import ugettext_lazy as _  # noqa
from horizon import tabs
from horizon import messages
from openstack_dashboard.api import congress

import logging

LOG = logging.getLogger(__name__)

class PoliciesTab(tabs.Tab):
    name = _("Policies")
    slug = "Policies"
    template_name = ("admin/policy/policies.html")
    #preload = False

    def get_context_data(self, request):
        context = {'policy': 'tests'}
        return context



class PoliciesListTab(tabs.Tab):
    name = _("Policies lists")
    slug = "policies_lists"
    template_name = ("admin/policy/policies_list.html")
    #preload = False

    def get_context_data(self, request):
        policies = ""
	results = ""
	policy_name = "classification"
	table_name = "error"
        try:
    	    #policies = congress.policies_list(request)
    	    #policies = congress.policy_get(request, "classification")
	    #policies = congress.policy_rules_list(request, policy_name)
	    #policies = congress.policy_tables_list(request, policy_name)
	    results = congress.policy_rows_list(request, policy_name, table_name)
        except Exception as e:
    	    msg = ('Unable to get policies list: %s') % e.message
    	    messages.error(self.request, msg)
###    	policies=str(policies)
###	policies=policies.replace("[<PolicyAPIDictWrapper: ","")
###	policies=policies.replace(">]","")
###	policies=policies.split(">, <PolicyAPIDictWrapper: ")
###	data=""
###	for policy in policies:
###	    dicPolicy=eval(policy)
###	    data+=dicPolicy['name']+','+dicPolicy['description']+','+dicPolicy['kind']+','+dicPolicy['owner_id']+'&'
	

	data = ""
	for item in results:
		data += str(item['data'])
		#LOG.error('***************: %s\n' % policy['rule'])
	LOG.error('********************** tables ************************: %s' % data)


        context = {'table_name':"test", 'results':data}
        return context

class PolicyOverviewTabs(tabs.TabGroup):
    slug = "policy_overview"
    tabs = (PoliciesTab,PoliciesListTab)
    sticky = True
