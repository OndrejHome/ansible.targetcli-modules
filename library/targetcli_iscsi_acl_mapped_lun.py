#!/usr/bin/python
# Copyright: (c) 2021, Ondrej Famera <ondrej-xa2iel8u@famera.cz>
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
module: targetcli_iscsi_acl_mapped_lun
short_description: TargetCLI iSCSI ACL module for mapped luns
description:
     - module for handling iSCSI ACL mapped_lun objects in targetcli ('/iscsi/.../tpg1/acls/.../').
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
  state:
    description:
      - Should the object be present or absent from TargetCLI configuration
    required: false
    default: present
    choices: [present, absent]
    type: str
  backstore_name:
    description:
      - name of backstore object
    required: true
    default: null
    type: str
  backstore_type:
    description:
      - type of backstore object
    required: true
    default: null
    type: str
  mapped_lun_id:
    description:
      - LUN ID of added backstore object (only needed when creating mapped LUN)
    required: false
    default: null
    type: int
notes:
   - Tested on CentOS 7.9
requirements: [ ]
author: "Ondrej Famera (@OndrejHome)"
'''

EXAMPLES = '''
- name: define new iscsi ACL client mapped LUN
  targetcli_iscsi_acl_mapped_lun:
    wwn: 'iqn.1994-05.com.redhat:data'
    initiator_wwn: 'iqn.1994-05.com.redhat:client1'
    backstore_type: 'block'
    backstore_name: 'test2'
    mapped_lun_id: '2'

- name: remove iSCSI ACL mapped LUN
  targetcli_iscsi_acl_mapped_lun:
    wwn: 'iqn.1994-05.com.redhat:data'
    initiator_wwn: 'iqn.1994-05.com.redhat:client1'
    backstore_type: 'block'
    backstore_name: 'test2'
    state: 'absent'
'''

from distutils.spawn import find_executable


def main():
    module = AnsibleModule(
        argument_spec=dict(
            wwn=dict(required=True, type='str'),
            initiator_wwn=dict(required=True, type='str'),
            backstore_name=dict(required=True, type='str'),
            backstore_type=dict(required=True, type='str'),
            mapped_lun_id=dict(required=False, type='int'),
            state=dict(default="present", choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    state = module.params['state']

    if find_executable('targetcli') is None:
        module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

    result = {}
    luns = {}

    if state == 'present' and not module.params['mapped_lun_id']:
        module.fail_json(msg="Missing mapped_lun_id parameter for creating mappen LUN", output=out, error=err)

    try:
        cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s status'" % module.params
        rc, out, err = module.run_command(cmd)
        if rc != 0 and state == 'present':
            module.fail_json(msg="Target WWN or target WWN ACL doesn't exists.", output=out, error=err)
        elif rc != 0 and state == 'absent':
            result['changed'] = False
        # at this point we know that WWN target and ACL exists, so lets get list of LUNs in it
        cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s ls'" % module.params
        rc, output, err = module.run_command(cmd)
        result['luns_output'] = output
        for row in output.split('\n'):
            row_data = row.split(' ')
            if len(row_data) < 2 or row_data[0] == "%(initiator_wwn)s" % module.params:
                continue
            if row_data[1] == "%(initiator_wwn)s" % module.params:
                continue
            luns[row_data[6]] = row_data[3][10:]
            # o- iqn.2003-01.org.linux-iscsi.client1:111 .......... [Mapped LUNs: 2]
            #  o- mapped_lun0 .............................. [lun0 block/test1 (rw)]
            #  o- mapped_lun2 .............................. [lun1 block/test2 (rw)]
            #     ^3                                         ^5    ^6
        result['luns'] = luns
        lun_path = module.params['backstore_type'] + "/" + module.params['backstore_name']
        result['lun_path'] = lun_path
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
                cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s create mapped_lun=%(mapped_lun_id)s tpg_lun_or_backstore=/backstores/%(backstore_type)s/%(backstore_name)s'" % module.params
                rc, out, err = module.run_command(cmd)
                if rc == 0:
                    module.exit_json(**result)
                else:
                    module.fail_json(msg="Failed to create iSCSI ACL mapped_lun object using command " + cmd, output=out, error=err)
        elif state == 'absent' and lun_path in luns:
            # delete LUN
            result['changed'] = True
            if module.check_mode:
                module.exit_json(**result)
            else:
                cmd = "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s delete " % module.params + luns[lun_path] + "'"
                rc, out, err = module.run_command(cmd)
                if rc == 0:
                    module.exit_json(**result)
                else:
                    module.fail_json(msg="Failed to delete iSCSI ACL LUN object using command " + cmd, output=out, error=err)
    except OSError as e:
        module.fail_json(msg="Failed to check iSCSI ACL LUN object - %s" % (e))
    module.exit_json(**result)


# import module snippets
from ansible.module_utils.basic import AnsibleModule
if __name__ == "__main__":
    main()
