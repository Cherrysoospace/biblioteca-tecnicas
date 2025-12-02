print('Comparación de strings (orden lexicográfico):')
print('  "1" < "123":', '1' < '123')
print('  "123" < "2":', '123' < '2')
print('  "2" < "345":', '2' < '345')
print('  "345" < "4":', '345' < '4')
print('  "4" < "9780060850524":', '4' < '9780060850524')
print()

isbns = ['1', '123', '123456', '2', '345', '4', '9780060850524']
isbns_sorted = sorted(isbns)
print('Orden lexicográfico de ISBNs:')
print('  Original:', isbns)
print('  Ordenado:', isbns_sorted)
