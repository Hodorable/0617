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

import sys,logging
import models as db
from horizon import messages
from openstack_dashboard.api import congress as cg_api
LOG = logging.getLogger(__name__)


def get_object(request, obj_name, contains, keys, final_list):

    # generate head
    sentence = obj_name
    for i, attr in enumerate(final_list):
        sentence += "(" if i == 0 else ","
        sentence += attr
    sentence +=  ") " + cg_api.RULE_SEPARATOR + " "

    c = 0
    f = True
    for j,(dname, tname, lst, mp) in enumerate(contains) :
        try:
            schema = cg_api.datasource_table_schema_get_by_name(request, dname, tname)
            sen = dname + cg_api.TABLE_SEPARATOR + tname
            ignore = True
            for i,col in enumerate(schema['columns']):
                sen += "(" if i == 0 else ","
                t = mp.get(col['name'], col['name'])
                if t in keys or (t in lst and t in final_list): 
                    sen += t
                    if t in final_list:
                        ignore = False
                else:
                    sen += "v%d" % c
                    c += 1
            if j == 0 or not ignore:
                if not f:
                    sentence += ","
                f = False
                sentence += sen + ")"
        except Exception as e:
            messages.error(request, e.message)

    return sentence

def __object__(request):

    active_object = []

    for i,(obj_name, dname, tname) in enumerate(db.object_list):
        try:
            # check object main table in datasource
            schema = cg_api.datasource_table_schema_get_by_name(request, dname, tname)
            # if get main table success
            exec("contains = db.%s_contains" % obj_name)
            attr = []
            obj_struct = [obj_name, attr]
            for i,(dname, tname, lst, mp) in enumerate(contains) :
                try:
                    schema = cg_api.datasource_table_schema_get_by_name(request, dname, tname)
                    # if get table success
                    for i, t in enumerate(lst):
                        attr.append(t)
                except Exception as e:
                    LOG.error(e.message)            
            # register
            active_object.append(obj_struct)    
        except Exception as e:
            LOG.error("__object__ error :%s" % e.message)


    return active_object

def object_register(request, object_name, final_list):

    sentence = ""
    exec("contains = db.%s_contains" % object_name)
    exec("keys = db.%s_keys" % object_name)
    sentence = get_object(request, object_name, contains, keys, final_list)
    return sentence

def create_rule(request, sentence):

    try:
        params = {
            'name': "",
            'comment': "",
            'rule': sentence,
        }
        rule = cg_api.policy_rule_create(request, "classification",
                                           body=params)
    except Exception as e:
        messages.error(request, e.message)
