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
module: yc
short_description: Control of creating virtual machines in yandec cloud.
version_added: "1.0.0"
description: This is the initial level of interaction with Yandex Cloud. In this version of the module, only the creation of virtual machines in the YC cloud is available.
options:
    folder_id:
        description:
            - Yandex Cloud Folder ID.
        required: true
        type: str
    service_account_key_file:
        description:
            - Yandex Cloud service account key file path.
            - Use service_account_key_file or token
        required: true
        type: str
    token:
        description:
            - Yandex Cloud token.
            - Use service_account_key_file or token
        required: true
        type: str
    vms:
        description:
            - "List of virtual machines to create or manage."
        type: list
        elements: dict
        options:
            name:
                description:
                    - "The name of the virtual machine."
                type: str
                required: true
            zone:
                description:
                    - "The zone where the VM will be created."
                type: str
                required: true
            platform_id:
                description:
                    - "The platform type of the virtual machine."
                type: str
                default: "standard-v1"
            force_recreate:
                description:
                    - "If true, this VM will be forcibly recreated even if it exists."
                type: bool
                default: false
            force_restart:
                description:
                    - "If true, this VM will be forcibly restarted even if no changes detected."
                type: bool
                default: false
            resources_spec:
                description:
                    - "The resources specification of the VM."
                type: dict
                options:
                    cores:
                        description:
                            - "Number of CPU cores."
                        type: int
                        required: true
                    memory:
                        description:
                            - "Amount of RAM in GB."
                        type: int
                        required: true
                    core_fraction:
                        description:
                            - "CPU time fraction."
                        type: int
                        default: 0
            boot_disk_spec:
                description:
                    - "Boot disk configuration."
                type: dict
                options:
                    disk_spec:
                        description:
                            - "Disk parameters."
                        type: dict
                        options:
                            type_id:
                                description:
                                    - "Disk type, e.g., network-hdd or network-ssd."
                                type: str
                            size:
                                description:
                                    - "Disk size in GB."
                                type: int
                                required: true
                            image_id:
                                description:
                                    - "Image ID for the disk."
                                type: str
                                required: true
            network_interface_specs:
                description:
                    - "Network interfaces of the VM."
                type: dict
                options:
                    subnet_id:
                        description:
                            - "Subnet ID."
                        type: str
                        required: true
                    primary_v4_address_spec:
                        description:
                            - "Primary IPv4 address settings."
                        type: dict
                        options:
                            nat:
                                description:
                                    - "Enable NAT"
                                type: bool
                                default: true
            scheduling_policy:
                description:
                    - "VM scheduling policy."
                type: dict
                options:
                    preemptible:
                        description:
                            - "Allow preemptible VM."
                        type: bool
                        default: false
            metadata:
                description:
                    - "VM metadata, e.g., SSH keys."
                type: dict
                options:
                    ssh-keys:
                        description:
                            - "SSH keys for VM access in format 'user:ssh-rsa ...'."
                        type: str


# Specify this value according to your collection
#
# extends_documentation_fragment:
#     - dimosspb-devopscourse.training.yc

author:
    - Dmitrii Osipov (@DimOsSpb)
'''

EXAMPLES = r'''
- name: Managing virtual machines in yandec cloud
  hosts: localhost
  tasks:
    - dimosspb-devopscourse.training.yc:
        - name: Create or update VMs in Yandex Cloud
          vm:
            folder_id: "b1gg....5qo1tt"
            service_key_file: "/home/user/.secret/ya-sa.json"
            token: "{{ yc_token | default(omit) }}"
            vms:
              - name: "vm1"
                zone: "ru-central1-a"
                platform_id: "standard-v1"
                force_recreate: false
                force_restart: false
                resources_spec:
                  cores: 4
                  memory: 8
                  core_fraction: 50
                boot_disk_spec:
                  disk_spec:
                    type_id: "network-hdd"
                    size: 10
                    image_id: "fd80g4....8q9r0s1"
                network_interface_specs:
                  subnet_id: "subnet-12345678"
                  primary_v4_address_spec:
                    nat: true
                scheduling_policy:
                  preemptible: true
                metadata:
                  ssh-keys: "ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD..."
              - name: "vm2"
                zone: "ru-central1-b"
                resources_spec:
                  cores: 2
                  memory: 4
                  core_fraction: 50
                boot_disk_spec:
                  disk_spec:
                    type_id: "network-ssd"
                    size: 50
                    image_id: "fd80......r0s2"
                network_interface_specs:
                  subnet_id: "subnet-87654321"
                  primary_v4_address_spec:
                    nat: true
                scheduling_policy:
                  preemptible: true
                metadata:
                  ssh-keys: "ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD..."

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

