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
from django.template.defaultfilters import linebreaksbr
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from horizon import messages
from horizon import exceptions

from openstack_dashboard import policy
from openstack_dashboard.api import congress


LOG = logging.getLogger(__name__)


def get_policy_link(datum):
    return reverse('horizon:admin:policy:detail', args=(datum['policy'],))

class CreateRule(tables.LinkAction):
    name = 'create_rule'
    verbose_name = _('Create Rule')
    url = 'horizon:admin:policy:create'
    classes = ('ajax-modal',)
    icon = 'plus'

class CreateObject(tables.LinkAction):
    name ='create_object'
    verbose_name = _('Create Object')
    url = 'horizon:admin:policy:object'
    classes = ('ajax-modal',)
    icon = 'plus'

class DeleteRule(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u'Delete Rule',
            u'Delete Rules',
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u'Deleted Rule',
            u'Deleted Rules',
            count
        )

    def delete(self, request, policy_name, rule_id):
        #LOG.info
        try:
            congress.policy_rule_delete(request, policy_name, rule_id)
            #LOG.info
        except Exception as e:
            #messages.error()
            redirect = reverse('horizon:admin:policy:admin')
            raise exceptions.Http302(redirect)

def _format_rule(rule):
    """Make rule's text more human readable."""
    head_body = rule.split(congress.RULE_SEPARATOR)
    if len(head_body) < 2:
        return rule
    head = head_body[0]
    body = head_body[1]

    # Add newline after each literal in the body.
    body_literals = body.split(congress.LITERALS_SEPARATOR)
    literals_break = congress.LITERALS_SEPARATOR + '\n'
    new_body = literals_break.join(body_literals)

    # Add newline after the head.
    rules_break = congress.RULE_SEPARATOR + '\n'
    return rules_break.join([head, new_body])

class RuleTable(tables.DataTable):
    rule_id = tables.Column("rule_id",
                            verbose_name = _("Rule ID"))
    policy_name = tables.Column("policy_name",
                                verbose_name = _("Policy Name"))
    description = tables.Column("description",
                                verbose_name = _("Description"))
    datalog = tables.Column("datalog",
                            verbose_name = _("Datalog"),
                            filters=(linebreaksbr,))
    results = tables.Column("results",
                            verbose_name = _("Results"))

    class Meta(object):
        name = "rules"
        verbose_name = "Rules"
        table_actions = (CreateObject ,CreateRule, DeleteRule)
        row_actions = (DeleteRule,)
