#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi
short_description: TargetCLI iSCSI target module
description:
     - module for handling iSCSI objects in targetcli ('/iscsi').
version_added: "0.1"
options:
  wwn:
    description:
      - WWN of iSCSI target
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

#FIXME
EXAMPLES = '''
define new iscsi target
- targetcli_iscsi: wwn=iqn.1994-05.com.redhat:data

remove existing target
- targetcli_iscsi: wwn=iqn.1994-05.com.redhat:hell state=absent
'''

from subprocess import call

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        wwn=dict(required=True),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        wwn = module.params['wwn']
        state = module.params['state']

        result = {}
        
        try:
            retcode = subprocess.call("targetcli '/iscsi/" + wwn + "/tpg1 status'", shell=True) #FIXME think of something better than shell=True
            if retcode == 0 and state == 'present':
                result['changed'] = False
            elif retcode == 0 and state == 'absent':
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    retcode = call("targetcli '/iscsi delete " + wwn + "'", shell=True) #FIXME think of something better than shell=True
                    if retcode == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI object")
            elif state == 'absent':
                result['changed'] = False
            else:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    retcode = call("targetcli '/iscsi create " + wwn + "'", shell=True) #FIXME think of something better than shell=True
                    if retcode == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to define iSCSI object")
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
