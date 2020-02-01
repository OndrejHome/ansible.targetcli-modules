#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_acl
short_description: TargetCLI iSCSI ACL module
description:
     - module for handling iSCSI ACL objects in targetcli ('/iscsi/.../tpg1/acls').
version_added: "2.1"
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
  initiator_user:
    description:
      - Username of iSCSI initiator (client)
        User-based authentication will be enabled, if non-empty
    required: false
    default: null
  initiator_password:
    description:
      - Password of iSCSI initiator user (client)
        Must be set, if initiator_user is set
    required: false
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
define new iscsi ACL client
- targetcli_iscsi_acl: wwn=iqn.1994-05.com.redhat:data initiator_wwn=iqn.1994-05.com.redhat:client1 initiator_user="" initiator_password=""

remove iSCSI ACL
- targetcli_iscsi_acl: wwn=iqn.1994-05.com.redhat:data initiator_wwn=iqn.1994-05.com.redhat:client1 state=absent
'''

from distutils.spawn import find_executable


def main():
        module = AnsibleModule(
                argument_spec=dict(
                        wwn=dict(required=True, type='str'),
                        initiator_wwn=dict(required=True, type='str'),
                        state=dict(default="present", choices=['present', 'absent']),
                        initiator_user=dict(required=False, type='str'),
                        initiator_password=dict(required=False, type='str')
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
                    if rc != 0:
                        module.fail_json(msg="Failed to define iSCSI ACL object using command " + cmd, output=out, error=err)
                    if  module.params['initiator_user']:
                        cmd = "targetcli '/iscsi/%(wwn)s/tpg1 set attribute authentication=1'" % module.params
                        rc, out, err = module.run_command(cmd)
                        if rc != 0:
                            module.fail_json(msg="Failed to enable user authentication using command " + cmd, output=out, error=err)
                        cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s set auth userid=%(initiator_user)s" % module.params
                        if module.params['initiator_password']:
                            cmd = cmd + " password=%(initiator_password)s" % module.params
                        cmd = cmd + "'"
                        rc, out, err = module.run_command(cmd)
                        if rc != 0:
                            module.fail_json(msg="Failed to set user authentication using command " + cmd, output=out, error=err)
                    module.exit_json(**result)
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI ACL object - %s" % (e))
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
