# Analysis and Solution Strategies for Project Components

This document contains a concise technical analysis and recommended solution strategies for each project component required by the assignment. Each section is split into: Analysis, Solution Strategy, and for algorithmic modules a dedicated "Chosen Algorithm Strategy (and rationale)" subsection.

Notes:
- English only, technical and concise.
- No code provided — design, risks, and step-by-step implementation guidance only.

---

## Data acquisition

### Analysis
- Problem solved: load the initial catalog of books (minimum attributes: ISBN, title, author, weight, value) into domain objects and repository storage.
- Key requirements: support JSON/CSV input, validate fields, map to domain objects, and provide repeatable ingestion.

### Solution Strategy
1. Implement an ingestion pipeline: detect file type → parse → validate → normalize → map to Book objects.
2. Validation rules: required fields present, ISBN format check, numeric weight/value, non-empty title/author.
3. Normalization: trim, unify encoding (UTF-8), normalize accents and case where needed for text search indices; store canonical ISBN for comparisons.
4. Persist as a single atomic operation (write tmp file → move) to prevent partial state.

### Risks / Difficulties
- Irregular CSV rows and mixed types.  
- Encoding problems with international characters.  
- Duplicate ISBNs and inconsistent identifiers.

### Best practices
- Provide clear ingestion logs and error summaries.  
- Make ingestion idempotent.  
- Include a small utility to re-run imports or migrate formats.

---

## Lists (Inventory General and Inventory Ordered)

### Analysis
- Problem solved: maintain an unsorted master list for mutation and a separately maintained sorted list by ISBN for binary search.

### Solution Strategy
1. Keep `inventory_general` as authoritative for create/update/delete operations.
2. Maintain `inventory_sorted` as a deep copy of `inventory_general` that is sorted by ISBN after mutations using insertion sort (or updated incrementally).
3. Expose a `synchronize_inventories()` method that deep-copies, runs insertion sort, and persists both lists atomically.

### Risks / Difficulties
- Synchronization failures leading to divergence.  
- Potential performance issues if many updates happen frequently.

### Best practices
- Support batch synchronization mode for bulk updates.  
- Use atomic file replace when persisting sorted/unsorted files.  
- Provide a verification helper that asserts inventory_sorted is ordered before binary search.

---

## Stacks (Loan history per user)

### Analysis
- Problem solved: per-user loan histories implemented as stacks (LIFO) with persistence.

### Solution Strategy
1. Use a Stack class with push/pop/peek/size and maintain a `user_stacks: Dict[user_id, Stack]` in LoanService.
2. Persist loan histories to `loan_history.json` and reload to rebuild stacks at startup.
3. On loan creation push loan data; on queries return LIFO-ordered lists.

### Risks / Difficulties
- File corruption and concurrent updates.

### Best practices
- Store histories chronologically (oldest first) in JSON and rebuild stacks on load.  
- Use atomic writes and backups for history files.

---

## Queues (Reservation waiting lists)

### Analysis
- Problem solved: manage waiting lists for out-of-stock books using FIFO queues, assign when copies become available.

### Solution Strategy
1. Represent each ISBN's waiting list with a queue (deque). Persist reservations in repository.
2. Validate reservation creation: only allow when total stock == 0 and user does not already hold the book on loan.
3. On loan return, use binary search to find inventory entry, check the queue, assign the first pending reservation and update its status and assigned_date.

### Risks / Difficulties
- Race conditions for concurrent returns/assignments.  
- Inconsistent reservation states if persistence fails.

### Best practices
- Persist immediately after status change and use atomic file operations.  
- Expose queue position queries and cancellation APIs.

---

## Sorting algorithms

### Analysis
- Problem solved: keep inventory_sorted by ISBN (insertion sort) and generate a price/value report (merge sort).

### Solution Strategy
1. Keep insertion sort in algorithms module and call it when inventory_sorted needs updating after single mutations.
2. Implement merge sort for global reports by book value; run it on report generation (can be scheduled or triggered after relevant mutations).

### Risks / Difficulties
- Insertion sort O(n^2) for many items; merge sort recursion depth on very large lists.

