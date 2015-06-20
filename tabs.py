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
        context = {}
        return context

class PolicyOverviewTabs(tabs.TabGroup):
    slug = "policy_overview"
    tabs = (PoliciesTab,PoliciesListTab)
    sticky = True
