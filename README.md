targetcli-modules
=================

Modules for interacting with targetcli command line utility.

Requirements
------------

*targetcli* utility is expected to be installed on machine.

Role Variables
--------------

None. This role is intended to be included as dependency.

Provided Modules
----------------
*targetcli_backstore* - create/delete backstore objects ('/backstore')

*targetcli_iscsi* - create/delete iscsi object ('/iscsi')

*targetcli_iscsi_lun* - add/remove luns to/from iscsi object ('/iscsi/.../tpg1/luns')

*targetcli_iscsi_acl* - add/remove acls to/from iscsi object ('/iscsi/.../tpg1/acls')

*targetcli_iscsi_portal* - add/remove portals to/from iscsi object ('/iscsi/.../tpg1/portals')

Example Playbook
----------------

Example playbook for including modules in your playbook

    - hosts: servers
      roles:
         - { role: 'OndrejHome.targetcli-modules' }

License
-------

GPLv3

Author Information
------------------

To get in touch with author you can use email ondrej-xa2iel8u@famera.cz or create a issue on github when requesting some feature.
