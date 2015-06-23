#-*-coding:utf-8-*-
from oslo.config import cfg

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

#if __name__ =="__main__":
# 调用容器对象，传入要解析的文件（可以多个） 
#    CONF(default_config_files=['/etc/congress/congress.conf'])
    #CONF()
#    print("database.connection: "+ str(CONF.database.connection))
