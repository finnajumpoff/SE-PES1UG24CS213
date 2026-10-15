"""Collection ledger for a dairy cooperative.

Records each farmer's milk deliveries, totals a day's collection, finds the
top supplier, flags low-fat milk and prints collection slips.
"""
import hashlib
import sqlite3

LOW_FAT_THRESHOLD = 3.5


def create_ledger():
    """Create an in-memory database with an empty milk table."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE milk (id INTEGER PRIMARY KEY, "
        "farmer TEXT, litres REAL, fat REAL, day TEXT)"
    )
    return conn


def record_milk(conn, farmer, litres, fat, day):
    """Store one delivery using a parameterised query."""
    conn.execute(
        "INSERT INTO milk (farmer, litres, fat, day) VALUES (?, ?, ?, ?)",
        (farmer, litres, fat, day),
    )
    conn.commit()


def farmer_token(farmer):
    """Return a stable SHA-256 identifier for a farmer's name."""
    return hashlib.sha256(farmer.encode()).hexdigest()


def daily_total(conn, day):
    """Return the total litres collected on the given day as text."""
    rows = conn.execute(
        "SELECT litres FROM milk WHERE day = ?", (day,)
    ).fetchall()
    return f"Total: {sum(r[0] for r in rows):.1f} litres"


def top_farmer(conn):
    """Return the farmer with the highest total litres, or None if empty."""
    rows = conn.execute(
        "SELECT farmer, SUM(litres) FROM milk GROUP BY farmer"
    ).fetchall()
    if not rows:
        return None
    best = max(rows, key=lambda r: r[1])
    return best[0]


def print_slip(farmer):
    """Print a collection slip for a farmer."""
    print(f"printing slip for {farmer}")


def low_fat(conn):
    """Return farmers whose milk fat is missing or below the threshold."""
    rows = conn.execute("SELECT farmer, fat FROM milk").fetchall()
    return [f for f, fat in rows if fat is None or fat < LOW_FAT_THRESHOLD]


def main():
    """Run a short demonstration of the ledger."""
    conn = create_ledger()
    record_milk(conn, "Gopal", 12.5, 4.1, "Mon")
    record_milk(conn, "Lata", 20.0, 3.2, "Mon")
    print(daily_total(conn, "Mon"), top_farmer(conn), low_fat(conn))
    print_slip("Gopal")
    print(farmer_token("Lata"))
    conn.close()


if __name__ == "__main__":
    main()
