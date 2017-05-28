#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_auth
short_description: TargetCLI iSCSI authentication module
description:
     - module for setting iSCSI authentication parameters in targetcli ('/iscsi/.../tpg1').
version_added: "2.4"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
  userid:
    description:
      - userid needed by the initiator to access devices on this target
    required: true
    default: null
  password:
    description:
      - password needed by the initiator to access devices on this target
    required: true
    default: null
  userid_mutual:
    description:
      - mutual userid to ensure the initiator accesses the correct target
    required: false
    default: null
  password_mutual:
    description:
      - mutual password to ensure the initiator accesses the correct target
    required: false
    default: null
notes:
   - tested on Ubuntu 16.04
requirements: [ ]
author: "Michel Weitbrecht <michel.weitbrecht@stuvus.uni-stuttgart.de>"
'''

EXAMPLES = '''
set userid and password
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest userid=hypervisor01 password=12345

reset userid and password
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest userid=None password=None

set userid and password as well as mutual userid and password
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest userid=hypervisor01 password=12345 userid_mutual=storage01 password_mutual=54321

'''

from distutils.spawn import find_executable
import re
def main():
        module = AnsibleModule(
                argument_spec = dict(
                        wwn=dict(required=True),
                        userid=dict(required=True),
                        password=dict(required=True, no_log=True),
                        userid_mutual=dict(default="None"),
                        password_mutual=dict(default="None", no_log=True),
                ),
                supports_check_mode=True
        )

        if find_executable('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")
  
        try:
            rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1/ get auth'" % module.params)
            userid = re.search('(?<=\n\n  userid\=).*(?=\n)',out).group(0)
            password = re.search('(?<=\n\n  password\=).*(?=\n)',out).group(0)
            userid_mutual = re.search('(?<=\n\n  userid_mutual\=).*(?=\n)',out).group(0)
            password_mutual = re.search('(?<=\n\n  password_mutual\=).*(?=\n)',out).group(0)
            
            if rc != 0:
                module.fail_json(msg="failed to read authentication parameters")

            if password != module.params['password'] or userid != module.params['userid'] or password_mutual != module.params['password_mutual'] or userid_mutual != module.params['userid_mutual']:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1 set auth password=%(password)s userid=%(userid)s password_mutual=%(password_mutual)s userid_mutual=%(userid_mutual)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to set iSCSI authentication parameters")

        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI authentication - %s" %(e) )
        module.exit_json()

# import module snippets
from ansible.module_utils.basic import *
main()
