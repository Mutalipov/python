
-- ------------------------------------------------------------
-- 1. add_phone(contact_name, phone, type)
--    Adds a phone number to an existing contact.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home, work, or mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- ------------------------------------------------------------
-- 2. move_to_group(contact_name, group_name)
--    Moves a contact to a group; creates the group if missing.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Ensure contact exists
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Get or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name)
        RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created.', p_group_name;
    END IF;

    -- Update contact
    UPDATE contacts SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- ------------------------------------------------------------
-- 3. search_contacts(query TEXT)
--    Searches name, email, AND all phones in the phones table.
--    Returns a result set of matching contacts.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    name       VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
DECLARE
    v_pattern TEXT := '%' || p_query || '%';
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name       AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ')
                     AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g  ON g.id  = c.group_id
    LEFT JOIN phones p  ON p.contact_id = c.id
    WHERE
        c.name  ILIKE v_pattern
        OR c.email ILIKE v_pattern
        OR p.phone ILIKE v_pattern
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name;
END;
$$;