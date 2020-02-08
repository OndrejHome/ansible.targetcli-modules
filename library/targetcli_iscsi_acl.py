#!/usr/bin/python
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
module: targetcli_iscsi_acl
short_description: TargetCLI iSCSI ACL module
description:
     - module for handling iSCSI ACL objects in targetcli ('/iscsi/.../tpg1/acls').
version_added: "2.0"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
  initiator_wwn:
    description:
      - WWN of iSCSI initiator (client)
    required: true
    default: null
  state:
    description:
      - Should the object be present or absent from TargetCLI configuration
    required: false
    default: present
    choices: [present, absent]
notes:
   - Tested on CentOS 7.2
requirements: [ ]
author: "Ondrej Famera <ondrej-xa2iel8u@famera.cz>"
'''

EXAMPLES = '''
- name: define new iscsi ACL client
  targetcli_iscsi_acl:
    wwn: 'iqn.1994-05.com.redhat:data'
    initiator_wwn: 'iqn.1994-05.com.redhat:client1'

- name: remove iSCSI ACL
  targetcli_iscsi_acl:
    wwn: 'iqn.1994-05.com.redhat:data'
    initiator_wwn: 'iqn.1994-05.com.redhat:client1'
    state: 'absent'
'''

from distutils.spawn import find_executable


def main():
        module = AnsibleModule(
                argument_spec=dict(
                        wwn=dict(required=True),
                        initiator_wwn=dict(required=True),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        state = module.params['state']

        if find_executable('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

        result = {}

        try:
            cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s status'" % module.params
            rc, out, err = module.run_command(cmd)
            if rc == 0 and state == 'present':
                result['changed'] = False
            elif rc == 0 and state == 'absent':
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls delete %(initiator_wwn)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI ACL object using command " + cmd, output=out, error=err)
            elif state == 'absent':
                result['changed'] = False
            else:
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls create %(initiator_wwn)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to define iSCSI ACL object using command " + cmd, output=out, error=err)
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI ACL object - %s" % (e))
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import AnsibleModule
if __name__ == "__main__":
    main()
