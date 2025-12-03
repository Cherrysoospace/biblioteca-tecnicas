import json

with open('data/inventory_value.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total libros: {data['total_libros']}")
print(f"Precio total: ${data['precio_total']:,}")
print("\nÚltimos 5 libros:")
for b in data['libros'][-5:]:
    print(f"  {b['id']:15} {b['titulo'][:30]:30} ${b['precio']:,}")
