#!/bin/python

# MIT License
#
# Copyright (c) 2023 ArthurPV
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import os
from dataclasses import dataclass

PLAYBOOKS_DIR = "playbooks"


def create_file_with_content(path: str, content: str) -> None:
    path_split = path.split("/")

    if len(path_split) > 1:
        for i in range(len(path_split) - 1):
            dir = "/".join(path_split[: i + 1])

            if os.path.exists(dir) is False:
                os.mkdir(dir)

    with open(path, "w") as f:
        f.write(content)


def print_title(title: str) -> None:
    print("===========================================")
    print(title)
    print("===========================================")


@dataclass
class Inventory:
    ip: str
    user: str
    key_path: str

    def path() -> str:
        return "inventory.ini"

    def __str__(self) -> str:
        """
        Return the content of the `inventory.ini` file
        """
        return f"""[archlinux_server]
{self.ip} ansible_user={self.user} ansible_ssh_private_key_file={self.key_path}
"""


def inventory_configuration() -> Inventory:
    print_title("Inventory configuration")

    while True:
        ip = input("IP address of your server: ")

        if re.match(r"[0-9]{1,3}(\.[0-9]{1,3}){3}", ip) is None:
            print("Bad formating of IP address, expected XXX.XXX.XXX.XXX")
            continue
        else:
            break

    while True:
        user = input("User name of your server: ")

        if re.match(r"[a-z_][a-z0-9_-]*[$]?", user) is None:
            print("Bad formating of user name, expected [a-z_][a-z0-9_-]*[$]?")
            continue
        else:
            break

    while True:
        key_path = input("Enter your SSH private key path: ")

        if os.path.exists(key_path) is False:
            print("The private key file does not exist")
            continue
        else:
            break

    return Inventory(ip, user, key_path)


@dataclass
class MainRoleTaskMain:
    def path() -> str:
        return "roles/main/tasks/main.yaml"

    def __str__(self) -> str:
        """
        Return the content of the `roles/main/tasks/main.yaml` file
        """
        return """---

- name: Verify ping
  ansible.builtin.shell:
    cmd: ping -c 3 google.com

- name: Verify GPG key
  ansible.builtin.shell:
    cmd: gpg --auto-key-locate clear,wkd -v --locate-external-key pierre@archlinux.org

- name: Update pacman database
  pacman:
    update_cache: true

- name: Update the system clock
  ansible.builtin.shell:
    cmd: timedatectl
"""


@dataclass
class PartitionRoleVars:
    device: str
    layout: str
    efi_size: int  # in MiB
    swap_size: int  # in GiB

    def path() -> str:
        return "roles/partition/vars/main.yaml"

    def __str__(self) -> str:
        """
        Return the content of the `roles/partition/vars/main.yaml` file
        """
        return """device: %s
layout: %s
efi_size: "{{ %d * 1024 }}"
swap_size: "{{ %d * 1024 * 1024 }}"
efi_size_with_unit: "{{ efi_size }}KiB"
swap_size_with_unit: "{{ swap_size }}KiB"
root_size_with_unit: 100%%
part_start_efi_size: 1024KiB
part_end_efi_size: "{{ efi_size_with_unit }}"
part_start_swap_size: "{{ efi_size_with_unit if layout == \'uefi\' else \'1024KiB\' }}"
part_end_swap_size: "{{ (efi_size | int) + (swap_size | int) if layout == \'uefi\' else swap_size }}KiB"
efi_number: "{{ 1 if layout == \'uefi\' else 0 }}"
swap_number: "{{ 2 if layout == \'uefi\' else 1 }}"
root_number: "{{ 3 if layout == \'uefi\' else 2 }}"
part_start_root_size: "{{ part_end_swap_size }}"
part_end_root_size: "{{ root_size_with_unit }}"
""" % (
            self.device,
            self.layout,
            self.efi_size,
            self.swap_size,
        )


