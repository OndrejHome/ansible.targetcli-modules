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
    type: str
  initiator_wwn:
    description:
      - WWN of iSCSI initiator (client)
    required: true
    default: null
    type: str
  userid:
    description:
      - the userid
    required: false
    default: null
    type: str
  password:
    description:
      - the password
    required: false
    default: null
    type: str
  mutual_userid:
    description:
      - the mutual userid
    required: false
    default: null
    type: str
  mutual_password:
    description:
      - the mutual password
    required: false
    default: null
    type: str
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
author: "Ondrej Famera (@OndrejHome)"
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
            userid=dict(required=False),
            password=dict(required=False, no_log=True),
            mutual_userid=dict(required=False),
            mutual_password=dict(required=False, no_log=True),
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
        result["status"] = (rc,out,err)
        if state == 'absent':
            if rc == 0:
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls delete %(initiator_wwn)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI ACL object using command " + cmd, output=out, error=err)
            else:
                result['changed'] = False
            module.exit_json(**result)
        elif state == 'present':
            if rc == 0:
                result['changed'] = False
            else:
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls create %(initiator_wwn)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc != 0:
                        module.fail_json(msg="Failed to define iSCSI ACL object using command " + cmd, output=out, error=err)
    except OSError as e:
        module.fail_json(msg="Failed to check iSCSI ACL object - %s" % (e))

    try:
        fieldnames=["userid","password","mutual_userid","mutual_password"]
        acls = (module.params.get(i, "") for i in fieldnames)
        if not any(acls):
            module.exit_json(**result)

        cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s get auth'" % module.params
        rc, out, err = module.run_command(cmd)
        # default to None
        values = {k:None for k in fieldnames}
        for line in out.split("\n"):
            if not "=" in line:
                continue
            key,value = line.split("=",1)
            # ignore empty values - stay None
            if value != '' and key in fieldnames:
                values[key]=value

        for name in fieldnames:
            if module.params.get(name, None) == values[name]:
                continue

            result['changed'] = True

            if module.check_mode:
                module.exit_json(**result)

            cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s set auth %(name)s=%(value)s'" % {
                "wwn":module.params["wwn"],
                "initiator_wwn":module.params["initiator_wwn"],
                "name":name,
                "value":module.params[name]
            }

            rc, out, err = module.run_command(cmd)
            if rc != 0:
                module.fail_json(msg="Failed to define iSCSI ACL auth using command " + cmd, output=out, error=err)


    except OSError as e:
        module.fail_json(msg="Failed to check iSCSI ACL object - %s" % (e))

    module.exit_json(**result)


# import module snippets
from ansible.module_utils.basic import AnsibleModule
if __name__ == "__main__":
    main()
