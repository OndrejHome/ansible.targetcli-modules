#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_backstore
short_description: TargetCLI backstore module
description:
     - module for handling backstore objects in targetcli ('/backstores').
version_added: "0.1"
options:
  backstore_type:
    description:
      - Type of storage in TargetCLI
    required: true
    default: null
  backstore_name:
    description:
      - Name of backtore object in TargetCLI
    required: true
    default: null
  path:
    description:
      - path to device
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
define new block backstore from disk/LV /dev/c7vg/LV1
- targetcli_backstore: backstore_type=block backstore_name=test1 path=/dev/c7vg/LV1

remove block backstore from disk/LV /dev/c7vg/LV2
- targetcli_backstore: backstore_type=block backstore_name=test2 path=/dev/c7vg/LV2 state=absent

'''

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        backstore_type=dict(required=True),
                        backstore_name=dict(required=True),
                        path=dict(required=True),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        backstore_type = module.params['backstore_type']
        backstore_name = module.params['backstore_name']
        path = module.params['path']
        state = module.params['state']

        result = {}
        
        try:
            rc, out, err = module.run_command("targetcli '/backstores/%(backstore_type)s/%(backstore_name)s status'" % module.params)
            if rc == 0 and state == 'present':
                result['changed'] = False
            elif rc == 0 and state == 'absent':
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/backstores/%(backstore_type)s delete %(backstore_name)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to delete backstores object " + err)
            elif state == 'absent':
                result['changed'] = False
            else:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/backstores/%(backstore_type)s create %(backstore_name)s %(path)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to define backstores object " + err)
        except OSError as e:
            module.fail_json(msg="Failed to check backstore object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