import json
import grpc
import yandexcloud
from google.protobuf.field_mask_pb2 import FieldMask
from yandexcloud import SDK, RetryPolicy, ThrottlingMode  # type: ignore
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.compute.v1.instance_service_pb2 import GetInstanceRequest, InstanceView
from yandex.cloud.compute.v1.instance_pb2 import IPV4, Instance, SchedulingPolicy
from yandex.cloud.compute.v1.disk_service_pb2 import GetDiskRequest
from yandex.cloud.compute.v1.disk_service_pb2_grpc import DiskServiceStub
from yandex.cloud.compute.v1.instance_service_pb2 import (
    CreateInstanceMetadata,
    DeleteInstanceMetadata,
    StopInstanceMetadata,
    StartInstanceMetadata,
    ListInstancesRequest,
    UpdateInstanceRequest,
    StartInstanceRequest,
    StopInstanceRequest,
    DeleteInstanceRequest,
    CreateInstanceRequest,
    NetworkInterfaceSpec,
    OneToOneNatSpec,
    PrimaryAddressSpec,
    ResourcesSpec,
    AttachedDiskSpec,
)
from ansible.module_utils.basic import AnsibleModule
from typing import Dict, Any
from enum import Enum

class VMAction(str, Enum):
    CREATE = "create",
    RECREATE = "recreate"
    RESTART = "restart"
    INPLACE = "inplace"

FIELDS_SPEC = {
    "folder_id": {
        "action": VMAction.RECREATE,
        "type": "str",
        "required": True,
    },
    "service_key_file": {
        "action": VMAction.INPLACE,
        "type": "str",
        "required": True,
    },
    "token": {
        "action": VMAction.INPLACE,
        "type": "str",
        "default": None,
    },
    "vms": [
        {
            "type": "dict",
            "name": {
                "action": VMAction.INPLACE,
                "type": "str",
                "required": True,
            },
            "zone": {
                "action": VMAction.RECREATE,
                "type": "str",
                "required": True,
            },
            "platform_id": {
                "action": VMAction.RECREATE,
                "type": "str",
                "default": "standard-v1",
            },
            "force_recreate": {
                "action": VMAction.INPLACE,
                "type": "bool",
                "default": False,
            },
            "force_restart": {
                "action": VMAction.INPLACE,
                "type": "bool",
                "default": False,
            },
            "resources_spec": {
                "type": "dict",
                "cores": {
                    "action": VMAction.RESTART,
                    "type": "int",
                    "required": True,
                },
                "memory": {
                    "action": VMAction.RESTART,
                    "type": "int",
                    "required": True,
                },
                "core_fraction": {
                    "action": VMAction.RESTART,
                    "type": "int",
                    "default": 100,
                },
            },
            "boot_disk_spec": {
                "type": "dict",
                "disk_spec": {
                    "type": "dict",
                    "type_id": {
                        "action": VMAction.RECREATE,
                        "type": "str",
                    },
                    "size": {
                        "action": VMAction.RESTART,
                        "type": "int",
                        "required": True,
                    },
                    "image_id": {
                        "action": VMAction.RECREATE,
                        "type": "str",
                        "required": True,
                    },
                },
            },
            "network_interface_specs": {
                "type": "dict",
                "subnet_id": {
                    "action": VMAction.RESTART,
                    "type": "str",
                    "required": True,
                },
                "primary_v4_address_spec": {
                    "type": "dict",
                    "nat": {
                        "action": VMAction.RESTART,
                        "type": "bool",
                        "default": True,
                    },
                },
            },
            "scheduling_policy": {
                "type": "dict",
                "preemptible": {
                    "action": VMAction.RESTART,
                    "type": "bool",
                    "default": False,
                },
            },
            "metadata": {
                "type": "dict",
                # "user-data": {
                #     "action": VMAction.RESTART,
                #     "type": "str",
                # },
                "ssh-keys": {
                    "action": VMAction.RESTART,
                    "type": "str",
                },
            },
        },
    ],
}

