import db_PolicyUI as dt
import uuidutils
#from congress.openstack.common import uuidutils
#from congress.openstack.common import log as logging

class PolicyUI_Model(object):
    def __init__(self):
      pass
    def PolicyUI_Add(self,name,objs,cdn,acts,data,datalog,result,id_=None):
        if(id_!=None):
          p = self.PolicyUI_get(id_)
          if(p!=None and p!=-1):
            print id_+" is exit"
            return -2
        if(id_==None):
          try:
            id_ = str(uuidutils.generate_uuid())
          except Exception , e:
            print "Policy_Model PolicyUI_Add sec1:",e
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
        res = dt.add_data(id_,name,objs,cdn,acts,data,datalog,result)
        return res
    def PolicyUI_Del(self,id_):
      if(id_==None):
        return -1
      if(id_!=None):
        p = self.PolicyUI_get(id_)
        if(p==None):
          print id_+" is not exit"
          return -2
        res = dt.delete_data(id_)
        return res
    
    def PolicyUI_get(self,id_):
      if(id_==None):
        return -1
      data = dt.get_data(id_)
      return data
      
    def PolicyUI_gets(self):
        data = dt.get_datas()
        return data

#p=PolicyUI_Model()
#p.PolicyUI_Add("p","o","i","u","y","000")
#p.PolicyUI_Del("3")
#print p.PolicyUI_get("3")
#obj=p.PolicyUI_gets()
#for o in obj:
#  print o.id