@dataclass
class PartitionRoleTaskMain:
    def path() -> str:
        return "roles/partition/tasks/main.yaml"

    def __str__(self) -> str:
        """
        Return the content of the `roles/partition/tasks/main.yaml` file
        """
        return f"""---

- name: Create EFI partition
  community.general.parted:
    device: {'"{{ device }}"'}
    number: {'"{{ efi_number }}"'}
    state: present
    label: gpt
    flags: [esp]
    part_start: {'"{{ part_start_efi_size }}"'}
    part_end: {'"{{ part_end_efi_size }}"'}
  when: layout == "uefi"

- name: Format EFI partition
  community.general.filesystem:
    fstype: vfat
    dev: {'"{{ device }}{{ efi_number }}"'}
  when: layout == "uefi"

- name: Create swap partition
  community.general.parted:
    device: {'"{{ device }}"'}
    number: {'"{{ swap_number }}"'}
    state: present
    label: gpt
    flags: [swap]
    part_start: {'"{{ part_start_swap_size }}"'}
    part_end: {'"{{ part_end_swap_size }}"'}

- name: Format swap partition
  community.general.filesystem:
    fstype: swap
    dev: {'"{{ device }}{{ swap_number }}"'}

- name: Create root partition
  community.general.parted:
    device: {'"{{ device }}"'}
    number: {'"{{ root_number }}"'}
    state: present
    label: gpt
    flags: [boot]
    part_start: {'"{{ part_start_root_size }}"'}
    part_end: {'"{{ part_end_root_size }}"'}

- name: Format root partition
  community.general.filesystem:
    fstype: ext4
    dev: {'"{{ device }}{{ root_number }}"'}

- name: Mount root partition
  ansible.builtin.mount:
    path: /mnt
    src: {'"{{ device }}{{ root_number }}"'}
    state: mounted
    fstype: ext4

- name: Create /mnt/boot directory
  ansible.builtin.file:
    path: /mnt/boot
    state: directory
    mode: 0755
    owner: root
    group: root
    recurse: yes
    selevel: s0
    serole: object_r
    setype: sysfs_t
    seuser: system_u
  when: layout == "uefi"

- name: Mount EFI partition
  ansible.builtin.mount:
    path: /mnt/boot
    src: {'"{{ device }}{{ efi_number }}"'}
    state: mounted
    fstype: vfat
  when: layout == "uefi"

- name: Swapon swap partition
  ansible.builtin.shell:
    cmd: swapon {'"{{ device }}{{ swap_number }}"'}
"""


def partition_role_var_configuration() -> PartitionRoleVars:
    print_title("Partition role configuration")

    while True:
        device = input("Device: ")

        if re.match(r"/dev/[a-z][a-z0-9]*", device) is None:
            print("Bad formating of device name, expected /dev/[a-z][a-z0-9]*")
            continue
        else:
            break

    while True:
        layout = input("Layout (uefi|bios): ")

        if re.match(r"uefi|bios", layout) is None:
            print("Bad formating of layout, expected uefi|bios")
            continue
        else:
            break

    while True:
        if layout == "bios":
            efi_size = 0
            break

        efi_size = input("Size of your EFI partition in MiB: ")

        if re.match(r"[0-9]+", efi_size) is None:
            print("Bad formating of EFI size, expected [0-9]+")
            continue
        else:
            efi_size = int(efi_size)
            break

    while True:
        swap_size = input("Size of your swap partition in GiB: ")

        if re.match(r"[0-9]+", swap_size) is None:
            print("Bad formating of swap size, expected [0-9]+")
            continue
        else:
            swap_size = int(swap_size)
            break

    return PartitionRoleVars(device, layout, efi_size, swap_size)


@dataclass
class InstallationRoleTaskMain:
    def path() -> str:
        return "roles/installation/tasks/main.yaml"

    def __str__(self) -> str:
        """
        Return the content of the `roles/installation/tasks/main.yaml` file
        """
        return """---

- name: Install base, linux, linux-firmware
  ansible.builtin.shell:
    cmd: pacstrap /mnt base linux linux-firmware
"""


@dataclass
class Playbook:
    name: str

    def path() -> str:
        return f"playbook.yaml"

    def __str__(self) -> str:
        """
        Return the content of the `main.yaml` file
        """
        return f"""---

- name: Install ArchLinux - {self.name}
  hosts: archlinux_server
  connection: ssh
  become: true
  roles:
    - main
    - {"{ role: partition, vars_file: roles/partition/vars/main.yaml, tags: partition }"}
    - {"{ role: installation, tags: installation }"}
"""


def main():
    print("Welcome to the ArchLinux generator installation!")

    while True:
        playbook_name = input("Enter the name of your playbook: ")
        PLAYBOOK_DIR = f"{PLAYBOOKS_DIR}/{playbook_name}"

        # Check if the playbook already exists
        if os.path.exists(PLAYBOOK_DIR):
            print("Playbook already exists, please choose another name")
            continue
        else:
            os.mkdir(PLAYBOOK_DIR)
            break

    create_file_with_content(
        f"{PLAYBOOK_DIR}/{Inventory.path()}", str(inventory_configuration())
    )
    create_file_with_content(
        f"{PLAYBOOK_DIR}/{PartitionRoleVars.path()}",
        str(partition_role_var_configuration()),
    )
    create_file_with_content(
        f"{PLAYBOOK_DIR}/{PartitionRoleTaskMain.path()}", str(PartitionRoleTaskMain())
    )
    create_file_with_content(
        f"{PLAYBOOK_DIR}/{Playbook.path()}", str(Playbook(playbook_name))
    )
    create_file_with_content(
        f"{PLAYBOOK_DIR}/{MainRoleTaskMain.path()}", str(MainRoleTaskMain())
    )
    create_file_with_content(
        f"{PLAYBOOK_DIR}/{InstallationRoleTaskMain.path()}",
        str(InstallationRoleTaskMain()),
    )


if __name__ == "__main__":
    main()