def build_arguments(fields_spec):
    spec = {}

    for field, props in fields_spec.items():
        # Списки
        if isinstance(props, list):
            if len(props) != 1:
                raise ValueError(f"Список в field_map должен содержать ровно один элемент: {field}")
            elem_spec = props[0]
            # Отбираем реальные поля для options (исключая type/action/required/default)
            sub_fields = {k: v for k, v in elem_spec.items() if k not in ("type", "required", "default", "action")}
            spec[field] = {
                "type": "list",
                "elements": "dict",
                "options": build_arguments(sub_fields)
            }
            continue

        # Должно быть dict
        if not isinstance(props, dict):
            raise ValueError(f"Некорректное описание поля {field}: {props}")

        # Вложенный dict
        if props.get("type") == "dict":
            field_spec = {"type": "dict"}
            if "required" in props:
                field_spec["required"] = props["required"]
            if "default" in props:
                field_spec["default"] = props["default"]

            sub_fields = {k: v for k, v in props.items() if k not in ("type", "required", "default", "action")}
            if sub_fields:
                field_spec["options"] = build_arguments(sub_fields) # type: ignore
            spec[field] = field_spec
            continue

        # Простое поле
        if "type" in props:
            field_spec = {"type": props["type"]}
            if "required" in props:
                field_spec["required"] = props["required"]
            if "default" in props:
                field_spec["default"] = props["default"]
            spec[field] = field_spec
            continue

        raise ValueError(f"Некорректное описание поля {field}: {props}")

    return spec

def build_vm_diff(desired_vm: Dict, sdk, current_instance: Instance | None, fields_spec: Dict, original_args: Dict) -> Dict:
    diff = {
        "name": desired_vm["name"],
        "changes": [],
        "actions": {
            VMAction.INPLACE.value: False,
            VMAction.RESTART.value: False,
            VMAction.RECREATE.value: False,
            VMAction.CREATE.value: False
        },
        "changed": False
    }

    if current_instance is None:
        diff["changes"].append("VM does not exist, needs creation")
        diff["actions"][VMAction.CREATE.value] = True
        diff["changed"] = True
        return diff

    # Преобразуем текущий инстанс в простой dict для сравнения
    current_vm = {}

    # Базовые поля
    if hasattr(current_instance, 'name'):
        current_vm["name"] = current_instance.name
    if hasattr(current_instance, 'zone_id'):
        current_vm["zone"] = current_instance.zone_id
    if hasattr(current_instance, 'platform_id'):
        current_vm["platform_id"] = current_instance.platform_id

    # Ресурсы
    if hasattr(current_instance, 'resources'):
        current_vm["resources_spec"] = {
            "cores": current_instance.resources.cores,
            "memory": current_instance.resources.memory // (1024**3),  # bytes в GB
            "core_fraction": current_instance.resources.core_fraction
        }

    # Boot disk
    if hasattr(current_instance, 'boot_disk') and current_instance.boot_disk:

        disk_id = current_instance.boot_disk.disk_id
        disk_service = sdk.client(DiskServiceStub)
        disk = disk_service.Get(GetDiskRequest(disk_id=disk_id))
        if disk:
            disk_info = {
                "type_id": disk.type_id,
                "size": disk.size // (1024**3),
                "image_id": disk.source_image_id
            }
            current_vm["boot_disk_spec"] = {"disk_spec": disk_info}
            # print("Disk info:", disk_info)

    # Network interfaces
    if hasattr(current_instance, 'network_interfaces') and current_instance.network_interfaces:
        nic = current_instance.network_interfaces[0]
        nic_spec = {
            "subnet_id": nic.subnet_id,
            "primary_v4_address_spec": {
                "nat": bool(nic.primary_v4_address.one_to_one_nat)
            }

        }
        current_vm["network_interface_specs"] = nic_spec

    # Scheduling policy
    if hasattr(current_instance, 'scheduling_policy'):
        current_vm["scheduling_policy"] = {
            "preemptible": current_instance.scheduling_policy.preemptible
        }

    # Metadata
    current_vm["metadata"] = dict(current_instance.metadata or {})

    # print(f"DESIRED: {json.dumps(desired_vm, indent=2)}")
    # print(f"CURRENT: {json.dumps(current_vm, indent=2)}")

    # Рекурсивная функция для сравнения полей
    def compare_fields(desired: Any, current: Any, spec: Dict, path: str = ""):
        nonlocal diff

        if isinstance(spec, dict) and spec.get("type") == "dict":
            # Обработка словаря
            if desired is None or current is None:
                if desired is not None and current is None:
                    # Поле есть в desired, но нет в current
                    for field, field_spec in spec.items():
                        if field not in ["type", "required", "default", "action", "force_restart", "force_recreate"] and field in desired:
                            action = field_spec.get("action", VMAction.INPLACE)
                            diff["changes"].append(f"{path}.{field}: None -> {desired[field]}")
                            diff["actions"][action.value] = True
                return

            for field, field_spec in spec.items():
                if field in ["type", "required", "default", "action", "force_restart", "force_recreate"]:
                    continue

                field_path = f"{path}.{field}" if path else field
                if field in desired:
                    if field in current:
                        compare_fields(
                            desired[field],
                            current[field],
                            field_spec,
                            field_path
                        )
                    else:
                        # Поле есть в desired, но нет в current
                        action = field_spec.get("action", VMAction.INPLACE)
                        diff["changes"].append(f"{field_path}: None -> {desired[field]}")
                        diff["actions"][action.value] = True
                elif field in current:
                    # Поле есть в current, но нет в desired (должно быть удалено)
                    action = field_spec.get("action", VMAction.INPLACE)
                    diff["changes"].append(f"{field_path}: {current[field]} -> None")
                    diff["actions"][action.value] = True

        elif isinstance(spec, dict) and "action" in spec:
            # Простое поле с действием
            action = spec.get("action", VMAction.INPLACE)

            # Преобразуем типы для сравнения
            desired_value = desired
            current_value = current

            if spec.get("type") == "int":
                desired_value = int(desired) if desired is not None else None
                current_value = int(current) if current is not None else None
            elif spec.get("type") == "bool":
                desired_value = bool(desired) if desired is not None else None
                current_value = bool(current) if current is not None else None

            if desired_value != current_value:
                change_desc = f"{path}: {current_value} -> {desired_value}"
                diff["changes"].append(change_desc)
                diff["actions"][action.value] = True

    # Сравниваем поля согласно FIELDS_SPEC
    for field, field_spec in fields_spec.items():
        if field in ["type", "required", "default", "action", "force_restart", "force_recreate"]:
            continue

        field_path = field
        if field in desired_vm:
            if field in current_vm:
                compare_fields(
                    desired_vm[field],
                    current_vm[field],
                    field_spec,
                    field_path
                )
            else:
                # Поле есть в desired, но нет в current
                action = field_spec.get("action", VMAction.INPLACE) if isinstance(field_spec, dict) else VMAction.INPLACE
                diff["changes"].append(f"{field_path}: None -> {desired_vm[field]}")
                diff["actions"][action.value] = True
        elif field in current_vm:
            # Поле есть в current, но нет в desired
            action = field_spec.get("action", VMAction.INPLACE) if isinstance(field_spec, dict) else VMAction.INPLACE
            diff["changes"].append(f"{field_path}: {current_vm[field]} -> None")
            diff["actions"][action.value] = True

    diff["changed"] = len(diff["changes"]) > 0
    return diff

