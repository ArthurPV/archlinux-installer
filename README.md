# ArchLinux Install

> [!WARNING]  
> This playbook is not intended to be used on a local machine, it will erase all your data. Use it only on a remote host that you can access with SSH and that you don't care about.

Here is the steps to install ArchLinux on a remote host with a custom generated Ansible playbook:

## 1. Clone repo

```bash
git clone repo
cd repo
```

## 2. Install ansible

on ArchLinux:

```bash
sudo pacman -S ansible sshpass
```

## 3. Install ansible-galaxy roles

```bash
ansible-galaxy collection install community.general
```

## 4. Generate a SSH key for your host

```bash
ssh-keygen -f ./key -t ecdsa -b 521
```

## 5. Add your SSH key to your host

```bash
ssh-copy-id -i ./key.pub <user>@<host>
```

## 6. Generate a custom playbook & run it

```bash
./generate_playbook.py
ansible-playbook -i ./playbooks/<playbook_name>/inventory.ini ./playbooks/<playbook_name>/playbook.yaml
```

You can also run the example playbook:

```bash
ansible-playbook -i ./playbooks/example/inventory.ini ./playbooks/example/playbook.yaml
```