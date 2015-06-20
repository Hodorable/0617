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

from horizon import messages
from openstack_dashboard.api import congress

import objects as objs
import logging
import sys,os

LOG = logging.getLogger(__name__)

#conditions means the Violation Conditions column of UI
condition_type = { "equal(==)":"equal",
                   "greater than(>)":"gt",
                   "greater or equal(>=)":"gteq",
                   "less than(<)":"lt",
                   "less or equal(<=)":"lteq" }
def create_sentence_from_objects(object_name, final_list,onymous_attr, attr_mp):

    sentence = object_name + "("
    
    for i, attr in enumerate(final_list):
        if i:
            sentence += "," 
        attr = object_name + "_" + attr
        sentence += attr_mp.get(attr, attr) 
    sentence += ")"
    LOG.error("==== create_sentence_from_objects %s  ====" % (sentence))
    return sentence

def create_sentence_from_conditions(condition, onymous_attr, attr_mp):

    content = condition.split(":")
    conName = content[0].lower()
    conName = condition_type.get(conName, conName)

    args = content[1].split(",")
    args = [i for i in args if i != '']
    args = list(set(args))

    sentence = conName + "("
    for i,attr in enumerate(args):
        if i:
            sentence += ","
        attr = attr.replace('.','_')
        if attr not in onymous_attr:
            onymous_attr.append(attr)
        attr = attr_mp.get(attr, attr)
        sentence += attr 
    sentence += ")"
    LOG.error("==== create_sentence_from_conditions %s  ====" % (sentence))
    return sentence

#data means the Data column of UI
def create_sentence_from_data(content, policy_table_name, onymous_attr, attr_mp):

    args = content.split(",")
    args = [i for i in args if i != '']
    args = list(set(args))

    sentence = policy_table_name + "("
    for i,attr in enumerate(args):
        if i:
            sentence += ","
        attr = attr.replace('.', '_')
        if attr not in onymous_attr:
            onymous_attr.append(attr)
        attr = attr_mp.get(attr,attr)
        sentence += attr
    sentence += ") " + str(congress.RULE_SEPARATOR) + " "
    LOG.error("==== create_sentence_from_data %s  ====" % (sentence))
    return sentence


def get_object_relation(content, onymous_attr, attr_mp):

    objects = content.split(",")
    objects = [i for i in objects if i != '']
    objects = list(set(objects))

    for i,name in enumerate(objects):
        # db
        exec("relations = objs.%s_relations" % name)

        for o,a1,a2 in relations:
            if o in objects:
                if a1:
                    t1 = "%s_%s" % (name,a1[0])
                    t2 = "%s_%s" % (o,a1[1])
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
                            objects.append(k)
    return objects


def monitor_datalog(request, content):

    datalog = ""
    rule = ""

    attr_mp = {}
    onymous_attr = []
    objects = get_object_relation(content[0], onymous_attr, attr_mp)

    # generate head part
    # use "error" as default name    
    head_name = "error" if content[3] == "None" else content[3]
    if content[2]:
        rule += create_sentence_from_data(content[2], head_name, onymous_attr, attr_mp)

    # generate condition part
    rule_t = ""
    if content[1]:
        conditions = content[1].split("|")
        for i, con in enumerate(conditions):
            if con:
                rule_t += "," + create_sentence_from_conditions(con, onymous_attr, attr_mp)

    # generate subtarget part
    for i, obj_name in enumerate(objects):
        final_list = []
        for attr in onymous_attr:
            (name,attr) = attr.split("_", 1)
            if obj_name == name:
                final_list.append(attr)
                LOG.error("final_list : %s" % attr)

        # register object
        sentence = ""
        if final_list:
            sentence = objs.object_register(request, obj_name, final_list)
            LOG.error("==== sentence  %s====" % sentence)
        if sentence:
            objs.create_rule(request, sentence)
            datalog += sentence + "\n\n"
        if i:
            rule += ","
        rule += create_sentence_from_objects(obj_name, final_list, onymous_attr, attr_mp)
    
    rule += rule_t
    if rule:
        objs.create_rule(request, rule)
    return datalog + rule