### Best practices
- Use insertion sort for small/near-sorted lists (its strengths).  
- Keep merge sort stable and pure (returns new list).  
- Provide fallback to built-in sorts for very large batch operations (documented exception to educational requirement, if acceptable).

### Chosen Algorithm Strategy (and rationale)
- Insertion Sort: chosen to maintain `inventory_sorted` because typical updates are single insertions and the list is usually nearly-sorted; insertion sort is simple, stable and efficient for small or almost-sorted lists.
- Merge Sort: chosen for global price reports because it guarantees O(n log n) worst-case performance and is stable, which preserves deterministic reporting.

---

## Searching algorithms

### Analysis
- Problem solved: flexible title/author search on unsorted inventory (linear search) and efficient ISBN lookup on sorted inventory (binary search). Binary search is critical for reservation assignment.

### Solution Strategy
1. Linear search: normalize text input and the fields (case/accents) and perform partial matches across title and author fields. Return list of matches.
2. Binary search: validate that inventory_sorted is ordered; perform standard (iterative or recursive) binary search on ISBN key returning index or -1.

### Risks / Difficulties
- Text normalization (unicode, accents) and inconsistent ISBN formats.  

### Best practices
- Centralize normalization logic; canonicalize ISBN for all comparisons.  
- Use verification helpers to assert preconditions for binary search.

### Chosen Algorithm Strategy (and rationale)
- Linear search for Title/Author: acceptable O(n) cost for flexible partial matching where sorting is not helpful.  
- Binary search for ISBN: mandatory O(log n) behavior for quick existence checks on returns and reservation assignments.

---

## Shelf module — Brute Force (enumeration of risky combinations)

### Analysis
- Problem solved: enumerate all 4-book combinations whose combined weight exceeds the risk threshold (8 Kg) — exhaustive exploration required by spec.

### Solution Strategy
1. Use combinatorics (itertools.combinations) to produce all 4-element combinations.  
2. For each candidate, sum validated numeric weights and filter those > threshold.  
3. Stream or paginate results for UI consumption; optionally provide count-only mode for large datasets.

### Risks / Difficulties
- Combinatorial explosion (O(n^4) combinations).  

### Best practices
- Pre-check dataset size and provide an early warning if result count will be large.  
- Provide a sample mode for presentation and a full mode for offline runs.

### Chosen Algorithm Strategy (and rationale)
- Brute-force enumeration meets the educational requirement to explore all combinations exhaustively and is correct and transparent for demonstration.

---

## Shelf module — Backtracking (knapsack optimization)

### Analysis
- Problem solved: select books to maximize total monetary value without exceeding shelf weight capacity (8 Kg). This is the 0/1 knapsack problem; backtracking demonstrates exploration and pruning.

### Solution Strategy
1. Extract weights and values from a normalized candidate list; validate and skip corrupt entries.
2. Optionally prefilter top candidates by value-to-weight ratio to make search tractable for large n (document this step clearly).  
3. Implement recursive backtracking with two branches at each index: include (if capacity allows) and exclude; maintain current_weight/current_value and best_solution state.
4. Implement pruning heuristics: if current_weight exceeds capacity, backtrack immediately; if current_value + optimistic_remaining_value ≤ best_value, prune the branch.
5. Map resulting indices back to book objects and return an ordered result with total weight/value.

### Risks / Difficulties
- Exponential time O(2^n), so performance can be poor for large candidate sets.  
- Floating point rounding of weights.  

### Best practices
- Use deterministic candidate ordering and document the MAX candidate limit if applied.  
- Provide verbose/debug mode to print exploration traces for demos and unit tests.

### Chosen Algorithm Strategy (and rationale)
- Backtracking with pruning is chosen because it finds an optimal 0/1 knapsack solution while allowing pedagogical tracing of the search tree and effective pruning to reduce work compared to brute-force.

---

## Recursion — Stack recursion (total value by author)

### Analysis
- Problem solved: compute total monetary value for books by a specific author using classic (stack) recursion where accumulation happens on the return path.

### Solution Strategy
1. Implement a clear recursive function that processes one element and returns contribution + recursive(rest).  
2. Validate book data (missing price treated as zero).  
3. Provide a demo/test harness and limit recursion depth awareness for large collections.

