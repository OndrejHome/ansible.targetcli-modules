#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi
short_description: TargetCLI iSCSI target module
description:
     - module for handling iSCSI objects in targetcli ('/iscsi').
version_added: "2.0"
options:
  wwn:
    description:
      - WWN of iSCSI target
    required: true
    default: null
  attributes:
    description:
      - Attributes for the defined target
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
define new iscsi target
- targetcli_iscsi: wwn=iqn.1994-05.com.redhat:data attributes={{ "demo_mode_write_protect=0" }}

remove existing target
- targetcli_iscsi: wwn=iqn.1994-05.com.redhat:hell state=absent
'''

from distutils.spawn import find_executable

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        wwn=dict(required=True),
                        attributes=dict(required=False),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        wwn = module.params['wwn']
        attributes = module.params['attributes']
        state = module.params['state']

        if find_executable('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

        result = {}
        
        try:
            rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1 status'" % module.params)
            if rc == 0 and state == 'present':
                result['changed'] = False
            elif rc == 0 and state == 'absent':
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/iscsi delete %(wwn)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI object")
            elif state == 'absent':
                result['changed'] = False
            else:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/iscsi create %(wwn)s'" % module.params)
                    if rc == 0:
                        if attributes:
                            rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1 set attribute %(attributes)s'" % module.params)
                            if rc == 0:
                                module.exit_json(changed=True)
                            else:
                                module.fail_json(msg="Failed to set TPG's attributes")
                        else:
                            module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to define iSCSI object")
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
