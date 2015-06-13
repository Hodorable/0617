import sys,logging
from horizon import messages
from openstack_dashboard.api import congress as cg_api
LOG = logging.getLogger(__name__)

server_contains = [ ('nova', 'servers', ['server_id','name', 'status'], {'id':'server_id'}),
                    ('keystone', 'users', ['username', 'enabled', 'email'], {'id':'user_id'}), 
                    ('neutronv2', 'security_groups', ['tenant_security_group_id','tenant_security_group_name'], 
                        {'id':'tenant_security_group_id', 'name':'tenant_security_group_name'}),
                    ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}), 
                    ('nova', 'floating_IPs', ['fixed_ip', 'ip_pool'], {'pool':'ip_pool'}), 
                    ('glancev2', 'images', ['image_name', 'container_format', 'created_at', 'updated_at', 'disk_format', 'protected', 
                        'min_ram', 'min_disk', 'checksum', 'size', 'file', 'kernel_id', 'ramdisk_id', 'schema', 'visibility'],
                        {'id':'image_id', 'name':'image_name'}), 
                    ('nova', 'flavors', ['vcpus', 'ram', 'disk', 'ephemeral', 'rxtx_factor'], {'id':'flavor_id'}) ]
server_keys = ('server_id', 'user_id', 'image_id', 'flavor_id', 'tenant_id')
server_sentence = []
server_final_list = []
server_head_list = []

port_contains = [ ('neutronv2', 'ports', ['port_id', 'name', 'mac_address', 'admin_state_up', 'status'],
                    {'id':'port_id'}),
                  ('neutronv2', 'fixed_ips' ,['ip_address',], {}),
                  ('neutronv2', 'security_groups', ['security_group_id', 'tenant_id', 'security_group_name'], 
                    {'id':'security_group_id','name':'security_group_name'}),
                  ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}),
                  ('neutronv2', 'security_group_rules', ['rule_direction', 'rule_ethertype', 
                    'rule_protocol', 'rule_port_range_min', 'rule_port_range_max','rule_remote_ip_prefix'],
                    {'direction':'rule_direction', 'ethertype':'rule_ethertype', 'protocol':'rule_protocol',
                    'port_range_min':'rule_port_range_min', 'port_range_max':'rule_port_range_max',
                    'remote_ip_prefix':'rule_remote_ip_prefix'}) ]
port_keys = ('port_id', 'tenant_id')
port_sentence = []
port_final_list = []
port_head_list = []

network_contains = [ ('neutronv2', 'networks', ['network_id', 'name', 'status', 'admin_state_up', 'shared'],
                    {'id':'network_id'}),
                     ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}),
                     ('neutronv2', 'security_groups',['tenant_security_group_id', 'tenant_security_group_name'],
                    {'id':'tenant_security_group_id', 'name':'tenant_security_group_name'}) ]
network_keys = ('network_id','tenant_id')
network_sentence = []
network_final_list = []
network_head_list = []

subnet_contains = [ ('neutronv2', 'subnets', ['subnet_id', 'name', 'ip_version', 'cidr', 'gateway_ip', 'enable_dhcp',
                    'ipv6_ra_mode'], {'id':'subnet_id'}),
                    ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}),
                    ('neutronv2', 'security_groups', ['tenant_security_group_id', 'tenant_security_group_name'],
                    {'id':'tenant_security_group_id', 'name':'tenant_security_group_name'}),
                    ('neutronv2', 'dns_nameservers', ['dns_nameserver',], {}),
                    ('neutronv2', 'allocation_pools', ['pool_start','pool_end'], {'parent_key':'subnet_id',
                    'start':'pool_start', 'end':'pool_end'}),
                    ('neutronv2', 'host_routes', ['destination', 'nexthop'], {}) ]
subnet_keys = ('subnet_id', 'tenant_id')
subnet_sentence = []
subnet_final_list = []
subnet_head_list = []

router_contains = [('neutronv2', 'routers', ['router_id', 'name', 'status', 'admin_state_up', 'distributed'], {'id':'router_id'}),
                   ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}),
                   ('neutronv2', 'security_groups', ['tenant_security_group_id', 'tenant_security_group_name'],
                    {'id':'tenant_security_group_id', 'name':'tenant_security_group_name'}),
                   ('neutronv2', 'external_gateway_infos', ['enable_snat', 'network_id'], {}),
                   ('neutronv2', 'networks', ['external_network_name',], {'id':'network_id', 'name':'external_network_name'}),
                   ('neutronv2', 'external_fixed_ips', ['external_ip_address', 'subnet_id'], {'ip_address':'external_ip_address'}),
                   ('neutronv2', 'subnets', ['external_subnet_name',], {'id':'subnet_id','name':'external_subnet_name'}) ]
router_keys = ('router_id', 'tenant_id', 'network_id', 'subnet_id')
router_sentence = []
router_final_list = []
router_head_list = []

