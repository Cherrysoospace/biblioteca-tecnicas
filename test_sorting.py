from services.inventory_service import InventoryService

inv = InventoryService()

print('Primeros 15 ISBNs ordenados numéricamente:')
print('-' * 50)
for i in range(min(15, len(inv.inventory_sorted))):
    isbn = inv.inventory_sorted[i].get_isbn()
    stock = inv.inventory_sorted[i].get_stock()
    print(f'  {i+1:2}. ISBN: {isbn:20} (Stock: {stock})')

print()
print(f'Total de grupos de inventario: {len(inv.inventory_sorted)}')
