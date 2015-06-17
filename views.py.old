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

from openstack_dashboard.dashboards.admin.policy import objects as objs

import logging
import sys,os

LOG = logging.getLogger(__name__)

class IndexView(tabs.TabbedTableView):
    tab_group_class = policy_tabs.PolicyOverviewTabs
    template_name = 'admin/policy/index.html'

#objects means the Objects column of UI
def create_sentence_from_objects(name):
    sentence = ""
    #set the attributes fixed temporary,later we will get them from database
    if name == "servers":
	sentence += "nova:servers("
        sentence += "servers_id" + ", servers_name"
	sentence += ", servers_hID" + ", servers_status" + ", servers_tenant_id"
	sentence += ", servers_user_id" + ", servers_image" + ", servers_flavor"
	sentence += "),"
    elif name == "networks":
    	sentence += "neutronv2:networks("
    	sentence += "net_id" + ", net_tenant_id"
    	sentence += ", net_name" + ", net_status"
    	sentence += ", net_admin_state_up" + ", net_shared"
    	sentence += "),"
    return sentence

#conditions means the Violation Conditions column of UI
def create_sentence_from_conditions(lenConditions, condition, conditionIndex):
    content = condition.split(":")
    conName = content[0].lower()
    if conName == "equal(==)":
        conName = "equal"
    elif conName == "greater than(>)":
        conName = "gt"
    elif conName == "greater or equal(>=)":
        conName = "gteq"
    elif conName == "less than(<)":
        conName = "lt"
    elif conName == "less or equal(<=)":
        conName = "lteq"
    args = content[1].split(",")
    sentence = ""
    sentence += conName + "("
    for k in range(len(args)-1):
        if args[k].find("servers.") >= 0:
            args[k] = args[k].replace("servers.", "servers_")
        elif args[k].find("networks.") >= 0:
            args[k] = args[k].replace("networks.", "net_")
    
        if k == 0:
            sentence += args[k]
        else:
            sentence += ", " + args[k]
    if (lenConditions-1) == 1:
        sentence += ")"
    elif conditionIndex != (lenConditions-2):
        sentence += "),"
    else:
        sentence += ")"
    return sentence

#data means the Data column of UI
def create_sentence_from_data(dataMesg, policy_table_name):
    title = dataMesg.split(",")
    sentence = policy_table_name + "("
    #sentence = "error1("
    for i in range((len(title)-1)):
        title[i] = title[i].lower()
        title[i] = title[i].replace("servers.", "servers_")
        title[i] = title[i].replace("networks.", "net_")
        sentence += title[i]
        if i != (len(title)-2):
            sentence += ","
    sentence += ")" + str(congress.RULE_SEPARATOR)
    return sentence


#according the message sended by UI to create datalog
def generate_rule(request):
    #get user's input message on UI
    rules_string = request.GET.get('msg')
    response = http.HttpResponse(content_type='text/plain')

    rules_list = rules_string.split("@@")
    rule = ""
    for mesg in rules_list:
        if mesg != "":
            #create datalog
            rule = ""
	    rule_string = mesg
            mesg=mesg.split("&")
	
	    policy_table_name = "error"
	    if mesg[3] != "":
	        policy_table_name = mesg[3]
	    LOG.error("--------policy_table_name=%s" % policy_table_name)
            rule += create_sentence_from_data(mesg[2], policy_table_name)

            objects = mesg[0].split(",")
            iAddPorts = 0
            for i in range(len(objects)-1):
                if objects[i] == "servers":
                    rule += create_sentence_from_objects("servers")
                    iAddPorts = iAddPorts + 1
                elif objects[i] == "networks":
                    rule += create_sentence_from_objects("networks")
                    iAddPorts = iAddPorts + 1
            if iAddPorts == 2:
                rule += "neutronv2:ports(a, tenant_id, c, network_id, e, f, g, device_id, i),"
                rule=rule.replace("servers_id", "device_id")
                rule=rule.replace("net_id", "network_id")


            conditions = mesg[1].split("|")
	    conLength = len(conditions)
            for j in range(len(conditions)-1):
                condition = conditions[j]
		rule += create_sentence_from_conditions(conLength, condition, j)




            comment = ""
            policy_name = "classification"
            try:
                params = {
                    'name': rule_string,
                    'comment': comment,
                    'rule': rule,
                }
                LOG.error('************Policy PARAMS: %s' % params)
                rule = congress.policy_rule_create(request, policy_name,
                                                   body=params)
            except Exception as e:
                exceptions.handle(request)


   
    response.write(rule)
    response.flush()                                                    
    return response

