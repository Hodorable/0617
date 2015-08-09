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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages
from horizon import exceptions

from openstack_dashboard.api import congress


LOG = logging.getLogger(__name__)


class CreateRule(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Rule Name")) 
    description = forms.CharField(label=_("Description"), required=False,
                                  widget=forms.Textarea(attrs={'rows':'4'}))
    failure_url = 'horizon:admin:policy:index'

    def handle(self, request, data):
        rule_name = data['name']
        rule_description = data.get('description')
        redirect = reverse(self.failure_url)
        raise exceptions.Http302(redirect)
        return None