### Risks / Difficulties
- Stack depth equals number of books (O(n) call frames) — Python does not have TCO; risk of RecursionError for extremely large inputs.

### Best practices
- For production-scale inputs prefer iteration or explicit stack if dataset becomes large. Keep recursion for demonstration and small datasets.

---

## Recursion — Queue (tail) recursion (average weight by author)

### Analysis
- Problem solved: compute average weight for an author using tail-style recursion (accumulators) to show the queue/tail recursion pattern.

### Solution Strategy
1. Implement recursion with parameters (index, count, total_weight) where the recursive call is in tail position and returns final result immediately from base case.
2. Provide debug output that prints accumulator state at each call for educational demonstration.

### Risks / Difficulties
- Python lacks tail-call optimization, so tail recursion still uses O(n) stack. Make this explicit in documentation.

### Best practices
- Document the difference between tail recursion conceptually and Python behavior. Provide an iterative equivalent and recommend iterative implementation for production.

---

## CRUD: users / books / loans / reservations

### Analysis
- Problem solved: full lifecycle management (create/read/update/delete) for users, books, loans and reservations with associated business rules (loan decreases stock, reservations allowed only when stock==0, loan history stacks, reservation assignment on return).

### Solution Strategy
1. Implement a repository layer per entity type for persistence (JSON files) with single responsibility.  
2. Implement service layer for business rules and validation and controller layer that returns UI-friendly shapes.  
3. Enforce business rules in services: loans decrement stock and push history; reservations require stock==0 and user not having active loan; on return run binary search + assign reservation if present.

### Risks / Difficulties
- Cross-entity invariants (book deletion while loans/reservations exist) and inconsistent states when persistence fails mid-operation.  

### Best practices
- Validate references before destructive operations and fail with explanatory errors.  
- Perform multi-step operations in transactional style: complete all in-memory updates and then persist; if persistence fails, attempt rollback or fail loudly and provide remediation.

---

## File handling and persistence

### Analysis
- Problem solved: reliable read/write of JSON data files for domain persistence (books.json, inventory_sorted.json, loan_history.json, reservations.json, etc.).

### Solution Strategy
1. Centralize file IO in repository classes.  
2. Use atomic write pattern: write to a `.tmp` file then rename to target to avoid partial writes.  
3. Keep simple schema versions and a lightweight migration helper when formats change.  
4. Provide backups on destructive migrations.

### Risks / Difficulties
- Corrupt files, concurrent writes, cross-platform path/encoding issues.

### Best practices
- Always write with explicit UTF-8 and ensure ensure_ascii=False if preserving unicode.  
- Use try/except with logged backups and fail-safe recovery.  
- Keep repository APIs idempotent where possible.

---

## Modularity and project structure

### Analysis
- Problem solved: maintain a modular project (models, repositories, services, controllers, ui, utils) to keep responsibilities separated and testable.

### Solution Strategy
1. Follow SRP: Repositories only handle IO; Services implement business logic and validation; Controllers adapt service responses for UI; Utils contain algorithms and helpers.
2. Keep algorithms in utils/algorithms and recursion examples in utils/recursion for clarity.  
3. Use explicit imports and small public APIs per module; document expected contracts (input shapes and error modes).

### Risks / Difficulties
- Circular imports between layers — guard by importing within functions where needed or by using dependency injection patterns.

### Best practices
- Document module contracts (inputs/outputs and error modes).  
- Keep side-effect-free functions in algorithms modules.  
- Add unit tests per module and keep CI checks for linting and basic tests.

---

## Final notes — verification checklist

- Ensure insertion-sort precondition is enforced before calling binary search.  
- Persist changes atomically and provide backups for data files.  
- Expose debug/demo modes for backtracking and recursion modules for presentations.  
- Document any prefiltering or candidate-limiting decisions used to make NP-hard searches practical and deterministic.

This completes the required per-component analysis and recommended implementation strategies. If you want, I can now (a) produce a one-page summary for academic submission, (b) generate a checklist-based README for verifying each module at runtime, or (c) convert this document into a format required by your instructor.
