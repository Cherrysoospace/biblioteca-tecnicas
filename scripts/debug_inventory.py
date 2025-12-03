import sys
import os

# Ensure project root is on sys.path so top-level imports like `services` work
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.inventory_service import InventoryService

svc = InventoryService()
all_groups = svc.inventory_general
zero_groups = [inv for inv in all_groups if inv.get_stock() == 0]
print(f"Total groups: {len(all_groups)}")
print(f"Zero-stock groups: {len(zero_groups)}")
for inv in zero_groups:
    try:
        print(inv.get_isbn(), inv.get_stock(), inv.get_book().get_title(), len(inv.get_items()))
    except Exception:
        print("(malformed inventory)")

# Simulate reservation form selection logic
invs = svc.inventory_general
totals = {}
samples = {}
for inv in invs:
    try:
        isbn = inv.get_book().get_ISBNCode()
        totals[isbn] = totals.get(isbn, 0) + int(inv.get_stock())
        if isbn not in samples:
            samples[isbn] = (inv.get_book().get_title(), inv.get_book().get_id())
    except Exception:
        continue

book_values = []
for isbn, total in totals.items():
    if total == 0:
        title = samples.get(isbn, (None, None))[0]
        if title:
            book_values.append(f"{isbn} - {title}")
        else:
            book_values.append(isbn)

if not book_values:
    book_values = ["(No books with stock 0)"]

print('\nBook selector values:')
for v in book_values:
    print('-', v)
