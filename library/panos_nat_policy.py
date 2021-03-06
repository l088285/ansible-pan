#!/usr/bin/env python

#  Copyright 2016 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

DOCUMENTATION = '''
---
module: panos_nat_policy
short_description: create a policy NAT rule
description:
    - Create a policy nat rule. Keep in mind that we can either end up configuring source NAT, destination NAT, or both. Instead of splitting it into two we will make a fair attempt to determine which one the user wants.
author: "Luigi Mori (@jtschichold), Ivan Bojer (@ivanbojer)"
version_added: "2.3"
requirements:
    - pan-python
options:
    ip_address:
        description:
            - IP address (or hostname) of PAN-OS device
        required: true
    password:
        description:
            - password for authentication
        required: true
    username:
        description:
            - username for authentication
        required: false
        default: "admin"
    rule_name:
        description:
            - name of the SNAT rule
        required: true
    from_zone:
        description:
            - list of source zones
        required: true
    to_zone:
        description:
            - destination zone
        required: true
    source:
        description:
            - list of source addresses
        required: false
        default: ["any"]
    destination:
        description:
            - list of destination addresses
        required: false
        default: ["any"]
    service:
        description:
            - service
        required: false
        default: "any"
    snat_type:
        description:
            - type of source translation
        required: false
        default: None
    snat_address:
        description:
            - snat translated address
        required: false
        default: None
    snat_interface:
        description:
            - snat interface
        required: false
        default: None
    snat_interface_address:
        description:
            - snat interface address
        required: false
        default: None
    snat_bidirectional:
        description:
            - bidirectional flag
        required: false
        default: "false"
    dnat_address:
        description:
            - dnat translated address
        required: false
        default: None
    dnat_port:
        description:
            - dnat translated port
        required: false
        default: None
    override:
        description:
            - attempt to override rule if one with the same name already exists
        required: false
        default: "false"
    commit:
        description:
            - commit if changed
        required: false
        default: true
'''

EXAMPLES = '''
# Create a source and destination nat rule
  - name: create nat SSH221 rule for 10.0.1.101
    panos_nat:
      ip_address: "192.168.1.1"
      password: "admin"
      rule_name: "Web SSH"
      from_zone: ["external"]
      to_zone: "external"
      source: ["any"]
      destination: ["10.0.0.100"]
      service: "service-tcp-221"
      snat_type: "dynamic-ip-and-port"
      snat_interface: "ethernet1/2"
      dnat_address: "10.0.1.101"
      dnat_port: "22"
      commit: False
'''

RETURN = '''
# Default return values
'''

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import get_exception

try:
    import pan.xapi
    from pan.xapi import PanXapiError

    HAS_LIB = True
except ImportError:
    HAS_LIB = False

_NAT_XPATH = "/config/devices/entry[@name='localhost.localdomain']" + \
             "/vsys/entry[@name='vsys1']" + \
             "/rulebase/nat/rules/entry[@name='%s']"


def nat_rule_exists(xapi, rule_name):
    xapi.get(_NAT_XPATH % rule_name)
    e = xapi.element_root.find('.//entry')
    if e is None:
        return False
    return True


def dnat_xml(m, dnat_address, dnat_port):
    if dnat_address is None and dnat_port is None:
        return None

    exml = ["<destination-translation>"]
    if dnat_address is not None:
        exml.append("<translated-address>%s</translated-address>" %
                    dnat_address)
    if dnat_port is not None:
        exml.append("<translated-port>%s</translated-port>" %
                    dnat_port)
    exml.append('</destination-translation>')

    return ''.join(exml)


