import sqlalchemy as sa
from sqlalchemy.types import CHAR, Integer, String
from sqlalchemy.orm import exc as db_exc
from oslo_db.sqlalchemy import models
from sqlalchemy.ext import declarative
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BaseModel = declarative.declarative_base()
engine = create_engine('mysql+mysqlconnector://root:password@localhost:3306/congress')
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
#PolicyUI.add_data(1,"q","w","e","r")
#PolicyUI.delete_data(1)
#print PolicyUI.get_data("3").name
