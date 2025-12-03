import json

# Verificar books.json
with open('data/books.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

test_books = [b for b in books if 'TEST' in b['id'] or 'Test' in b.get('title', '')]
print(f"Books.json - Total: {len(books)}")
print(f"Libros TEST: {len(test_books)}")
for b in test_books[-3:]:
    print(f"  {b['id']:15} {b.get('title', 'N/A')[:30]:30} ${b.get('price', 0):,}")

print()

# Verificar inventory_general.json
with open('data/inventory_general.json', 'r', encoding='utf-8') as f:
    inventory = json.load(f)

print(f"\nInventory_general.json - Total grupos: {len(inventory)}")
total_books_in_inventory = sum(len(group['items']) for group in inventory)
print(f"Total copias en inventario: {total_books_in_inventory}")

# Buscar libros TEST en inventario
test_inv = []
for group in inventory:
    for item in group['items']:
        if 'TEST' in item['id'] or 'Test' in item.get('title', ''):
            test_inv.append(item)

print(f"Copias TEST en inventario: {len(test_inv)}")
for b in test_inv[-3:]:
    print(f"  {b['id']:15} {b.get('title', 'N/A')[:30]:30} ${b.get('price', 0):,}")
