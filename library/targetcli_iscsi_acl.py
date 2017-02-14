#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_acl
short_description: TargetCLI iSCSI ACL module
description:
     - module for handling iSCSI ACL objects in targetcli ('/iscsi/.../tpg1/acls').
version_added: "0.1"
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
    choices: [present, absent]
notes:
   - Tested on CentOS 7.2
requirements: [ ]
author: "Ondrej Famera <ondrej-xa2iel8u@famera.cz>"
'''

EXAMPLES = '''
define new iscsi ACL client
- targetcli_iscsi_acl: wwn=iqn.1994-05.com.redhat:data initiator_wwn=iqn.1994-05.com.redhat:client1

remove iSCSI ACL
- targetcli_iscsi_acl: wwn=iqn.1994-05.com.redhat:data initiator_wwn=iqn.1994-05.com.redhat:client1 state=absent
'''

from subprocess import call

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        wwn=dict(required=True),
                        initiator_wwn=dict(required=True),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        wwn = module.params['wwn']
        initiator_wwn = module.params['initiator_wwn']
        state = module.params['state']

        result = {}
        
        try:
            retcode = subprocess.call("targetcli '/iscsi/" + wwn + "/tpg1/acls/" + initiator_wwn + " status'", shell=True) #FIXME think of something better than shell=True
            if retcode == 0 and state == 'present':
                result['changed'] = False
            elif retcode == 0 and state == 'absent':
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    retcode = call("targetcli '/iscsi/" + wwn + "/tpg1/acls delete " + initiator_wwn + "'", shell=True) #FIXME think of something better than shell=True
                    if retcode == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI ACL object")
            elif state == 'absent':
                result['changed'] = False
            else:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    retcode = call("targetcli '/iscsi/" + wwn + "/tpg1/acls create " + initiator_wwn + "'", shell=True) #FIXME think of something better than shell=True
                    if retcode == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to define iSCSI ACL object")
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI ACL object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
