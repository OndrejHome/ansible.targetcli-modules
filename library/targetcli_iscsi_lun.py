#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_lun
short_description: TargetCLI LUN module
description:
     - module for handling iSCSI LUN objects in targetcli ('/iscsi/.../tpg1/luns').
version_added: "0.1"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
  backstore_type:
    description:
      - type of backstore object
    required: true
    default: null
  backstore_name:
    description:
      - name of backstore object
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
define new iSCSI LUN
- targetcli_iscsi_lun: wwn=iqn.1994-05.com.redhat:fastvm backstopre_type=block backstore_name=test1

remove iSCSI LUN
- targetcli_iscsi_lun: wwn=iqn.1994-05.com.redhat:hell backstopre_type=block backstore_name=test2 state=absent
'''

from subprocess import call

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        wwn=dict(required=True),
                        backstore_type=dict(required=True),
                        backstore_name=dict(required=True),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        wwn = module.params['wwn']
        lun_path = module.params['backstore_type']+"/"+module.params['backstore_name']
        state = module.params['state']

        result = {}
        luns = {}
        
        try:
            # check if the iscsi target exists
            retcode = subprocess.call("targetcli '/iscsi/" + wwn + "/tpg1 status'", shell=True) #FIXME think of something better than shell=True
            if retcode <> 0 and state == 'present':
                result['changed'] = False
                module.fail_json(msg="ISCSI object doesn't exists")
            elif retcode <> 0 and state == 'absent':
                result['changed'] = False
                # ok iSCSI object doesn't exist so LUN is also not there --> success 
            else:
                # lets parse the list of LUNs from the targetcli
                output = subprocess.check_output("targetcli '/iscsi/" + wwn + "/tpg1/luns ls'",  shell=True)
                for row in output.split('\n'):
                    row_data = row.split(' ')
                    if len(row_data) < 2 or row_data[0] == 'luns':
                        continue
                    if row_data[1] == "luns":
                        continue
                    luns[row_data[5][1:]] = row_data[3][3:]
                if state == 'present' and luns.has_key(lun_path):
                    # LUN is already there and present
                    result['changed'] = False
                    result['lun_id'] = luns[lun_path]
                elif state == 'absent' and not luns.has_key(lun_path):
                    # LUN is not there and should not be there
                    result['changed'] = False
                elif state == 'present' and not luns.has_key(lun_path):
                    # create LUN
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        retcode = call("targetcli '/iscsi/" + wwn + "/tpg1/luns create /backstores/" + lun_path + "'", shell=True) #FIXME think of something better than shell=True
                        if retcode == 0:
                            module.exit_json(changed=True)
                        else:
                            module.fail_json(msg="Failed to create iSCSI LUN object")

                elif state == 'absent' and luns.has_key(lun_path):
                    # delete LUN
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        retcode = call("targetcli '/iscsi/" + wwn + "/tpg1/luns delete lun" + luns[lun_path] + "'", shell=True) #FIXME think of something better than shell=True
                        if retcode == 0:
                            module.exit_json(changed=True)
                        else:
                            module.fail_json(msg="Failed to create iSCSI LUN object")
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI ACL object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
