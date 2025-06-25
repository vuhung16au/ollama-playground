# SQLite Database Structure - testdb.sqlite

## Overview

This document describes the structure of the `testdb.sqlite` database, which appears to be a simple e-commerce or order management system with users, orders, and items.

## Database Schema

### Tables Summary

- **users**: Customer information
- **orders**: Order records with status tracking
- **items**: Individual items within orders

### Table Relationships

```text
users (1) ──── (many) orders (1) ──── (many) items
```

## Table Structures

### 1. users

Stores customer information.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, NOT NULL | Unique user identifier |
| name | VARCHAR | NOT NULL | User's name |

**Sample Data:**

```text
id | name
---|-----
1  | Alice
2  | Bob
3  | John
```

**Record Count:** 3 users

---

### 2. orders

Stores order information with status tracking.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, NOT NULL | Unique order identifier |
| status | VARCHAR | NOT NULL | Current order status |
| user_id | INTEGER | FOREIGN KEY → users(id) | Reference to the user who placed the order |

**Relationships:**

- `user_id` → `users.id` (Many-to-One)

**Sample Data:**

```text
id | status    | user_id
---|-----------|--------
1  | pending   | 1
2  | shipped   | 1
3  | shipped   | 2
4  | delivered | 2
5  | delivered | 3
```

**Order Statuses Found:**

- `pending`
- `shipped`
- `delivered`

**Record Count:** 5 orders

---

### 3. items

Stores individual items within orders.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, NOT NULL | Unique item identifier |
| name | VARCHAR | NOT NULL | Item name/description |
| price | INTEGER | NOT NULL | Item price (appears to be in cents or basic units) |
| order_id | INTEGER | FOREIGN KEY → orders(id) | Reference to the order containing this item |

**Relationships:**

- `order_id` → `orders.id` (Many-to-One)

**Sample Data:**

```text
id | name     | price | order_id
---|----------|-------|----------
1  | Book     | 10    | 1
2  | Flower   | 5     | 2
3  | Pen      | 1     | 2
4  | Notebook | 7     | 3
5  | Book     | 10    | 4
6  | [more]   | [...]  | [...]
7  | [more]   | [...]  | [...]
```

**Record Count:** 7 items

---

## Entity Relationship Diagram

```text
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │   orders    │       │    items    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄─────┤│ id (PK)     │◄─────┤│ id (PK)     │
│ name        │      ││ status      │      ││ name        │
└─────────────┘      ││ user_id(FK) │      ││ price       │
                     │└─────────────┘      ││ order_id(FK)│
                     │                     │└─────────────┘
                     └─────────────────────┘
```

## Business Logic Insights

Based on the data structure and sample records:

1. **User Management**: Simple user storage with ID and name
2. **Order Processing**: Orders have status tracking (pending → shipped → delivered)
3. **Item Management**: Multiple items can belong to a single order
4. **Pricing**: Prices are stored as integers (likely cents or basic currency units)

## Data Statistics

- **Total Users**: 3
- **Total Orders**: 5
- **Total Items**: 7
- **Average Items per Order**: ~1.4 items

## Common Query Patterns

This database structure supports typical e-commerce queries such as:

- Finding all orders for a specific user
- Getting all items in a specific order
- Calculating order totals by summing item prices
- Tracking order status progression
- User purchase history analysis

## Notes

- The database uses simple integer foreign keys for relationships
- Price is stored as INTEGER, suggesting a need for careful handling of decimal values
- No timestamp fields are present, which might be needed for real-world applications
- No constraints on order status values (could benefit from CHECK constraints)