def show_results(request):
    #get_objects(request)    
    #LOG.error('************ok*********** \n')

    policy_name = "classification"
    table_name = "error"
    results = ""
    data = ""
    try:
        #policies = congress.policy_get(request, policy_name)
        #LOG.error('************Policy_GET : %s' % policies)
        policies = congress.policy_rules_list(request, policy_name)
    #    LOG.error('************Policy_Rules_list : %s' % policies)
	#id=""
	for rule in policies:
	#    rule.set_id_as_name_if_empty()
        #    LOG.error('************rule: %s\n' % rule)
	#    LOG.error('>>>>>>>>>>>>>>>\n')	
	#    LOG.error('rule name: %s\n' % rule['name'])
	#    LOG.error('<<<<<<<<<<<<<<<\n\n\n')
	    #id = rule['id']
	    rule_string = rule['name']
	    LOG.error("++++++++++rule_string=%s\n" % rule_string)
	    contents = rule_string.split("&")
	    if contents[3] != "":
	        table_name = contents[3]
            LOG.error('************table_name: %s' % table_name)
            results = ""
            results = congress.policy_rows_list(request, policy_name, table_name)
            LOG.error('************results: %s' % results)
            data += rule_string + "&"
            for item in results:
                data += str(item['data'])+","
                LOG.error('************data: %s' % data)
	    data += "&" + rule['rule']
	    data += "@@"
	    
	#congress.policy_rule_delete(request, policy_name, id)
	#LOG.error('id = %sn\n\n' % id)
        #policies = congress.policy_tables_list(request, policy_name)
	#table_name = "(615a14fc)"
        #results = congress.policy_rows_list(request, policy_name, table_name)
        #LOG.error('************results: %s' % results)
    except Exception as e:
        msg = ('Unable to get results: %s') % e.message
        #messages.error(request, msg)

    #data = ""
    #for item in results:
    #    data += str(item['data'])+","
    #    LOG.error('************data: %s' % data)
    #data = data.replace("[u'", "")
    #data = data.replace("']", "")
    context = data
    response = http.HttpResponse(content_type='text/plain')
    response.write(context)
    response.flush()
    return response    

def get_objects(request):
    #objs.get_server(request, objs.server_contains, objs.server_keys, objs.server_sentense,
    #                objs.server_final_list, objs.server_head_list)
    objs.__object__(request)
    objs.object_register(request)
    objs.create_rule(request)
    try:
        policy_name = "classification"
        policies = congress.policy_rules_list(request, policy_name)
        LOG.error('************Policy_Rules_list : %s' % policies)
    except Exception as e:
        messages.error(request, e.message)
    data = ""
    for i,item in enumerate(objs.active_object):
	    data += item['name'] + ","

    data += "&"
    for i,item in enumerate(objs.active_object):
        try:
            #messages.error(request, "dname: %s table_name: %s\n" % (obj['datasource_id'],obj['id']))
            data += item['name'] + ":"
            #LOG.error("---------schema[columns]= %s\n" % schema['columns'])
            lst = item['final_list']
            for it in lst:
                data += it + ","
                #LOG.error("---------it[name]= %s\n" % it['name'])
            data += ";"
                #LOG.error("**********data = %s \n" % data)
        except Exception as e:
            message.error(request, e.message)
            return []
    context = data
    LOG.error("\n&&&&&&%s\n&&&&&&" % data)
    response = http.HttpResponse(content_type='text/plain')
    response.write(context)
    response.flush()
    return response    


