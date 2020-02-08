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
module: targetcli_backstore
short_description: TargetCLI backstore module
description:
     - module for handling backstore objects in targetcli ('/backstores').
version_added: "2.0"
options:
  backstore_type:
    description:
      - Type of storage in TargetCLI (block, fileio, pscsi, ramdisk)
    required: true
    default: null
  backstore_name:
    description:
      - Name of backtore object in TargetCLI
    required: true
    default: null
  options:
    description:
      - options for create operation when creating backstore object
    required: false
    default: null
  attributes:
    description:
      - Attributes for the defined LUN
    required: false
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
- name: define new block backstore from disk/LV /dev/c7vg/LV1
  targetcli_backstore:
    backstore_type: 'block'
    backstore_name: 'test1'
    options: '/dev/c7vg/LV1'

- name: define new block backstore from disk/LV /dev/c7vg/LV2 with attributes
  argetcli_backstore:
    backstore_type: 'block'
    backstore_name: 'test2'
    options: '/dev/c7vg/LV2'
    attributes: {{ "emulate_tpu=1" }}

- name: remove block backstore from disk/LV /dev/c7vg/LV2
  targetcli_backstore:
    backstore_type: 'block'
    backstore_name: 'test2'
    state: 'absent'
'''

from distutils.spawn import find_executable


def main():
        module = AnsibleModule(
                argument_spec=dict(
                        backstore_type=dict(required=True),
                        backstore_name=dict(required=True),
                        options=dict(required=False),
                        attributes=dict(required=False),
                        state=dict(default="present", choices=['present', 'absent']),
                ),
                supports_check_mode=True
        )

        attributes = module.params['attributes']

        state = module.params['state']
        if state == 'present' and not module.params['options']:
            module.fail_json(msg="Missing options parameter needed for creating backstore object")

        if find_executable('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

        result = {}

        try:
            rc, out, err = module.run_command("targetcli '/backstores/%(backstore_type)s/%(backstore_name)s status'" % module.params)
            if rc == 0 and state == 'present':
                result['changed'] = False
            elif rc == 0 and state == 'absent':
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/backstores/%(backstore_type)s delete %(backstore_name)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to delete backstores object using command " + cmd, output=out, error=err)
            elif state == 'absent':
                result['changed'] = False
            else:
                result['changed'] = True
                if module.check_mode:
                    module.exit_json(**result)
                else:
                    cmd = "targetcli '/backstores/%(backstore_type)s create %(backstore_name)s %(options)s'" % module.params
                    rc, out, err = module.run_command(cmd)
                    if rc == 0:
                        if attributes:
                            cmd = "targetcli '/backstores/%(backstore_type)s/%(backstore_name)s set attribute %(attributes)s'" % module.params
                            rc, out, err = module.run_command(cmd)
                            if rc == 0:
                                module.exit_json(**result)
                            else:
                                module.fail_json(msg="Failed to set LUN's attributes using cmd "+cmd, output=out, error=err)
                        else:
                            module.exit_json(**result)
                    else:
                        module.fail_json(msg="Failed to define backstores object using command " + cmd, output=out, error=err)
        except OSError as e:
            module.fail_json(msg="Failed to check backstore object - %s" % (e))
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