def create_instance(sdk, instance_service , vm_spec, instance: Instance | None):
    #
    # Функция удалит instance если он определен и создаст новый
    # Вернет None или ошибку
    #
    if instance:
        del_op = instance_service.Delete(DeleteInstanceRequest(instance_id=instance.id))
        try:
            sdk.wait_operation_and_get_result(del_op, meta_type=DeleteInstanceMetadata)
        except Exception as e:
            return e


    t_resources_spec = vm_spec.get("resources_spec", {})
    t_boot_disk_spec = vm_spec.get("boot_disk_spec", {})
    t_disk_spec = t_boot_disk_spec.get("disk_spec", {})
    t_network_interface_specs = vm_spec.get("network_interface_specs", {})
    t_primary_v4_address_spec = t_network_interface_specs.get("primary_v4_address_spec", {})
    t_metadata = vm_spec.get("metadata", {})
    t_scheduling_policy = vm_spec.get("scheduling_policy", {})

    # t_key = t_metadata.get("ssh_keys")
    # print(f"t_metadata_ssh_keys: {t_key}")

    # image_service = sdk.client(ImageServiceStub)
    # image = image_service.Get(GetImageRequest(image_id="fd80g4m9n1o7p8q9r0s1"))


    create_op = instance_service.Create(

        CreateInstanceRequest(
            folder_id=vm_spec.get("folder_id"),
            name=vm_spec.get("name"),
            zone_id=vm_spec.get("zone"),
            platform_id=vm_spec.get("platform_id"),

            resources_spec=ResourcesSpec(
                cores=t_resources_spec.get("cores"),
                memory=t_resources_spec.get("memory")* 1024**3,
                core_fraction=t_resources_spec.get("core_fraction"),
            ),
            boot_disk_spec=AttachedDiskSpec(
                auto_delete=True,
                disk_spec=AttachedDiskSpec.DiskSpec(
                    type_id=t_disk_spec.get("type_id"),
                    size=t_disk_spec.get("size") * 1024**3,
                    image_id=t_disk_spec.get("image_id"),
                ),
            ),
            network_interface_specs=[
                NetworkInterfaceSpec(
                    subnet_id=t_network_interface_specs.get("subnet_id"),
                    primary_v4_address_spec=PrimaryAddressSpec(
                        one_to_one_nat_spec=OneToOneNatSpec(
                            ip_version=IPV4,
                        ) if t_primary_v4_address_spec.get("nat", True) else None
                    ),
                ),
            ],
            metadata={
                "ssh-keys": f'{t_metadata.get("ssh-keys")}',
            },
            scheduling_policy=SchedulingPolicy(
                preemptible = t_scheduling_policy.get("preemptible", True),
            )
        )
    )
    try:
        sdk.wait_operation_and_get_result(create_op, meta_type=CreateInstanceMetadata)
    except Exception as e:
        return e
    return None

