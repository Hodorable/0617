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


server_contains = [ ('nova', 'servers', ['server_id', 'name', 'status'], {'id':'server_id'}),
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
server_relations = [ ('port', ('server_id', 'device_id'), ()), 
                     ('network', (), ('port', )),]

port_contains = [ ('neutronv2', 'ports', ['port_id', 'name', 'mac_address', 'admin_state_up', 'status', 'device_id', 'network_id'],
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
port_relations = [ ('server', ('device_id', 'server_id'), ()),
                   ('network', ('network_id', 'network_id'), ()), ]

network_contains = [ ('neutronv2', 'networks', ['network_id', 'name', 'status', 'admin_state_up', 'shared'],
                    {'id':'network_id'}),
                     ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}),
                     ('neutronv2', 'security_groups',['tenant_security_group_id', 'tenant_security_group_name'],
                    {'id':'tenant_security_group_id', 'name':'tenant_security_group_name'}) ]
network_keys = ('network_id','tenant_id')
network_relations = [ ('port', ('network_id', 'network_id'), ()),
                      ('server', (), ('port', )) ]

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
subnet_relations = [('port', ('subnet_id', 'port_id'), ()),]

router_contains = [('neutronv2', 'routers', ['router_id', 'name', 'status', 'admin_state_up', 'distributed'], {'id':'router_id'}),
                   ('keystone', 'tenants', ['tenant_name',], {'id':'tenant_id', 'name':'tenant_name'}),
                   ('neutronv2', 'security_groups', ['tenant_security_group_id', 'tenant_security_group_name'],
                    {'id':'tenant_security_group_id', 'name':'tenant_security_group_name'}),
                   ('neutronv2', 'external_gateway_infos', ['enable_snat', 'network_id'], {}),
                   ('neutronv2', 'networks', ['external_network_name',], {'id':'network_id', 'name':'external_network_name'}),
                   ('neutronv2', 'external_fixed_ips', ['external_ip_address', 'subnet_id'], {'ip_address':'external_ip_address'}),
                   ('neutronv2', 'subnets', ['external_subnet_name',], {'id':'subnet_id','name':'external_subnet_name'}) ]
router_keys = ('router_id', 'tenant_id', 'network_id', 'subnet_id')
router_relations = [('port', ('router_id', 'port_id'), ()),]

object_list = [ 
             ('server', 'nova', 'servers'), 
             ('port', 'neutronv2', 'ports'),
             ('subnet', 'neutronv2', 'subnets'),
             ('network', 'neutronv2', 'networks'),
             ('router', 'neutronv2', 'routers'),
              ]
    
def get_object_list(request):
    return object_list
