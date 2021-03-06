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

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: panos_security_policy
short_description: create security rule policy
description: >
    Security policies allow you to enforce rules and take action, and can be as general or specific as needed.
    The policy rules are compared against the incoming traffic in sequence, and because the first rule that matches
    the traffic is applied, the more specific rules must precede the more general ones.
author: "Ivan Bojer (@ivanbojer)"
version_added: "2.3"
requirements:
    - pan-python can be obtained from PyPi U(https://pypi.python.org/pypi/pan-python)
    - pandevice can be obtained from PyPi U(https://pypi.python.org/pypi/pandevice)
notes:
    - Checkmode is not supported.
    - Panorama is supported
options:
    ip_address:
        description:
            - IP address (or hostname) of PAN-OS device being configured.
        required: true
    username:
        description:
            - Username credentials to use for auth.
        required: false
        default: "admin"
    password:
        description:
            - Password credentials to use for auth.
        required: true
    api_key:
        description:
            - API key that can be used instead of I(username)/I(password) credentials.
    rule_name:
        description:
            - Name of the security rule.
        required: true
    rule_type:
        description:
            - Type of security rule (6.1+).
        required: false
        default: "universal"
    description:
        description:
            - Description for the security rule.
        required: false
        default: "None"
    tag:
        description:
            - Administrative tags that can be added to the rule. Note, tags must be already defined.
        required: false
        default: "None"
    from_zone:
        description:
            - List of source zones.
        required: false
        default: "any"
    to_zone:
        description:
            - List of destination zones.
        required: false
        default: "any"
    source:
        description:
            - List of source addresses.
        required: false
        default: "any"
    source_user:
        description:
            - Use users to enforce policy for individual users or a group of users.
        required: false
        default: "any"
    hip_profiles:
        description: >
            If you are using GlobalProtect with host information profile (HIP) enabled, you can also base the policy
            on information collected by GlobalProtect. For example, the user access level can be determined HIP that
            notifies the firewall about the user's local configuration.
        required: false
        default: "any"
    destination:
        description:
            - List of destination addresses.
        required: false
        default: "any"
    application:
        description:
            - List of applications.
        required: false
        default: "any"
    service:
        description:
            - List of services.
        required: false
        default: "application-default"
    log_start:
        description:
            - Whether to log at session start.
        required: false
        default: false
    log_end:
        description:
            - Whether to log at session end.
        required: false
        default: true
    action:
        description:
            - Action to apply once rules maches.
        required: false
        default: "allow"
    group_profile:
        description: >
            Security profile group that is already defined in the system. This property supersedes antivirus,
            vulnerability, spyware, url_filtering, file_blocking, data_filtering, and wildfire_analysis properties.
        required: false
        default: None
    antivirus:
        description:
            - Name of the already defined antivirus profile.
        required: false
        default: None
    vulnerability:
        description:
            - Name of the already defined vulnerability profile.
        required: false
        default: None
    spyware:
        description:
            - Name of the already defined spyware profile.
        required: false
        default: None
    url_filtering:
        description:
            - Name of the already defined url_filtering profile.
        required: false
        default: None
    file_blocking:
        description:
            - Name of the already defined file_blocking profile.
        required: false
        default: None
    data_filtering:
        description:
            - Name of the already defined data_filtering profile.
        required: false
        default: None
    wildfire_analysis:
        description:
            - Name of the already defined wildfire_analysis profile.
        required: false
        default: None
    devicegroup:
        description: >
            Device groups are used for the Panorama interaction with Firewall(s). The group must exists on Panorama.
            If device group is not define we assume that we are contacting Firewall.
        required: false
        default: None
    commit:
        description:
            - Commit if changed
        required: false
        default: true
'''

EXAMPLES = '''
- name: permit ssh to 1.1.1.1
  panos_security_policy:
    ip_address: '10.5.172.91'
    username: 'admin'
    password: 'paloalto'
    rule_name: 'SSH permit'
    description: 'SSH rule test'
    from_zone: ['public']
    to_zone: ['private']
    source: ['any']
    source_user: ['any']
    destination: ['1.1.1.1']
    category: ['any']
    application: ['ssh']
    service: ['application-default']
    hip_profiles: ['any']
    action: 'allow'
    commit: false

- name: Allow HTTP multimedia only from CDNs
  panos_security_policy:
    ip_address: '10.5.172.91'
    username: 'admin'
    password: 'paloalto'
    rule_name: 'HTTP Multimedia'
    description: 'Allow HTTP multimedia only to host at 1.1.1.1'
    from_zone: ['public']
    to_zone: ['private']
    source: ['any']
    source_user: ['any']
    destination: ['1.1.1.1']
    category: ['content-delivery-networks']
    application: ['http-video', 'http-audio']
    service: ['service-http', 'service-https']
    hip_profiles: ['any']
    action: 'allow'
    commit: false

- name: more complex fictitious rule that uses profiles
  panos_security_policy:
    ip_address: '10.5.172.91'
    username: 'admin'
    password: 'paloalto'
    rule_name: 'Allow HTTP w profile'
    log_start: false
    log_end: true
    action: 'allow'
    antivirus: 'default'
    vulnerability: 'default'
    spyware: 'default'
    url_filtering: 'default'
    wildfire_analysis: 'default'
    commit: false

- name: deny all
  panos_security_policy:
    ip_address: '10.5.172.91'
    username: 'admin'
    password: 'paloalto'
    rule_name: 'DenyAll'
    log_start: true
    log_end: true
    action: 'deny'
    rule_type: 'interzone'
    commit: false

# permit ssh to 1.1.1.1 using panorama and pushing the configuration to firewalls
# that are defined in 'DeviceGroupA' device group
- name: permit ssh to 1.1.1.1 through Panorama
  panos_security_policy:
    ip_address: '10.5.172.92'
    password: 'paloalto'
    rule_name: 'SSH permit'
    description: 'SSH rule test'
    from_zone: ['public']
    to_zone: ['private']
    source: ['any']
    source_user: ['any']
    destination: ['1.1.1.1']
    category: ['any']
    application: ['ssh']
    service: ['application-default']
    hip_profiles: ['any']
    action: 'allow'
    devicegroup: 'DeviceGroupA'
'''

RETURN = '''
# Default return values
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import get_exception

try:
    import pan.xapi
    from pan.xapi import PanXapiError
    import pandevice
    import pandevice.firewall
    import pandevice.panorama
    import pandevice.objects
    import pandevice.policies

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def security_rule_exists(device, rule_name):
    if isinstance(device, pandevice.firewall.Firewall):
        rule_base = pandevice.policies.Rulebase.refreshall(device)
    elif isinstance(device, pandevice.panorama.Panorama):
        # look for only pre-rulebase ATM
        rule_base = pandevice.policies.PreRulebase.refreshall(device)

    if rule_base:
        rule_base = rule_base[0]
        security_rules = rule_base.findall(pandevice.policies.SecurityRule)

        if security_rules:
            for r in security_rules:
                if r.name == rule_name:
                    return True

    return False


def create_security_rule(**kwargs):
    security_rule = pandevice.policies.SecurityRule(
        name=kwargs['rule_name'],
        description=kwargs['description'],
        tozone=kwargs['to_zone'],
        fromzone=kwargs['from_zone'],
        source=kwargs['source'],
        source_user=kwargs['source_user'],
        destination=kwargs['destination'],
        category=kwargs['category'],
        application=kwargs['application'],
        service=kwargs['service'],
        hip_profiles=kwargs['hip_profiles'],
        log_start=kwargs['log_start'],
        log_end=kwargs['log_end'],
        type=kwargs['rule_type'],
        action=kwargs['action'])

    if 'tag' in kwargs:
        security_rule.tag = kwargs['tag']

    # profile settings
    if 'group_profile' in kwargs:
        security_rule.group = kwargs['group_profile']
    else:
        if 'antivirus' in kwargs:
            security_rule.virus = kwargs['antivirus']
        if 'vulnerability' in kwargs:
            security_rule.vulnerability = kwargs['vulnerability']
        if 'spyware' in kwargs:
            security_rule.spyware = kwargs['spyware']
        if 'url_filtering' in kwargs:
            security_rule.url_filtering = kwargs['url_filtering']
        if 'file_blocking' in kwargs:
            security_rule.file_blocking = kwargs['file_blocking']
        if 'data_filtering' in kwargs:
            security_rule.data_filtering = kwargs['data_filtering']
        if 'wildfire_analysis' in kwargs:
            security_rule.wildfire_analysis = kwargs['wildfire_analysis']

    return security_rule


def add_security_rule(device, sec_rule):
    if isinstance(device, pandevice.firewall.Firewall):
        rule_base = pandevice.policies.Rulebase.refreshall(device)
    elif isinstance(device, pandevice.panorama.Panorama):
        # look for only pre-rulebase ATM
        rule_base = pandevice.policies.PreRulebase.refreshall(device)

    if rule_base:
        rule_base = rule_base[0]

        rule_base.add(sec_rule)
        sec_rule.create()

        return True
    else:
        return False


def _commit(device, device_group=None):
    """
    :param device: either firewall or panorama
    :param device_group: panorama device group or if none then 'all'
    :return: True if successful
    """
    result = device.commit(sync=True)

    if isinstance(device, pandevice.panorama.Panorama):
        result = device.commit_all(sync=True, sync_all=True, devicegroup=device_group)

    return result


def main():
    argument_spec = dict(
        ip_address=dict(required=True),
        password=dict(no_log=True),
        username=dict(default='admin'),
        api_key=dict(no_log=True),
        rule_name=dict(required=True),
        description=dict(default=''),
        tag=dict(),
        to_zone=dict(type='list', default=['any']),
        from_zone=dict(type='list', default=['any']),
        source=dict(type='list', default=["any"]),
        source_user=dict(type='list', default=['any']),
        destination=dict(type='list', default=["any"]),
        category=dict(type='list', default=['any']),
        application=dict(type='list', default=['any']),
        service=dict(type='list', default=['application-default']),
        hip_profiles=dict(type='list', default=['any']),
        group_profile=dict(),
        antivirus=dict(),
        vulnerability=dict(),
        spyware=dict(),
        url_filtering=dict(),
        file_blocking=dict(),
        data_filtering=dict(),
        wildfire_analysis=dict(),
        log_start=dict(type='bool', default=False),
        log_end=dict(type='bool', default=True),
        rule_type=dict(default='universal'),
        action=dict(default='allow'),
        devicegroup=dict(),
        commit=dict(type='bool', default=True)
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False,
                           required_one_of=[['api_key', 'password']])
    if not HAS_LIB:
        module.fail_json(msg='Missing required pan-python and pandevice modules.')

    ip_address = module.params["ip_address"]
    password = module.params["password"]
    username = module.params['username']
    api_key = module.params['api_key']
    rule_name = module.params['rule_name']
    description = module.params['description']
    tag = module.params['tag']
    from_zone = module.params['from_zone']
    to_zone = module.params['to_zone']
    source = module.params['source']
    source_user = module.params['source_user']
    destination = module.params['destination']
    category = module.params['category']
    application = module.params['application']
    service = module.params['service']
    hip_profiles = module.params['hip_profiles']
    log_start = module.params['log_start']
    log_end = module.params['log_end']
    rule_type = module.params['rule_type']
    action = module.params['action']

    group_profile = module.params['group_profile']
    antivirus = module.params['antivirus']
    vulnerability = module.params['vulnerability']
    spyware = module.params['spyware']
    url_filtering = module.params['url_filtering']
    file_blocking = module.params['file_blocking']
    data_filtering = module.params['data_filtering']
    wildfire_analysis = module.params['wildfire_analysis']

    devicegroup = module.params['devicegroup']

    commit = module.params['commit']

    if devicegroup:
        device = pandevice.panorama.Panorama(ip_address, username, password, api_key=api_key)
        dev_grps = device.refresh_devices()

        for grp in dev_grps:
            if grp.name == devicegroup:
                break
            module.fail_json(msg=' \'%s\' device group not found in Panorama. Is the name correct?' % devicegroup)
    else:
        device = pandevice.firewall.Firewall(ip_address, username, password, api_key=api_key)

    if security_rule_exists(device, rule_name):
        module.fail_json(msg='Rule with the same name already exists.')

    try:
        sec_rule = create_security_rule(
            rule_name=rule_name,
            description=description,
            tag=tag,
            from_zone=from_zone,
            to_zone=to_zone,
            source=source,
            source_user=source_user,
            destination=destination,
            category=category,
            application=application,
            service=service,
            hip_profiles=hip_profiles,
            group_profile=group_profile,
            antivirus=antivirus,
            vulnerability=vulnerability,
            spyware=spyware,
            url_filtering=url_filtering,
            file_blocking=file_blocking,
            data_filtering=data_filtering,
            wildfire_analysis=wildfire_analysis,
            log_start=log_start,
            log_end=log_end,
            rule_type=rule_type,
            action=action
        )

        changed = add_security_rule(device, sec_rule)
    except PanXapiError:
        exc = get_exception()
        module.fail_json(msg=exc.message)

    if changed and commit:
        result = _commit(device, devicegroup)

    module.exit_json(changed=changed, msg="okey dokey")


if __name__ == '__main__':
    main()
