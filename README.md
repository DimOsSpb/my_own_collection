# Ansible Collection - dimosspb_devopscourse.training
## Description

This collection contains:
- Мodule "my_own_module" and role for creates a text file on a remote host with a given content.
- Module "yc" for interaction with Yandex Cloud. In this version of the module, only the creation/update of virtual machines in the YC

> **! Notice**
This collection does not guarantee the correct work. This is the result of the solution of home work at the DevOps course and an example of using ANSIBLE collections, modules, roles... for automatic inventory configuration deployment.
## Dependencies

- For yc
  - Ansible >= 2.9
  - Python >= 3.6
  - Yandex Cloud SDK (pip install yandexcloud)
  - [Yandex Cloud access](https://yandex.cloud/en/docs/getting-started/)

## Installation

- [Download collection](https://raw.githubusercontent.com/DimOsSpb/my_own_collection/1.1.2/dimosspb_devopscourse-training-1.1.1.tar.gz) and install it:

```shell
ansible-galaxy collection install dimosspb_devopscourse-training-1.0.0.tar.gz
```

## Role instruction

[Role readme](roles/my_own_role/README.md)

## YC module instruction

```shell
ansible-doc dimosspb_devopscourse.training.yc
# OR
ansible-doc -M ./dimosspb_devopscourse/training/plugins/modules yc
```

## License

MIT

## Author Information

Dmitrii Osipov
dimosspb@vk.ru
