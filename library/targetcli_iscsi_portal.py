#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_portal
short_description: TargetCLI iSCSI portal module
description:
     - module for handling iSCSI portal objects in targetcli ('/iscsi/.../tpg1/portals').
version_added: "2.4"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
  ip:
    description:
      - IP where the target shall be exported on
    required: true
    default: null
  port:
    description:
      - port where the target shall be exported on
    required: false
    default: 3260
  state:
    description:
      - Should the object be present or absent from TargetCLI configuration
    required: false
    default: present
    choices: [present, absent]
notes:
   - tested on Ubuntu 16.04
requirements: [ ]
author: "Michel Weitbrecht <michel.weitbrecht@stuvus.uni-stuttgart.de>"
'''

EXAMPLES = '''
define new portal with default port
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest ip=192.168.178.55

define new portal with non-default port
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest ip=192.168.178.55 port=2881

remove the portal
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest ip=192.168.178.55 port=2881 state=absent
'''

from distutils.spawn import find_executable

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        wwn=dict(required=True),
                        ip=dict(required=True),
                        port=dict(default="3260"),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        state = module.params['state']

        if find_executable('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

        result = {}
        
        try:
            rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1/portals/%(ip)s:%(port)s status'" % module.params)
            if rc == 0 and state == 'present':
                result['changed'] = False
            elif rc == 0 and state == 'absent':
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1/portals delete %(ip)s %(port)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI portal object")
            elif state == 'absent':
                result['changed'] = False
            else:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1/portals create %(ip)s %(port)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to define iSCSI portal object")
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI portal object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
