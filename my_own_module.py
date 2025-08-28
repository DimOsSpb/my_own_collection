#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# Old block - help: https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/boilerplate.html
#
# from __future__ import (absolute_import, division, print_function)
# __metaclass__ = type
# For Python 3.12+
#
from __future__ import annotations
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_own_module
short_description: This is my test module.
version_added: "1.0.0"
description: The module creates a text file on a remote host with a given content.
options:
    path:
        description: The path to the file that will be created.
        required: true
        type: str
    content:
        description:
            - The contents that will be written to the file.
            - You can indicate both a single-line line and a multi-line YAML block.
        required: false
        type: str
        default: ""

# Specify this value according to your collection
#
# extends_documentation_fragment:
#     - dimosspb-devopscourse.training.my_own_module

author:
    - Dmitrii Osipov (@DimOsSpb)
'''

EXAMPLES = r'''
# Create a file with simple content
- name: Create hello.txt with "Hello World!"
  dimosspb-devopscourse.training.my_own_module:
    path: /tmp/hello.txt
    content: "Hello, World!"

# Create a configuration file with multi-line content
- name: Create configuration file example
  hosts: all
  tasks:
    - dimosspb-devopscourse.training.my_own_module:
        path: /etc/myapp/config.conf
        content: |
          option1 = true
          option2 = value
          # configuration comment
          name = app-{{ inventory_hostname }}

# Create an empty file
- name: Create empty file
  dimosspb-devopscourse.training.my_own_module:
    path: /tmp/empty.txt
'''

RETURN = r'''
changed:
    description: File was created or its content was changed.
    type: bool
    returned: always
    sample: true

created:
    description: Indicates if the file was created.
    type: bool
    returned: always
    sample: true

updated:
    description: Indicates if the file exist and its content was updated.
    type: bool
    returned: always
    sample: true
'''

from ansible.module_utils.basic import AnsibleModule
import os


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=False, default='')
    )

    result = dict(
        changed=False,
        created=False,
        updated=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    path = module.params['path']
    abs_path = os.path.abspath(os.path.expanduser(path))
    content = module.params['content']

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    file_exist = os.path.exists(abs_path)
    old_content = None

    if file_exist:
        with open(abs_path, 'r', encoding='utf-8') as f:
            old_content = f.read()

    if module.check_mode:
        if not file_exist:
            result['changed'] = True
            result['created'] = True
        elif old_content != content:
            result['changed'] = True
            result['updated'] = True
        module.exit_json(**result)

    if not file_exist:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        result['changed'] = True
        result['created'] = True

    elif old_content != content:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        result['changed'] = True
        result['updated'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
