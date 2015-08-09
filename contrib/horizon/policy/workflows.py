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

from django import template
from django import http
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms 
from horizon import messages
from horizon import workflows
from horizon import exceptions

from openstack_dashboard.api import congress
from openstack_dashboard.dashboards.admin.policy import models \
    as policy_models
from openstack_dashboard.dashboards.admin.policy import objects \
    as policy_objects
from openstack_dashboard.dashboards.admin.policy import datalog \
    as policy_dl
from openstack_dashboard.dashboards.admin.policy import utils \
    as policy_utils
LOG = logging.getLogger(__name__)

POLICY_URL = "horizon:admin:policies:create"


class CreateRuleInfoAction(workflows.Action):

    policy_name = forms.CharField(
        label=_('Policy Name'),
        max_length=255,
        initial='',
        required=False,
        add_item_link=TEST_URL)
    rule_name = forms.CharField(
        label=_('Rule Name'),
        max_length=255,
        initial='',
        required=False)
    comment = forms.CharField(
        label=_("Rule Comment"),
        initial='',
        widget=forms.Textarea(attrs={'row':'4'}),
        required=False)

    class Meta(object):
        name = _("Rule Information")
        help_text = _('Infomation about the rule and policy table'
                      ' being created.')

    def clean(self):
        cleaned_data = super(CreateRuleInfoAction, self).clean()
        policy_name = cleaned_data.get('policy_name')
        rule_name = cleaned_data.get('rule_name')

        return cleaned_data


class CreateRuleInfo(workflows.Step):
    action_class = CreateRuleInfoAction
    contributes = ("policy_name",
                   "rule_name",
                   "comment")



class ObjectSelectAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(ObjectSelectAction, self).__init__(request,
                                                 *args,
                                                 **kwargs)
        err_msg = _('Unable to retrieve objects list. '
                    'Please try again later.')
        context = args[0]

        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)

        # Get list of available projects.
        all_objects = []
        try:
            all_objects = policy_models.get_object_list(request)
        except Exception:
            exceptions.handle(request, err_msg)

        objects_list = [(obj_name,obj_name)
                        for obj_id, (obj_name, j, k) in enumerate(all_objects)]
        self.fields[field_name].choices = objects_list
        self.fields[field_name].initial = objects_list

    class Meta(object):
        name = _("Object Select")
        slug = "object_select"


class ObjectSelect(workflows.UpdateMembersStep):
    action_class = ObjectSelectAction
    help_text = _("Select the objects where the rule will be used. If no "
                  "objects are selected, then the rule will be created successfully "
                  "in policy.")
    available_list_title = _("All Objects")
    members_list_title = _("Selected Objects")
    no_available_text = _("No objects found.")
    no_members_text = _("No projects selected. ")
    show_roles = False
    contributes = ("objects_list",)


    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['objects_list'] = data.get(member_field_name, [])
        return context

class CreateConditionsAction(workflows.Action):
    def __init__(self, request, *args, **kwargs):
        super(CreateConditionsAction, self).__init__(request,
                                                 *args,
                                                 **kwargs)

    conditions = forms.CharField(
        label=_('Conditions'),
        max_length=255,
        initial='',
        required=False)
    values = forms.CharField(
        label=_('Values'),
        max_length=255,
        initial='',
        required=False)

    class Meta(object):
        name = _("Conditons Information")

class CreateConditions(workflows.Step):
    action_class = CreateConditionsAction
    contributes = ("conditions","values")
    template_name = "admin/policy/_create_output.html"
    depends_on = ("objects_list",)
    global val
    global attr

    def render(self):
        global attr
        global val
        # Overriding parent method to add extra template context variables.
        step_template = template.loader.get_template(self.template_name)
        extra_context = {"form": self.action,
                         "step": self}
        context = template.RequestContext(self.workflow.request, extra_context)
        conditions = self.workflow.request.POST.get('conditions', '')
        columns_list = conditions.split(',')
        context['condition_columns_list'] = columns_list
        context['condition_columns_count'] = len(columns_list)
        value = self.workflow.request.POST.get('values', '')
        value_list = value.split(',')
        context['value_columns_list'] = value_list
        context['value_columns_count'] = len(value_list)

        symbols = [(i,j) for i,j in policy_dl.condition_type.items()]
        context['symbols'] = symbols

        get = self.workflow.request.GET
        if get.get('f'):
            attr = get.get('attr', '')
            val = get.get('val', '')
        return step_template.render(context)
        
    def contribute(self, data, context):
        global attr
        global val
        get = self.workflow.request.GET
        context['conditions'] = attr
        context['values'] = val
        return context

class CreateRule(workflows.Workflow):
    slug = "create_rule"
    name = _("Create Rule")
    finalize_button_name = _("Create")
    success_message = _('Created new rule "%s".')
    failure_message = _('Unable to create rule "%s".')
    success_url = "horizon:admin:policy:index"
    default_steps = (CreateRuleInfo,
                     ObjectSelect,
                     CreateConditions)
    wizard = True
    fullscreen = False

    def format_status_message(self, message):
        return message % self.context['rule_name']

    def handle(self, request, data):
        content = []
        objects_list = data.get('objects_list', '')
        content.append(objects_list)
        conditions = data.get('conditions', '')
        content.append(conditions)
        values = data.get('values','')
        content.append(values)
        rule_name = data.get('rule_name') or 'auto'
        content.append(rule_name)

        rule_string = policy_dl.monitor_datalog(request, content)
        rule_id = data.get('rule_name','')
        policy_name = data.get('policy_name','')
        comment = data.get('comment','')
        rule_db = policy_utils.PolicyUI_Model()
        rule_db.PolicyUI_Add(rule_id,policy_name,comment,rule_string,'a','b','c')

        return True


class CreateObjectInfoAction(workflows.Action):

    object_name = forms.CharField(
        label=_('Object Name'),
        max_length=255,
        initial='',)
    comment = forms.CharField(
        label=_("Comment"),
        initial='',
        widget=forms.Textarea(attrs={'row':'4'}),
        required=False)

    class Meta(object):
        name = _("Object Information")
        help_text = _('Infomation about the object name and comment.')

    def clean(self):
        cleaned_data = super(CreateObjectInfoAction, self).clean()
        object_name = cleaned_data.get('object_name')
        return cleaned_data


class CreateObjectInfo(workflows.Step):
    action_class = CreateObjectInfoAction
    contributes = ("object_name",
                   "comment")

class CreateObject(workflows.Workflow):
    slug = "create_object"
    name = _("Create Object")
    finalize_button_name = _("Create")
    success_message = _('Created new object "%s".')
    failure_message = _('Unable to create object "%s".')
    success_url = "horizon:admin:policy:index"
    default_steps = (CreateObjectInfo,)

    wizard = True
    fullscreen = False

    def format_status_message(self, message):
        return message % self.context['object_name']