def update_instance(sdk, instance_service, vm_spec, instance, vm_diff):
    update_mask = FieldMask()
    request_fields = {}

    resource_changes = any(change.startswith("resources_spec.") for change in vm_diff.get("changes", []))
    if resource_changes:
        resources = vm_spec.get("resources_spec", {})
        update_mask.paths.append("resources_spec")
        request_fields["resources_spec"] = ResourcesSpec(
            cores=resources.get("cores", 2),
            memory=resources.get("memory", 2) * 1024**3,
            core_fraction=resources.get("core_fraction", 100)
        )

    metadata_changes = any(change.startswith("metadata.") for change in vm_diff.get("changes", []))
    if metadata_changes:
        metadata = vm_spec.get("metadata", {})
        update_mask.paths.append("metadata")
        request_fields["metadata"] = metadata

    scheduling_changes = any(change.startswith("scheduling_policy.") for change in vm_diff.get("changes", []))
    if scheduling_changes:
        scheduling = vm_spec.get("scheduling_policy", {})
        update_mask.paths.append("scheduling_policy")
        request_fields["scheduling_policy"] = SchedulingPolicy(
            preemptible=scheduling.get("preemptible", False)
        )

    if not update_mask.paths:
        return None

    try:
        if resource_changes:
            stop_op = instance_service.Stop(StopInstanceRequest(instance_id=instance.id))
            sdk.wait_operation_and_get_result(stop_op)

        update_request = UpdateInstanceRequest(
            instance_id=instance.id,
            update_mask=update_mask,
            **request_fields
        )

        update_op = instance_service.Update(update_request)
        sdk.wait_operation_and_get_result(update_op)

        if resource_changes:
            start_op = instance_service.Start(StartInstanceRequest(instance_id=instance.id))
            sdk.wait_operation_and_get_result(start_op)

        return None
    except Exception as e:
        if resource_changes:
            try:
                start_op = instance_service.Start(StartInstanceRequest(instance_id=instance.id))
                sdk.wait_operation_and_get_result(start_op)
            except:
                pass
        return e

def apply_vm_diff(sdk, instance_service, vm_spec: Dict, instance: Instance | None, vm_diff: Dict) -> Dict:
    result = vm_diff.copy()

    if not vm_diff["changed"]:
        result["status"] = "unchanged"
        return result

    try:
        # Определяем максимальное требуемое действие
        required_action = VMAction.INPLACE
        if vm_diff["actions"][VMAction.CREATE.value]:
            required_action = VMAction.CREATE
        elif vm_diff["actions"][VMAction.RECREATE.value]:
            required_action = VMAction.RECREATE
        elif vm_diff["actions"][VMAction.RESTART.value]:
            required_action = VMAction.RESTART

        if required_action == VMAction.CREATE:
            res = create_instance(sdk, instance_service, vm_spec, None)
            if res:
                result["status"] = "error"
                result["error"] = str(res)
            else:
                result["status"] = "created"

        elif required_action == VMAction.RECREATE:
            res = create_instance(sdk, instance_service, vm_spec, instance)
            if res:
                result["status"] = "error"
                result["error"] = str(res)
            else:
                result["status"] = "recreated"

        elif required_action == VMAction.RESTART:
            if instance:

                res = update_instance(sdk, instance_service, vm_spec, instance, vm_diff)
                if res:
                    result["status"] = "error"
                    result["error"] = str(res)
                else:
                    result["status"] = "restarted"
            else:
                result["status"] = "error"
                result["error"] = "Instance not found for restart"

        elif required_action == VMAction.INPLACE:
            if instance:
                res = update_instance(sdk, instance_service, vm_spec, instance, vm_diff)
                if res:
                    result["status"] = "error"
                    result["error"] = str(res)
                else:
                    result["status"] = "updated_in_place"
            else:
                result["status"] = "error"
                result["error"] = "Instance not found for update"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    # Очищаем вывод - оставляем только нужные поля
    clean_result = {
        "name": result.get("name"),
        "changed": result.get("changed", False),
        "status": result.get("status", "unknown")
    }

    if result.get("changes"):
        clean_result["changes"] = result["changes"]

    if "error" in result:
        clean_result["error"] = result["error"]

    return clean_result