def create_sentence(request, obj_name, c, head_col, dname, tname, lst, head_list):
    sentence = obj_name+"%d" % c
    #messages.error(request,"sentence %s" % sentence)
    for idx, ele in enumerate(head_col):   
        #messages.error(request,head_col)
        sentence += ("(" + ele) if idx == 0 else  ("," + ele)
    sentence += ") "
    head_list.append(sentence)
    sentence +=  cg_api.RULE_SEPARATOR + " "
    if c:
        sentence += head_list[c-1] + ","
    #messages.error(request,"sentence %s" % sentence)
    sentence += dname + cg_api.TABLE_SEPARATOR + tname
    #messages.error(request,"~ sentence %s" % sentence)
    for idx, ele in enumerate(lst):
        #messages.error(request,"ele %s" % ele)
        sentence += ("(" + ele) if idx == 0 else  ("," + ele)
        #messages.error(request,"sentence %s" % sentence)
    sentence += ")"
    LOG.error(sentence)
    return sentence
    

def get_object(request, obj_name, contains, keys, sentence, final_list, head_list):
    c = 0
    head_col = []
    for i,(dname, tname, lst, mp) in enumerate(contains) :
        try:
            schema = cg_api.datasource_table_schema_get_by_name(request, dname, tname)
            #messages.error(request,"dname:%s tname:%s c:%d" %(dname,tname,c))
            if c == 0:
                for col in schema['columns']:
                    t = mp.get(col['name'], col['name'])
                    if t in keys or t in lst: 
                        #messages.error(request,col['name'])
                        head_col.append(t)
                for l in lst:
                    #messages.error(request,mp.get(l,l))
                    final_list.append(mp.get(l,l))
            else:
                for col in lst:
                    t = mp.get(col,col)
                    #messages.error(request,"col %s" % t)
                    head_col.append(t)
                    final_list.append(t)
            lt = []
            for col in schema['columns']:
                t = mp.get(col['name'], col['name'])
                if t in keys or t in lst:
                    lt.append(t)
                else:
                    lt.append("_")
            sen = create_sentence(request, obj_name, c, head_col, dname, tname, lt, head_list)
            sentence.append(sen)
            #messages.error(request, msg)
            c += 1
        except Exception as e:
            messages.error(request, e.message)
            if c == 0:
                return "error!!" 
    sen = obj_name
    for idx, ele in enumerate(final_list):   
        #messages.error(request,head_col)
        sen += ("(" + ele) if idx == 0 else  ("," + ele)
    sen += ") "+ cg_api.RULE_SEPARATOR + " "
    if c:
        sen += head_list[c-1]
    sentence.append(sen)
    return sen

object_list = [ 
             ('server', 'nova', 'servers'), 
             ('port', 'neutronv2', 'ports'),
             ('subnet', 'neutronv2', 'subnets'),
             ('network', 'neutronv2', 'networks'),
             ('router', 'neutronv2', 'routers'),
              ]

active_object = []
def append_sentence(obj_name):
    sentence = "{'name':'%s'," % obj_name
    sentence += "'contains':%s_contains," % obj_name
    sentence += "'keys':%s_keys," % obj_name
    sentence += "'sentence':%s_sentence," % obj_name
    sentence += "'final_list':%s_final_list," % obj_name
    sentence += "'head_list':%s_head_list}" %obj_name 
    return sentence
def __object__(request):
    global active_object
    active_object = []
    for i,(obj_name,dname,tname) in enumerate(object_list):
        try:
            schema = cg_api.datasource_table_schema_get_by_name(request, dname, tname)
            #messages.error(request, "active_list.append("+append_sentence(obj_name)+")")
            exec("active_object.append("+append_sentence(obj_name)+")")
        except Exception as e:
            messages.error(request, e.message)

def object_register(request):
    for obj in active_object:
        messages.error(request, obj['name'])
    for i,obj in enumerate(active_object):
        try:
            name = obj['name']
            #messages.error(request,name)
            contains = obj['contains']
            keys = obj['keys']
            sentence = obj['sentence']
            final_list = obj['final_list']
            head_list = obj['head_list']
            get_object(request, name, contains, keys, sentence, final_list, head_list)
        except Exception as e:
            messages.error(request, e.message)

def create_rule(request):
    for i,obj in enumerate(active_object):
        sentence = obj['sentence']

        for j,sen in enumerate(sentence):
            #messages.error(request, "here %d" % j)
            try:
                #messages.error(request, sen)
                LOG.error("~~~~~~~~~------------------datalog:  %s\n~~~~~~~~~" % sen)
                params = {
                    'name': "",
                    'comment': "",
                    'rule': sen,
                }
                rule = cg_api.policy_rule_create(request, "classification",
                                                   body=params)
                LOG.error("--------------after-----------------\n")
            except Exception as e:
                messages.error(request, e.message)
