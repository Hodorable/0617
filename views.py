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

ACTIVE_OBJECT = []
OBJECT_INDEX_BY_NAME = {}

#objects means the Objects column of UI
def create_sentence_from_objects(request, object_name, onymous_attr, attr_mp):
    #set the attributes fixed temporary,later we will get them from database
    global OBJECT_INDEX_BY_NAME
    sentence = object_name + "("

    obj = OBJECT_INDEX_BY_NAME[object_name]
    f = False
    cnt = 0
    s = object_name[0] + object_name[1]
    for i,attr in enumerate(obj['final_list']):
        if not attr:
            continue
        if f:
            sentence += ","
        else:
            f = True
        attr = object_name + "_" + attr
        if attr in onymous_attr:
            sentence += attr_mp.get(attr,attr)
        else:
            #sentence += "_" 
            sentence += s + "%d" % cnt
            cnt += 1
    sentence += ")"
    #messages.error(request, " obj_sentence : " + sentence)
    return sentence


#conditions means the Violation Conditions column of UI
condition_type = { "equal(==)":"equal",
                   "greater than(>)":"gt",
                   "greater or equal(>=)":"gteq",
                   "less than(<)":"lt",
                   "less or equal(<=)":"lteq" }
def create_sentence_from_conditions(request, condition, onymous_attr, attr_mp):

#    messages.error(request, condition)
    content = condition.split(":")
#    for i in content:
#        messages.error(request, "content:" + i)
    conName = content[0].lower()
    conName = condition_type.get(conName, conName)
    args = content[1].split(",")

    sentence = conName + "("
    f = False
    for i,attr in enumerate(args):
        if not attr:
            continue
#        else:
#            messages.error(request, "args: " + attr)
        if f:
            sentence += ","
        else:
            f = True
        attr = attr.replace('.','_')
        if attr not in onymous_attr:
            onymous_attr.append(attr)
        attr = attr_mp.get(attr, attr)
        sentence += attr 
    sentence += ")"
    return sentence

#data means the Data column of UI
def create_sentence_from_data(request, dataMesg, policy_table_name, onymous_attr, attr_mp):

    title = dataMesg.split(",")
    sentence = policy_table_name + "("
#    messages.error(request, "data_sentence: " + sentence)
    f = False
    for i,attr in enumerate(title):
        if not attr:
            continue
        if f:
            sentence += ","
        else:
            f = True
        attr = attr.replace('.', '_')
        if attr not in onymous_attr:
            onymous_attr.append(attr)
        attr = attr_mp.get(attr,attr)
        sentence += attr
    sentence += ")" + str(congress.RULE_SEPARATOR)
#    messages.error(request, "~data_sentence: " + sentence)

    return sentence

def get_object_relation(request ,msg ,objects, onymous_attr, attr_mp):

    global ACTIVE_OBJECT
    global OBJECT_INDEX_BY_NAME
    #messages.error(request, "here")
#    for i in ACTIVE_OBJECT:
#        messages.error(request, "active_object: "+ i['name'])
#    for i in OBJECT_INDEX_BY_NAME:
#        messages.error(request, i)
    objects = msg.split(",")
    for i,name in enumerate(objects):
        if not name:
            continue
#        messages.error(request, "%d obj_name: %s" % (i,name))
        obj = OBJECT_INDEX_BY_NAME[name]
        #obj = objs.get_object_by_name(request, name)
        #for k in objs.object_index_by_name:
        #    messages.error(request, "index: "+ k)
        #obj = objs.object_index_by_name[name]
#        messages.error(request, "get_obj:" + obj['name'])
        for o,a1,a2 in obj['relations']:
            if o in objects:
                if a1:
                    t1 = "%s_%s" % (name,a1[0])
                    t2 = "%s_%s" % (o,a1[1])
