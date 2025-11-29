#!/usr/bin/env python3
"""Migration script: normalize loan IDs to pattern L{n:03d}.

- Creates a backup of data/loan.json as loan.json.bak.{timestamp}
- Converts any loan entries whose loan_id does not match '^L\d+(?:-\d+)?$' to sequential IDs
  using the next available numeric suffix (zero-padded to 3 digits), avoiding collisions.
- Prints a summary mapping old_id -> new_id for changed entries.
"""
import json
import os
from datetime import datetime
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'loan.json')

if not os.path.exists(DATA_PATH):
    print(f"No existe el archivo de préstamos en: {DATA_PATH}")
    raise SystemExit(1)

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
    except Exception as e:
        print(f"Error leyendo {DATA_PATH}: {e}")
        raise

if not isinstance(data, list):
    print(f"Formato inesperado en {DATA_PATH}: se esperaba una lista de préstamos")
    raise SystemExit(1)

# Backup
bak_path = DATA_PATH + '.bak.' + datetime.utcnow().strftime('%Y%m%d%H%M%S')
with open(bak_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Backup creado: {bak_path}")

# Collect existing L### numeric parts
pattern = re.compile(r'^L(\d+)(?:-\d+)?$')
existing_ids = set()
numeric_values = []
for item in data:
    lid = item.get('loan_id')
    if isinstance(lid, str) and pattern.match(lid):
        existing_ids.add(lid)
        m = pattern.match(lid)
        try:
            numeric_values.append(int(m.group(1)))
        except Exception:
            pass

max_n = max(numeric_values) if numeric_values else 0
next_n = max_n + 1

mapping = {}
all_ids = set(existing_ids)

for idx, item in enumerate(data):
    old = item.get('loan_id')
    if not isinstance(old, str) or not pattern.match(old):
        # assign new id
        new_id = f"L{next_n:03d}"
        # avoid collision
        counter = 1
        while new_id in all_ids:
            new_id = f"L{next_n:03d}-{counter}"
            counter += 1
        item['loan_id'] = new_id
        mapping[old] = new_id
        all_ids.add(new_id)
        next_n += 1

# If nothing changed, notify and exit
if not mapping:
    print("No se encontraron IDs para migrar. Nada que hacer.")
    raise SystemExit(0)

# Write back
with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Migración completada. {len(mapping)} IDs actualizados:")
for old, new in mapping.items():
    print(f"  {old} -> {new}")
print("Archivo actualizado:", DATA_PATH)
print("Si algo sale mal, restaura desde el backup creado arriba.")
