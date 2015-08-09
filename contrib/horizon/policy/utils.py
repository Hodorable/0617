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

"""
UUID related utilities and helper functions.
"""

import uuid
import re

import sqlalchemy as sa
from sqlalchemy.types import CHAR, Integer, String
from sqlalchemy.orm import exc as db_exc
from oslo_db.sqlalchemy import models
from sqlalchemy.ext import declarative
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oslo.config import cfg

def generate_uuid():
    return str(uuid.uuid4())


def is_uuid_like(val):
    """Returns validation of a value as a UUID.

    For our purposes, a UUID is a canonical form string:
    aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    :param val: val string can be with or without dash
    """
    try:
        uuid_str = str(uuid.UUID(val))
        regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?' +
            '[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
        match = regex.match(uuid_str)
        if match:
            return True
        else:
            return False
    except (TypeError, ValueError, AttributeError):
        return False

database_group = cfg.OptGroup(
    name='database', 
    title='databaseMQ options'
)

database_con_opt = cfg.StrOpt('connection',
                             default='mysql+mysqlconnector://root:password@localhost:3306/congress',
                             help='use connect mysql') 
CONF = cfg.CONF

CONF.register_group(database_group)
CONF.register_opt(database_con_opt, database_group)

def get_conn():
     
    CONF(default_config_files=['/etc/congress/congress.conf'])
    #CONF()
    return  str(CONF.database.connection)

BaseModel = declarative.declarative_base()
str_conn = get_conn()
engine = create_engine(str_conn)
Session = sessionmaker(bind=engine)
def init_db():
    BaseModel.metadata.create_all(engine)
def drop_db():
    BaseModel.metadata.drop_all(engine)
class PolicyUI(BaseModel):
    __tablename__ = "policy_ui"

    # TODO(thinrichs): change this so instead of storing the policy name
    #   we store the policy's ID.  Nontrivial since we often have the
    #   policy's name but not the ID; looking up the ID from the name
    #   outside of this class leads to race conditions, which means
    #   this class ought to be modified so that add/delete/etc. supports
    #   either name or ID as input.
    id = sa.Column(sa.String(40),primary_key=True)
    name = sa.Column(sa.Text(),nullable=True)
    objects = sa.Column(sa.Text(), nullable=True)
    vi_condition = sa.Column(sa.Text(), nullable=True)
    actions = sa.Column(sa.Text(), nullable=True)
    data = sa.Column(sa.Text(), nullable=True)
    datalog = sa.Column(sa.Text(), nullable=True)
    result = sa.Column(sa.Text(), nullable=True)
    #def __init__(self): pass
    def __init__(self, id_ , name, objects, vi_condition, 
                 actions,data,datalog,result):
        self.id = id_
        self.name = name
        self.objects = objects
        self.vi_condition = vi_condition
        self.actions = actions
        self.data =data
        self.datalog=datalog
        self.result=result
        #@staticmethod
        #def add_data()
def add_data(id_, name_tt, objects_tt, vi_condition_tt, actions_tt,
           data_tt,datalog_tt,result_tt,deleted=False, session=None):
    session =session or Session()
    #with session.begin(subsactions=True):
    try:
      lt = PolicyUI(id_, name_tt, objects_tt, vi_condition_tt,actions_tt,data_tt,datalog_tt,result_tt)
      session.add(lt)
      session.commit()
      return 0
    except Exception ,e:
      session.close()
      print "db_PolicyUI add_data:",e
      return -1

def delete_data(id_, session=None):
    try:
      session = session or Session()
      session.query(PolicyUI).filter(PolicyUI.id == id_).delete()
      session.commit()
      return 0
    except Exception ,e:
      session.close()
      print "db_PolicyUI delete_data:",e
      return -1
def get_data(id_, session=None, deleted=False):
    session = session or Session()
    try:
      return (session.query(PolicyUI).
             filter(PolicyUI.id == id_).
             one())
    except db_exc.NoResultFound:
        return None 
    except Exception, e:
        session.close()
        print "db_PolicyUI get_data:",e
        return -1

def get_datas(session=None, deleted=False):
    try:
      session =session or Session()
      return (session.query(PolicyUI).
             all())
    except db_exc.NoResultFound:
      return None 
    except Exception , e:
      session.close()
      print "db_PolicyUI get_datas:",e
      return -1
   # except db_exc.NoResultFound:
   #   pass

init_db()

class PolicyUI_Model(object):

    def PolicyUI_Add(self,name,objs,cdn,acts,data,datalog,result,id_=None):

        if(id_!=None):
          p = self.PolicyUI_get(id_)
          if(p!=None and p!=-1):
            return -2
        if(id_==None):
          try:
            id_ = str(generate_uuid())
          except Exception , e:
            return -2
        if(name==None):
            name="None";
        if(objs==None):
            objs="None";
        if(cdn==None):
            cdn="None";
        if(acts==None):
            acts="None";
        if(data==None):
            data="None";
        if(datalog==None):
            datalog="None";
        if(result==None):
            result="None";   
        res = add_data(id_,name,objs,cdn,acts,data,datalog,result)
        return res

    def PolicyUI_Del(self,id_):
      if(id_==None):
        return -1
      if(id_!=None):
        p = self.PolicyUI_get(id_)
        if(p==None):
          return -2
        res = delete_data(id_)
        return res
    
    def PolicyUI_get(self,id_):
        if(id_==None):
            return -1
        data = get_data(id_)
        return data
      
    def PolicyUI_gets(self):
        data = get_datas()
        return data
