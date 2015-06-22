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

from django import http
from django import template

from horizon import tabs
from horizon import messages
from horizon import exceptions
from openstack_dashboard.api import congress
from openstack_dashboard.dashboards.admin.policy import tabs as policy_tabs

import PolicyUI_Model
import objects as objs
import datalog as dl
import logging
import sys,os

LOG = logging.getLogger(__name__)

class IndexView(tabs.TabbedTableView):
    tab_group_class = policy_tabs.PolicyOverviewTabs
    template_name = 'admin/policy/index.html'


#according the message sended by UI to create datalog
def generate_rule(request):
    #get user's input message on UI
    rules_string = request.GET.get('msg')
    response = http.HttpResponse(content_type='text/plain')

    rules_list = rules_string.split("@@")

    for mesg in rules_list:
        if not mesg:
            continue
        rule_string = mesg 
        mesg = mesg.split("&")
        # generate violation datalog (only monitoring avaliable now)
        datalog = dl.monitor_datalog(request, mesg)
        
        # db operator
        results = congress.policy_rows_list(request, "classification", mesg[3])
        result = ""
        for item in results:
               result += str(item['data'])+","
         
        policy = PolicyUI_Model.PolicyUI_Model()
        policy.PolicyUI_Add(mesg[3], mesg[0], mesg[1], mesg[4], mesg[2], datalog, result)
   
    response.write("")
    response.flush()                                                    
    return response

def show_results(request):

    policy_name = "classification"
    table_name = "error"
    results = ""
    datas=""
    try:
        policy=PolicyUI_Model.PolicyUI_Model() 
        obj=policy.PolicyUI_gets()
        for o in obj:
            datas+=o.name+"&"+o.objects+"&"+o.vi_condition+"&"+o.actions+"&"+o.data+"&"+o.datalog+"&"+o.result+"@@"
    except Exception as e:
        msg = ('Unable to get results: %s') % e.message
#        messages.error(request, msg)

    response = http.HttpResponse(content_type='text/plain')
    response.write(datas)
    response.flush()
    return response    

def get_objects(request):

    active_object = objs.__object__(request)

    try:
        policy_name = "classification"
        policies = congress.policy_rules_list(request, policy_name)
    except Exception as e:
        messages.error(request, e.message)

    head = ""
    body = ""
    for i,(obj_name, obj_attr) in enumerate(active_object):
        try:
    	    head += obj_name + ","
            body += obj_name + ":"
            for j, attr in enumerate(obj_attr):
                body += attr + ","
            body += ";"
        except Exception as e:
            LOG.error("get_objects error : %s" % e.message)

    data = head + "&" + body

    response = http.HttpResponse(content_type='text/plain')
    response.write(data)
    response.flush()
    return response    

