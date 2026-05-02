
import csv
import json
import sys
from datetime import date, datetime
from connect import get_connection

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _json_serial(obj):
    """JSON serialiser for date/datetime objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serialisable")


def _print_contacts(rows):
    """Pretty-print a list of contact tuples/dicts."""
    if not rows:
        print("  (no contacts found)")
        return
    sep = "-" * 80
    print(sep)
    for r in rows:
        # Supports both tuple (from search_contacts function) and plain rows
        cid      = r[0]
        name     = r[1]
        email    = r[2] or "—"
        birthday = r[3].isoformat() if r[3] else "—"
        group    = r[4] or "—"
        phones   = r[5] or "—"
        created  = r[6].strftime("%Y-%m-%d") if r[6] else "—"
        print(f"  [{cid}] {name}")
        print(f"       Email: {email}  |  Birthday: {birthday}  |  Group: {group}")
        print(f"       Phones: {phones}  |  Added: {created}")
    print(sep)


# ─────────────────────────────────────────────────────────────────────────────
# 3.1 Schema initialisation
# ─────────────────────────────────────────────────────────────────────────────

def init_schema():
    """Run schema.sql and procedures.sql to set up the DB."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for fname in ("schema.sql", "procedures.sql"):
                with open(fname, "r") as f:
                    cur.execute(f.read())
        conn.commit()
        print("Schema and procedures applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error applying schema: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# 3.2 Console Search & Filter
# ─────────────────────────────────────────────────────────────────────────────

def filter_by_group():
    """Show contacts belonging to a chosen group."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            groups = cur.fetchall()

        if not groups:
            print("No groups found.")
            return

        print("\nAvailable groups:")
        for gid, gname in groups:
            print(f"  {gid}. {gname}")

        choice = input("Enter group number: ").strip()
        try:
            gid = int(choice)
        except ValueError:
            print("Invalid input.")
            return

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id, c.name, c.email, c.birthday,
                    g.name AS group_name,
                    STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                WHERE c.group_id = %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY c.name
            """, (gid,))
            rows = cur.fetchall()

        print(f"\nContacts in selected group ({len(rows)} found):")
        _print_contacts(rows)

    finally:
        conn.close()


