## Description

It role creates a text file on a remote host with a given content.

> **! Notice**
This role does not guarantee the correct work. This is the result of the solution of home work at the DevOPS course and an example of using ANSIBLE collections, modules, roles... for automatic inventory configuration deployment.

## Role Variables

| Variables name | Default value      | Description |
|----------------|--------------------|-------------|
| default_content | "Hello from role!!" | Content of the file |
| default_path | "~/tmp/Hello.txt" | Path to the file |

## Dependencies

Not found

## Installation

```shell
ansible-galaxy collection install dimosspb_devopscourse-training-1.0.0.tar.gz
```

## Example Playbook
```yaml
- name: Add file
  hosts: all
  roles:
    - dimosspb_devopscourse.training.my_own_role
```
## License

MIT

## Author Information

Dmitrii Osipov
dimosspb@vk.ru