def snat_xml(m, snat_type, snat_address, snat_interface,
             snat_interface_address, snat_bidirectional):
    if snat_type == 'static-ip':
        if snat_address is None:
            m.fail_json(msg="snat_address should be speicified "
                            "for snat_type static-ip")

        exml = ["<source-translation>", "<static-ip>"]
        if snat_bidirectional:
            exml.append('<bi-directional>%s</bi-directional>' % 'yes')
        else:
            exml.append('<bi-directional>%s</bi-directional>' % 'no')
        exml.append('<translated-address>%s</translated-address>' %
                    snat_address)
        exml.append('</static-ip>')
        exml.append('</source-translation>')
    elif snat_type == 'dynamic-ip-and-port':
        exml = ["<source-translation>",
                "<dynamic-ip-and-port>"]
        if snat_interface is not None:
            exml = exml + [
                "<interface-address>",
                "<interface>%s</interface>" % snat_interface]
            if snat_interface_address is not None:
                exml.append("<ip>%s</ip>" % snat_interface_address)
            exml.append("</interface-address>")
        elif snat_address is not None:
            exml.append("<translated-address>")
            for t in snat_address:
                exml.append("<member>%s</member>" % t)
            exml.append("</translated-address>")
        else:
            m.fail_json(msg="no snat_interface or snat_address "
                            "specified for snat_type dynamic-ip-and-port")
        exml.append('</dynamic-ip-and-port>')
        exml.append('</source-translation>')
    else:
        m.fail_json(msg="unknown snat_type %s" % snat_type)

    return ''.join(exml)


def add_nat(xapi, module, rule_name, from_zone, to_zone,
            source, destination, service, dnatxml=None, snatxml=None):
    exml = []
    if dnatxml:
        exml.append(dnatxml)
    if snatxml:
        exml.append(snatxml)

    exml.append("<to><member>%s</member></to>" % to_zone)

    exml.append("<from>")
    exml = exml + ["<member>%s</member>" % e for e in from_zone]
    exml.append("</from>")

    exml.append("<source>")
    exml = exml + ["<member>%s</member>" % e for e in source]
    exml.append("</source>")

    exml.append("<destination>")
    exml = exml + ["<member>%s</member>" % e for e in destination]
    exml.append("</destination>")

    exml.append("<service>%s</service>" % service)

    exml.append("<nat-type>ipv4</nat-type>")

    exml = ''.join(exml)

    xapi.set(xpath=_NAT_XPATH % rule_name, element=exml)

    return True


def main():
    argument_spec = dict(
        ip_address=dict(required=True),
        password=dict(required=True, no_log=True),
        username=dict(default='admin'),
        rule_name=dict(required=True),
        from_zone=dict(type='list', required=True),
        to_zone=dict(required=True),
        source=dict(type='list', default=["any"]),
        destination=dict(type='list', default=["any"]),
        service=dict(default="any"),
        snat_type=dict(),
        snat_address=dict(),
        snat_interface=dict(),
        snat_interface_address=dict(),
        snat_bidirectional=dict(default=False),
        dnat_address=dict(),
        dnat_port=dict(),
        override=dict(type='bool', default=False),
        commit=dict(type='bool', default=True)
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    if not HAS_LIB:
        module.fail_json(msg='pan-python is required for this module')

    ip_address = module.params["ip_address"]
    password = module.params["password"]
    username = module.params['username']

    xapi = pan.xapi.PanXapi(
        hostname=ip_address,
        api_username=username,
        api_password=password
    )

    rule_name = module.params['rule_name']
    from_zone = module.params['from_zone']
    to_zone = module.params['to_zone']
    source = module.params['source']
    destination = module.params['destination']
    service = module.params['service']

    snat_type = module.params['snat_type']
    snat_address = module.params['snat_address']
    snat_interface = module.params['snat_interface']
    snat_interface_address = module.params['snat_interface_address']
    snat_bidirectional = module.params['snat_bidirectional']

    dnat_address = module.params['dnat_address']
    dnat_port = module.params['dnat_port']
    commit = module.params['commit']

    override = module.params["override"]
    if not override and nat_rule_exists(xapi, rule_name):
        module.exit_json(changed=False, msg="rule exists")

    try:
        changed = add_nat(
            xapi,
            module,
            rule_name,
            from_zone,
            to_zone,
            source,
            destination,
            service,
            dnatxml=dnat_xml(module, dnat_address, dnat_port),
            snatxml=snat_xml(module, snat_type, snat_address,
                             snat_interface, snat_interface_address,
                             snat_bidirectional)
        )

        if changed and commit:
            xapi.commit(cmd="<commit></commit>", sync=True, interval=1)

        module.exit_json(changed=changed, msg="okey dokey")

    except PanXapiError:
        exc = get_exception()
        module.fail_json(msg=exc.message)


if __name__ == '__main__':
    main()
