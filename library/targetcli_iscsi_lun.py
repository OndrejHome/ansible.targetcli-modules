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
module: targetcli_iscsi_lun
short_description: TargetCLI LUN module
description:
     - module for handling iSCSI LUN objects in targetcli ('/iscsi/.../tpg1/luns').
version_added: "2.0"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
    type: str
  backstore_type:
    description:
      - type of backstore object
    required: true
    default: null
    type: str
  backstore_name:
    description:
      - name of backstore object
    required: true
    default: null
    type: str
  auto_add_luns:
    description:
      - Automatically map LUN to all existing ACLs
    required: false
    default: True
    type: bool
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
- name: define new iSCSI LUN
  targetcli_iscsi_lun:
    wwn: 'iqn.1994-05.com.redhat:fastvm'
    backstore_type: 'block'
    backstore_name: 'test1'

- name: remove iSCSI LUN
  targetcli_iscsi_lun:
    wwn: 'iqn.1994-05.com.redhat:data'
    backstore_type: 'block'
    backstore_name: 'test2'
    state: 'absent'
'''

from distutils.spawn import find_executable


def main():
    module = AnsibleModule(
        argument_spec=dict(
            wwn=dict(required=True),
            backstore_type=dict(required=True),
            backstore_name=dict(required=True),
            auto_add_luns=dict(default=True, type='bool', required=False),
            state=dict(default="present", choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    lun_path = module.params['backstore_type'] + "/" + module.params['backstore_name']
    state = module.params['state']

    if find_executable('targetcli') is None:
        module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

    result = {}
    luns = {}

    try:
        # check if the iscsi target exists
        cmd = "targetcli '/iscsi/%(wwn)s/tpg1 status'" % module.params
        rc, out, err = module.run_command(cmd)
        if rc != 0 and state == 'present':
            result['changed'] = False
            module.fail_json(msg="ISCSI object doesn't exists", cmd=cmd, output=out, error=err)
        elif rc != 0 and state == 'absent':
            result['changed'] = False
            # ok iSCSI object doesn't exist so LUN is also not there --> success
        else:
            # lets parse the list of LUNs from the targetcli
            cmd = "targetcli '/iscsi/%(wwn)s/tpg1/luns ls'" % module.params
            rc, output, err = module.run_command(cmd)
            result['luns_output'] = output
            for row in output.split('\n'):
                row_data = row.split(' ')
                if len(row_data) < 2 or row_data[0] == 'luns':
                    continue
                if row_data[1] == "luns":
                    continue
                luns[row_data[5][1:]] = row_data[3][3:]
            if state == 'present' and lun_path in luns:
                # LUN is already there and present
                result['changed'] = False
                result['lun_id'] = luns[lun_path]
            elif state == 'absent' and lun_path not in luns:
                # LUN is not there and should not be there
                result['changed'] = False
            elif state == 'present' and lun_path not in luns:
                # create LUN
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    module.params['add_luns'] = 'true' if module.params['auto_add_luns'] else 'false'
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/luns create add_mapped_luns=%(add_luns)s /backstores/%(backstore_type)s/%(backstore_name)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to create iSCSI LUN object using command " + cmd, output=out, error=err)

            elif state == 'absent' and lun_path in luns:
                # delete LUN
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/iscsi/%(wwn)s/tpg1/luns delete lun" % module.params + luns[lun_path] + "'"
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to delete iSCSI LUN object using command " + cmd, output=out, error=err)
    except OSError as e:
        module.fail_json(msg="Failed to check iSCSI lun object - %s" % (e))
    module.exit_json(**result)


# import module snippets
from ansible.module_utils.basic import AnsibleModule
if __name__ == "__main__":
    main()
