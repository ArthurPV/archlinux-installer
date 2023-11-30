# ArchLinux Install

```bash
git clone repo
cd repo
./generate_playbook.py
ansible-playbook -i ./playbooks/<playbook_name>/inventory.ini ./playbooks/<playbook_name>/playbook.yaml
```