def process_vm(sdk, instance_service, module, instances, vm):

    # Берём только явно указанные поля
    original_vm_args = getattr(vm, "_original_args", vm)

    instance: Instance | None = None
    for i in instances:
        if i.name == vm["name"]:
            instance = i
            break

    vm_diff = build_vm_diff(vm, sdk, instance, FIELDS_SPEC["vms"][0], original_vm_args)

    # Проверка флагов force_recreate/force_restart
    if vm_diff["actions"][VMAction.RECREATE.value] and not vm.get("force_recreate", False):
        module.fail_json(
            msg="Changes require VM recreation (use force_recreate to allow)",
            diff=vm_diff,
        )
    if vm_diff["actions"][VMAction.RESTART.value] and not vm.get("force_restart", False):
        module.fail_json(
            msg="Changes require VM restart (use force_restart to allow)",
            diff=vm_diff,
        )

    if not module.check_mode:
        vm["folder_id"] = module.params['folder_id']
        vm_diff = apply_vm_diff(sdk, instance_service, vm, instance, vm_diff)
    else:
        status_info = "would be changed" if vm_diff["changed"] else "no changes"

        if vm_diff["actions"][VMAction.RESTART.value]:
            status_info += " (requires restart)"
        elif vm_diff["actions"][VMAction.RECREATE.value]:
            status_info += " (requires recreate)"
        elif vm_diff["actions"][VMAction.CREATE.value]:
            status_info += " (requires create)"

        clean_vm_diff = {
            "name": vm_diff.get("name"),
            "changed": vm_diff.get("changed", False),
            "status": f"Check mode: {status_info}"
        }

        if vm_diff.get("changes"):
            clean_vm_diff["changes"] = vm_diff["changes"]

        return clean_vm_diff

    return vm_diff

def run_module():

    module = AnsibleModule(
        argument_spec = build_arguments(FIELDS_SPEC),
        supports_check_mode=True

    )


    token = module.params['token']
    folder_id = module.params['folder_id']
    skey_file = module.params['service_key_file']

    retry_policy = RetryPolicy(
        max_attempts=5,
        status_codes=(grpc.StatusCode.UNAVAILABLE,)
    )

    if token:
        sdk = SDK(token=token, retry_policy=retry_policy)
    else:
        with open(skey_file) as infile:
            sdk = SDK(service_account_key=json.load(infile), retry_policy=retry_policy)

    instance_service = sdk.client(InstanceServiceStub)

    # Получаем короткий список
    short_instances = instance_service.List(
        ListInstancesRequest(folder_id=folder_id)
    )

    # Список полных объектов
    instances = [
        instance_service.Get(GetInstanceRequest(instance_id=inst.id, view=InstanceView.FULL ))
        for inst in short_instances.instances
    ]

    result_instances = []
    for vm in module.params["vms"]:
        vm_diff = process_vm(sdk, instance_service, module, instances, vm)
        result_instances.append(vm_diff)

    final_instances = []
    for vm_result in result_instances:
        clean_result = {
            "name": vm_result.get("name"),
            "changed": vm_result.get("changed", False),
            "status": vm_result.get("status", "unknown")
        }

        if vm_result.get("changes"):
            clean_result["changes"] = vm_result["changes"]

        if "error" in vm_result:
            clean_result["error"] = vm_result["error"]

        final_instances.append(clean_result)

    module.exit_json(
        changed=any(vm.get("changed", False) for vm in final_instances),
        instances=final_instances,
    )


def main():
    run_module()


if __name__ == '__main__':
    main()