def search_by_email():
    """Partial-match search on the email field."""
    query = input("Enter email fragment to search: ").strip()
    if not query:
        print("Empty query.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id, c.name, c.email, c.birthday,
                    g.name AS group_name,
                    STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                WHERE c.email ILIKE %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY c.name
            """, (f"%{query}%",))
            rows = cur.fetchall()

        print(f"\nResults for email «{query}» ({len(rows)} found):")
        _print_contacts(rows)

    finally:
        conn.close()


def sorted_contact_list():
    """List all contacts sorted by user's choice."""
    print("\nSort by:")
    print("  1. Name")
    print("  2. Birthday")
    print("  3. Date added")
    choice = input("Choose (1-3): ").strip()

    order_map = {"1": "c.name", "2": "c.birthday", "3": "c.created_at"}
    order_col = order_map.get(choice)
    if not order_col:
        print("Invalid choice.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    c.id, c.name, c.email, c.birthday,
                    g.name AS group_name,
                    STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY {order_col} NULLS LAST
            """)
            rows = cur.fetchall()

        print(f"\nAll contacts sorted ({len(rows)} total):")
        _print_contacts(rows)

    finally:
        conn.close()


def paginated_browse():
    """
    Interactive paginated browsing using the get_contacts_page(limit, offset)
    function from Practice 8 (already in the DB).
    """
    page_size = 5
    offset    = 0

    conn = get_connection()
    try:
        while True:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_page(%s, %s)",
                    (page_size, offset)
                )
                rows = cur.fetchall()

            page_num = offset // page_size + 1
            print(f"\n── Page {page_num} ──")
            _print_contacts(rows)

            options = []
            if offset > 0:
                options.append("p=prev")
            if len(rows) == page_size:
                options.append("n=next")
            options.append("q=quit")

            cmd = input(f"[{', '.join(options)}] > ").strip().lower()
            if cmd == "n" and len(rows) == page_size:
                offset += page_size
            elif cmd == "p" and offset > 0:
                offset -= page_size
            elif cmd == "q":
                break
            else:
                print("Invalid command.")
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# 3.3 Import / Export
# ─────────────────────────────────────────────────────────────────────────────

def export_to_json(filepath="contacts_export.json"):
    """Export all contacts (with phones and group) to a JSON file."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id, c.name, c.email,
                    c.birthday, g.name AS group_name,
                    c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.name
            """)
            contacts = cur.fetchall()

            result = []
            for row in contacts:
                cid, name, email, birthday, group_name, created_at = row

                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s",
                    (cid,)
                )
                phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]

                result.append({
                    "name":       name,
                    "email":      email,
                    "birthday":   birthday,
                    "group":      group_name,
                    "phones":     phones,
                    "created_at": created_at,
                })

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=_json_serial, ensure_ascii=False)

        print(f"Exported {len(result)} contacts to '{filepath}'.")

    finally:
        conn.close()


def _get_or_create_group(cur, group_name):
    """Return group_id for group_name, creating it if necessary."""
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def import_from_json(filepath="contacts_export.json"):
    """
    Import contacts from a JSON file.
    On duplicate name: ask the user to skip or overwrite.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return

    conn = get_connection()
    skipped = inserted = updated = 0

    try:
        for entry in data:
            name     = entry.get("name", "").strip()
            email    = entry.get("email")
            birthday = entry.get("birthday")
            group    = entry.get("group")
            phones   = entry.get("phones", [])

            if not name:
                print("  Skipping entry with no name.")
                skipped += 1
                continue

            with conn.cursor() as cur:
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()

                if existing:
                    print(f"\n  Duplicate: '{name}' already exists.")
                    choice = input("  [s]kip / [o]verwrite? ").strip().lower()
                    if choice != "o":
                        skipped += 1
                        continue

                    # Overwrite
                    group_id = _get_or_create_group(cur, group)
                    cur.execute("""
                        UPDATE contacts
                        SET email = %s, birthday = %s, group_id = %s
                        WHERE name = %s
                    """, (email, birthday, group_id, name))
                    contact_id = existing[0]
                    # Replace phones
                    cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
                    for ph in phones:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (contact_id, ph.get("phone"), ph.get("type"))
                        )
                    updated += 1

                else:
                    group_id = _get_or_create_group(cur, group)
                    cur.execute("""
                        INSERT INTO contacts (name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (name, email, birthday, group_id))
                    contact_id = cur.fetchone()[0]
                    for ph in phones:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (contact_id, ph.get("phone"), ph.get("type"))
                        )
                    inserted += 1

            conn.commit()

        print(f"\nJSON import done: {inserted} inserted, {updated} overwritten, {skipped} skipped.")

    except Exception as e:
        conn.rollback()
        print(f"Import error: {e}")
    finally:
        conn.close()


def import_from_csv(filepath="contacts.csv"):
    """
    Extended CSV import (new fields: email, birthday, group, phone_type).
    CSV expected columns: name, email, birthday, group, phone, phone_type
    Contacts sharing the same name produce multiple phone rows.
    """
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return

    conn = get_connection()
    inserted = skipped = 0

    try:
        # Group rows by contact name so we can handle multiple phone lines
        contacts_map = {}
        for row in rows:
            name = row.get("name", "").strip()
            if not name:
                continue
            if name not in contacts_map:
                contacts_map[name] = {
                    "email":    row.get("email", "").strip() or None,
                    "birthday": row.get("birthday", "").strip() or None,
                    "group":    row.get("group", "").strip() or None,
                    "phones":   [],
                }
            phone      = row.get("phone", "").strip()
            phone_type = row.get("phone_type", "mobile").strip()
            if phone:
                contacts_map[name]["phones"].append((phone, phone_type))

        for name, info in contacts_map.items():
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                if cur.fetchone():
                    print(f"  Skipping existing contact: '{name}'")
                    skipped += 1
                    continue

                group_id = _get_or_create_group(cur, info["group"])
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, info["email"], info["birthday"], group_id))
                contact_id = cur.fetchone()[0]

                for phone, ptype in info["phones"]:
                    if ptype not in ("home", "work", "mobile"):
                        ptype = "mobile"
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, phone, ptype)
                    )

            conn.commit()
            inserted += 1

        print(f"CSV import done: {inserted} inserted, {skipped} skipped.")

    except Exception as e:
        conn.rollback()
        print(f"CSV import error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# 3.4 Stored Procedure Wrappers
# ─────────────────────────────────────────────────────────────────────────────

def add_phone_to_contact():
    """Call the add_phone stored procedure."""
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile): ").strip().lower()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print(f"Phone added to '{name}'.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()


def move_contact_to_group():
    """Call the move_to_group stored procedure."""
    name  = input("Contact name: ").strip()
    group = input("Target group: ").strip()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f"'{name}' moved to group '{group}'.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()


def full_search():
    """Call search_contacts DB function — searches name, email, and all phones."""
    query = input("Search query (name / email / phone): ").strip()
    if not query:
        print("Empty query.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()

        print(f"\nSearch results for «{query}» ({len(rows)} found):")
        _print_contacts(rows)

    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║   PhoneBook TSIS 1 — Extended Features   ║
╠══════════════════════════════════════════╣
║  Schema                                  ║
║   0. Initialise / update DB schema       ║
╠══════════════════════════════════════════╣
║  Search & Filter                         ║
║   1. Filter contacts by group            ║
║   2. Search contacts by email            ║
║   3. List all contacts (sorted)          ║
║   4. Browse contacts (paginated)         ║
║   5. Full search (name + email + phone)  ║
╠══════════════════════════════════════════╣
║  Import / Export                         ║
║   6. Export contacts to JSON             ║
║   7. Import contacts from JSON           ║
║   8. Import contacts from CSV            ║
╠══════════════════════════════════════════╣
║  Stored Procedures                       ║
║   9. Add phone number to contact         ║
║  10. Move contact to group               ║
╠══════════════════════════════════════════╣
║   q. Quit                                ║
╚══════════════════════════════════════════╝
"""

ACTIONS = {
    "0":  init_schema,
    "1":  filter_by_group,
    "2":  search_by_email,
    "3":  sorted_contact_list,
    "4":  paginated_browse,
    "5":  full_search,
    "6":  export_to_json,
    "7":  import_from_json,
    "8":  import_from_csv,
    "9":  add_phone_to_contact,
    "10": move_contact_to_group,
}


def main():
    while True:
        print(MENU)
        choice = input("Select option: ").strip().lower()
        if choice == "q":
            print("Goodbye.")
            sys.exit(0)
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except KeyboardInterrupt:
                print("\n(cancelled)")
        else:
            print("Unknown option. Try again.")


if __name__ == "__main__":
    main()