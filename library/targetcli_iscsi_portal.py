#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Loïc <loic@karafun.com>
# Copyright: (c) 2020, Ondrej Famera <ondrej-xa2iel8u@famera.cz>
# GNU General Public License v3.0+ (see LICENSE-GPLv3.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# Apache License v2.0 (see LICENSE-APACHE2.txt or http://www.apache.org/licenses/LICENSE-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: targetcli_iscsi_portal
short_description: TargetCLI portal module
description:
     - module for handling iSCSI portals object in targetcli ('/iscsi/.../tpg1/portals').
version_added: "2.0"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
    type: str
  portal_ip:
    description:
      - ip of portal object
    required: true
    default: null
    type: str
  portal_port:
    description:
      - port of portal object
    required: false
    default: 3260
    type: int
  state:
    description:
      - Should the object be present or absent from TargetCLI configuration
    required: false
    default: present
    choices: [present, absent]
    type: str
notes:
   - Tested on CentOS 7.7
requirements: [ ]
author: "Loïc (@psykotox)"
'''

EXAMPLES = '''
- name: remove default 0.0.0.0:3260 portal
  targetcli_iscsi_portal:
    wwn: 'iqn.2020-01.com.recisio.iscsi:alpha'
    portal_ip: '0.0.0.0'
    state: 'absent'

- name: define new iSCSI portal
  targetcli_iscsi_portal:
    wwn: 'iqn.2020-01.com.recisio.iscsi:alpha'
    portal_ip: '192.168.1.10'

- name: remove iSCSI portal
  targetcli_iscsi_portal:
    wwn: 'iqn.2020-01.com.recisio.iscsi:alpha'
    portal_ip: '192.168.1.10'
    state: 'absent'
'''

from distutils.spawn import find_executable


def main():
    module = AnsibleModule(
        argument_spec=dict(
            wwn=dict(required=True),
            portal_ip=dict(required=True),
            portal_port=dict(type='int', default="3260", required=False),
            state=dict(default="present", choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    portal = module.params['portal_ip'] + ":" + str(module.params['portal_port'])
    state = module.params['state']

    if find_executable('targetcli') is None:
        module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

    result = {}
    portals = []

    try:
        # check if the iscsi target exists
        cmd = "targetcli '/iscsi/%(wwn)s/tpg1 status'" % module.params
        rc, out, err = module.run_command(cmd)
        if rc != 0 and state == 'present':
            result['changed'] = False
            module.fail_json(msg="ISCSI object doesn't exists", cmd=cmd, output=out, error=err)
        elif rc != 0 and state == 'absent':
            result['changed'] = False
            # ok iSCSI object doesn't exist so portal is also not there --> success
        else:
            # lets parse the list of portals from the targetcli
            cmd = "targetcli '/iscsi/%(wwn)s/tpg1/portals ls'" % module.params
            rc, output, err = module.run_command(cmd)
            result['portals_output'] = output
            for row in output.split('\n'):
                row_data = row.split(' ')
                if len(row_data) < 2 or row_data[0] == 'portals':
                    continue
                if row_data[1] == "portals":
                    continue
                portals.append(row_data[3])
            if state == 'present' and portal in portals:
                # portal is already there and present
                result['changed'] = False
            elif state == 'absent' and portal not in portals:
                # portal is not there and should not be there
                result['changed'] = False
            elif state == 'present' and portal not in portals:
                # create portal
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/portals create ip_address=%(portal_ip)s ip_port=%(portal_port)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to create iSCSI portal object using command " + cmd, output=out, error=err)

            elif state == 'absent' and portal in portals:
                # delete portal
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/portals delete ip_address=%(portal_ip)s ip_port=%(portal_port)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI portal object using command " + cmd, output=out, error=err)
    except OSError as e:
        module.fail_json(msg="Failed to check iSCSI portal object - %s" % (e))
    module.exit_json(**result)


# import module snippets
from ansible.module_utils.basic import AnsibleModule
if __name__ == "__main__":
    main()
