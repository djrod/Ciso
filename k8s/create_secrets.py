import re
import sys
import os
SECRET_KEYS = ('DJANGO_SECRET_KEY', 'POSTGRES_PASSWORD')

if len(sys.argv) != 2:
    print("Usage: create_secrets.py var_file", file=sys.stderr)
    exit(1)

filename = sys.argv[1]
dirname = f"{filename}.secrets"
if not os.path.isdir(dirname):
    os.makedirs(dirname)

with open(filename, "r") as f:
    lines = f.readlines()
    for line in lines:
        q = re.match("export (.+)=(.+)", line)
        (name, val) = q.groups()
        if name in SECRET_KEYS:
            print("creating secret ", name)
            with open(f"myvars.secrets/{name}", "w") as f2:
                print(val, file=f2)

print("to load the secrets in K8s, use a command like: kubectl create secret generic myvars --from-file myvars.secrets")