#                    messages.error(request,"t1 t2: " + t1 + " " + t2)
                    if t1 not in onymous_attr:
                        onymous_attr.append(t1)
                    if t2 not in onymous_attr:
                        onymous_attr.append(t2)
                    if attr_mp.has_key(t1) == False:
                        attr_mp[t1] = attr_mp.get(t2,t1)
                    if attr_mp.has_key(t2) == False:
                        attr_mp[t2] = attr_mp.get(t1,t2)
                if a2:
                    for k in a2:
                        if k not in objects:
                            #messages.error(request,"k: " + k)
                            objects.append(k)
                            #for x in objects:
                            #    messages.error(request, "x: "+x)
#    messages.error(request, "~print_objects: ")
#    for i in objects:
#        if i:
#            messages.error(request, "~obj: " + i)
    return objects

#according the message sended by UI to create datalog
def generate_rule(request):
    #get user's input message on UI
    rules_string = request.GET.get('msg')
    response = http.HttpResponse(content_type='text/plain')
    
#    messages.error(request, rules_string)

    rules_list = rules_string.split("@@")
    global ACTIVE_OBJECT
    global OBJECT_INDEX_BY_NAME
    if not ACTIVE_OBJECT:
        messages.error(request, "g,active_obj = NULL")
        ACTIVE_OBJECT = objs.__object__(request)
    if not OBJECT_INDEX_BY_NAME:
        messages.error(request, "g,index_obj = NULL")
        OBJECT_INEDEX_BY_NAME = objs.object_register(request)
#    messages.error(request, "ghere")
#    for i in objs.active_object:
#        messages.error(request, "active_object: "+ i['name'])
#    for i in OBJECT_INDEX_BY_NAME:
#        messages.error(request, i)
    rule = ""
    for mesg in rules_list:
        if mesg != "":
            # generate datalog sentence
            rule = ""
            rule_string = mesg
            mesg = mesg.split("&")
	       
            # objects relations 
            attr_mp = {}
            objects = [] 
            onymous_attr = []
            if mesg[0] != "":
                objects = get_object_relation(request, mesg[0], objects, onymous_attr, attr_mp)
#            messages.error(request, "print_objects: ")
#            for i in objects:
#                if i:
#                    messages.error(request, "obj: " + i)
            # generate datalog head
            policy_table_name = "error"
            if mesg[3] != "None":
                policy_table_name = mesg[3]
#            messages.error(request, "policy_table_name = %s, %s" % (policy_table_name, mesg[3]))
            rule += create_sentence_from_data(request, mesg[2], policy_table_name, onymous_attr, attr_mp)


            conditions = mesg[1].split("|")
            rule_t = ""

            for i,con in enumerate(conditions):
                if con:
                    rule_t += ","
                    #messages.error(request, "conditions: " + con)
                    rule_t += create_sentence_from_conditions(request, con, onymous_attr, attr_mp)
            
            #messages.error(request, "rult_t : "+ rule_t)    
            
            f = True
            for i,obj in enumerate(objects):
                if obj:
                    if f:
                        f = False
                    else:
                        rule += ","
                    #messages.error(request, "object : " + obj)
                    rule += create_sentence_from_objects(request, obj, onymous_attr, attr_mp)

            rule += rule_t
    
            #messages.error(request, rule)

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
	    if rule_string != "":
	        LOG.error("++++++++++rule_string=%s\n" % rule_string)
	        contents = rule_string.split("&")
	        if contents[3] != "None":
	            table_name = contents[3]
                LOG.error('************table_name: %s' % table_name)
                results = ""
                results = congress.policy_rows_list(request, policy_name, table_name)
                LOG.error('************results: %s' % results)
                data += rule_string + "&"
                for item in results:
                    data += str(item['data'])+","
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
    LOG.error('************data: %s' % data)
    response = http.HttpResponse(content_type='text/plain')
    response.write(context)
    response.flush()
    return response    

def get_objects(request):

    global ACTIVE_OBJECT
    global OBJECT_INDEX_BY_NAME

    ACTIVE_OBJECT = objs.__object__(request)
    OBJECT_INDEX_BY_NAME = objs.object_register(request)
#    for i in OBJECT_INDEX_BY_NAME:
#        messages.error(request, "get_obj " + i)
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

