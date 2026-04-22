"""
Setup script to parse TSQL2012.sql and create SQLite database.
Parses actual INSERT statements from the UTF-16 SQL file and creates database.
"""
import sqlite3
import re
from pathlib import Path
import os

# Database file location
DB_FILE = os.path.join("/tmp", "TSQL2012.db")
SQL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TSQL2012.sql")




def create_sqlite_schema(conn):
    """Create SQLite schema with only the required tables."""
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS OrderDetails;")
    cursor.execute("DROP TABLE IF EXISTS Orders;")
    cursor.execute("DROP TABLE IF EXISTS Customers;")
    cursor.execute("DROP TABLE IF EXISTS Employees;")

    # Create Employees table (PascalCase)
    cursor.execute("""
        CREATE TABLE Employees (
            empid INTEGER PRIMARY KEY,
            lastname TEXT NOT NULL,
            firstname TEXT NOT NULL,
            title TEXT NOT NULL,
            titleofcourtesy TEXT NOT NULL,
            birthdate TEXT NOT NULL,
            hiredate TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            region TEXT,
            postalcode TEXT,
            country TEXT NOT NULL,
            phone TEXT NOT NULL,
            mgrid INTEGER,
            FOREIGN KEY (mgrid) REFERENCES Employees(empid)
        )
    """)

    # Create Customers table (PascalCase)
    cursor.execute("""
        CREATE TABLE Customers (
            custid INTEGER PRIMARY KEY,
            companyname TEXT NOT NULL,
            contactname TEXT NOT NULL,
            contacttitle TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            region TEXT,
            postalcode TEXT,
            country TEXT NOT NULL,
            phone TEXT NOT NULL,
            fax TEXT
        )
    """)

    # Create Orders table (PascalCase)
    cursor.execute("""
        CREATE TABLE Orders (
            orderid INTEGER PRIMARY KEY,
            custid INTEGER,
            empid INTEGER NOT NULL,
            orderdate TEXT NOT NULL,
            requireddate TEXT NOT NULL,
            shippeddate TEXT,
            shipperid INTEGER NOT NULL,
            freight REAL NOT NULL DEFAULT 0,
            shipname TEXT NOT NULL,
            shipaddress TEXT NOT NULL,
            shipcity TEXT NOT NULL,
            shipregion TEXT,
            shippostalcode TEXT,
            shipcountry TEXT NOT NULL,
            FOREIGN KEY (custid) REFERENCES Customers(custid),
            FOREIGN KEY (empid) REFERENCES Employees(empid)
        )
    """)

    # Create OrderDetails table (PascalCase)
    cursor.execute("""
        CREATE TABLE OrderDetails (
            orderid INTEGER NOT NULL,
            productid INTEGER NOT NULL,
            unitprice REAL NOT NULL DEFAULT 0,
            qty INTEGER NOT NULL DEFAULT 1,
            discount REAL NOT NULL DEFAULT 0,
            PRIMARY KEY (orderid, productid),
            FOREIGN KEY (orderid) REFERENCES Orders(orderid)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_employees_lastname ON Employees(lastname);")
    cursor.execute("CREATE INDEX idx_employees_postalcode ON Employees(postalcode);")
    cursor.execute("CREATE INDEX idx_customers_city ON Customers(city);")
    cursor.execute("CREATE INDEX idx_customers_companyname ON Customers(companyname);")
    cursor.execute("CREATE INDEX idx_customers_postalcode ON Customers(postalcode);")
    cursor.execute("CREATE INDEX idx_customers_region ON Customers(region);")
    cursor.execute("CREATE INDEX idx_orderdetails_orderid ON OrderDetails(orderid);")
    cursor.execute("CREATE INDEX idx_orderdetails_productid ON OrderDetails(productid);")

    conn.commit()
    print("✓ SQLite schema created successfully")


def parse_sql_value(value):
    """Parse a SQL value, handling N'strings', NULL, dates, etc."""
    value = value.strip()

    # Handle NULL
    if value.upper() == 'NULL':
        return None

    # Handle N'string' literals (Unicode strings)
    if value.startswith("N'") and value.endswith("'"):
        return value[2:-1]  # Remove N' and '

    # Handle regular strings
    if value.startswith("'") and value.endswith("'"):
        content = value[1:-1]  # Remove quotes

        # Handle escaped quotes like ''
        content = content.replace("''", "'")

        return content

    # Handle dates like '20060704 00:00:00.000' -> '2006-07-04'
    date_match = re.match(r"'(\d{4})(\d{2})(\d{2})\s+\d{2}:\d{2}:\d{2}\.\d{3}'", value)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month}-{day}"

    # Handle numbers (integers and floats)
    try:
        # Try integer first
        if '.' not in value:
            return int(value)
        else:
            return float(value)
    except ValueError:
        pass

    # If nothing else matches, return as string
    return value


def parse_values_clause(values_str):
    """Parse a VALUES clause into a list of values."""
    # Remove VALUES( and )
    values_str = values_str.strip()
    if values_str.startswith('VALUES(') and values_str.endswith(');'):
        values_str = values_str[7:-2]  # Remove VALUES( and );
    elif values_str.startswith('VALUES(') and values_str.endswith(')'):
        values_str = values_str[7:-1]  # Remove VALUES( and )

    values = []
    current_value = ""
    in_string = False
    string_char = None
    paren_depth = 0

    i = 0
    while i < len(values_str):
        char = values_str[i]

        if not in_string:
            if char in ("'", '"'):
                in_string = True
                string_char = char
                current_value += char
            elif char == '(':
                paren_depth += 1
                current_value += char
            elif char == ')':
                paren_depth -= 1
                current_value += char
            elif char == ',' and paren_depth == 0:
                # End of value
                values.append(parse_sql_value(current_value))
                current_value = ""
            else:
                current_value += char
        else:
            # Inside string
            current_value += char
            if char == string_char:
                # Check if this is an escaped quote
                if i + 1 < len(values_str) and values_str[i + 1] == string_char:
                    # Escaped quote, skip the next character
                    current_value += string_char
                    i += 1
                else:
                    # End of string
                    in_string = False

        i += 1

    # Add the last value
    if current_value:
        values.append(parse_sql_value(current_value))

    return values


def parse_sql_file():
    """Parse the TSQL2012.sql file and extract INSERT statements."""
    print("📖 Reading TSQL2012.sql file...")

    # Read the UTF-16 file
    with open(SQL_FILE, 'rb') as f:
        content = f.read()

    # Decode from UTF-16
    sql_content = content.decode('utf-16')

    # Dictionary to store parsed data
    data = {
        'Employees': [],
        'Customers': [],
        'Orders': [],
        'OrderDetails': []
    }

    # Split content into lines for easier processing
    lines = sql_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Look for INSERT INTO statements
        if line.startswith('INSERT INTO HR.Employees'):
            # Collect all lines until we find the semicolon
            insert_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(';'):
                insert_lines.append(lines[i])
                i += 1
            if i < len(lines):
                insert_lines.append(lines[i])  # Add the line with semicolon
                i += 1

            # Join all lines and extract VALUES
            full_insert = ' '.join(insert_lines)
            values_match = re.search(r'VALUES\s*\((.*?)\);', full_insert, re.DOTALL)
            if values_match:
                try:
                    values = parse_values_clause(f"VALUES({values_match.group(1)});")
                    data['Employees'].append(values)
                except Exception as e:
                    print(f"❌ Error parsing Employees VALUES: {values_match.group(1)[:100]}... Error: {e}")

        elif line.startswith('INSERT INTO Sales.Customers'):
            # Collect all lines until we find the semicolon
            insert_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(';'):
                insert_lines.append(lines[i])
                i += 1
            if i < len(lines):
                insert_lines.append(lines[i])  # Add the line with semicolon
                i += 1

            # Join all lines and extract VALUES
            full_insert = ' '.join(insert_lines)
            values_match = re.search(r'VALUES\s*\((.*?)\);', full_insert, re.DOTALL)
            if values_match:
                try:
                    values = parse_values_clause(f"VALUES({values_match.group(1)});")
                    data['Customers'].append(values)
                except Exception as e:
                    print(f"❌ Error parsing Customers VALUES: {values_match.group(1)[:100]}... Error: {e}")

        elif line.startswith('INSERT INTO Sales.Orders'):
            # Collect all lines until we find the semicolon
            insert_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(';'):
                insert_lines.append(lines[i])
                i += 1
            if i < len(lines):
                insert_lines.append(lines[i])  # Add the line with semicolon
                i += 1

            # Join all lines and extract VALUES
            full_insert = ' '.join(insert_lines)
            values_match = re.search(r'VALUES\s*\((.*?)\);', full_insert, re.DOTALL)
            if values_match:
                try:
                    values = parse_values_clause(f"VALUES({values_match.group(1)});")
                    data['Orders'].append(values)
                except Exception as e:
                    print(f"❌ Error parsing Orders VALUES: {values_match.group(1)[:100]}... Error: {e}")

        elif line.startswith('INSERT INTO Sales.OrderDetails'):
            # Collect all lines until we find the semicolon
            insert_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(';'):
                insert_lines.append(lines[i])
                i += 1
            if i < len(lines):
                insert_lines.append(lines[i])  # Add the line with semicolon
                i += 1

            # Join all lines and extract VALUES
            full_insert = ' '.join(insert_lines)
            values_match = re.search(r'VALUES\s*\((.*?)\);', full_insert, re.DOTALL)
            if values_match:
                try:
                    values = parse_values_clause(f"VALUES({values_match.group(1)});")
                    data['OrderDetails'].append(values)
                except Exception as e:
                    print(f"❌ Error parsing OrderDetails VALUES: {values_match.group(1)[:100]}... Error: {e}")

        else:
            i += 1

    print(f"✅ Parsed data: {len(data['Employees'])} Employees, {len(data['Customers'])} Customers, {len(data['Orders'])} Orders, {len(data['OrderDetails'])} OrderDetails")
    return data


def populate_database(conn, data):
    """Populate the database with parsed data."""
    cursor = conn.cursor()

    # Insert Employees
    print("👥 Inserting Employees...")
    for emp in data['Employees']:
        try:
            cursor.execute("""
                INSERT INTO Employees (empid, lastname, firstname, title, titleofcourtesy,
                                     birthdate, hiredate, address, city, region, postalcode,
                                     country, phone, mgrid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, emp)
        except Exception as e:
            print(f"❌ Error inserting employee: {emp}. Error: {e}")

    # Insert Customers
    print("🏢 Inserting Customers...")
    for cust in data['Customers']:
        try:
            cursor.execute("""
                INSERT INTO Customers (custid, companyname, contactname, contacttitle,
                                     address, city, region, postalcode, country, phone, fax)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, cust)
        except Exception as e:
            print(f"❌ Error inserting customer: {cust}. Error: {e}")

    # Insert Orders
    print("📦 Inserting Orders...")
    for order in data['Orders']:
        try:
            cursor.execute("""
                INSERT INTO Orders (orderid, custid, empid, orderdate, requireddate,
                                  shippeddate, shipperid, freight, shipname, shipaddress,
                                  shipcity, shipregion, shippostalcode, shipcountry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, order)
        except Exception as e:
            print(f"❌ Error inserting order: {order}. Error: {e}")

    # Insert OrderDetails
    print("📋 Inserting OrderDetails...")
    for detail in data['OrderDetails']:
        try:
            cursor.execute("""
                INSERT INTO OrderDetails (orderid, productid, unitprice, qty, discount)
                VALUES (?, ?, ?, ?, ?)
            """, detail)
        except Exception as e:
            print(f"❌ Error inserting order detail: {detail}. Error: {e}")

    conn.commit()


def setup_database():
    """Main function to create and populate the database."""
    # Remove existing database if it exists
    db_path = Path(DB_FILE)
    if db_path.exists():
        db_path.unlink()
        print(f"✓ Removed existing {DB_FILE}")

    # Check if SQL file exists
    sql_path = Path(SQL_FILE)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file {SQL_FILE} not found")

    # Create new database
    conn = sqlite3.connect(DB_FILE)

    try:
        create_sqlite_schema(conn)
        data = parse_sql_file()
        populate_database(conn, data)

        # Verify counts
        cursor = conn.cursor()
        emp_count = cursor.execute("SELECT COUNT(*) FROM Employees").fetchone()[0]
        cust_count = cursor.execute("SELECT COUNT(*) FROM Customers").fetchone()[0]
        order_count = cursor.execute("SELECT COUNT(*) FROM Orders").fetchone()[0]
        detail_count = cursor.execute("SELECT COUNT(*) FROM OrderDetails").fetchone()[0]

        print("\n✅ Database populated successfully!")
        print(f"✓ Employees: {emp_count} (expected: 9)")
        print(f"✓ Customers: {cust_count} (expected: 91)")
        print(f"✓ Orders: {order_count} (expected: 830)")
        print(f"✓ OrderDetails: {detail_count} (expected: 2155)")

        # Check if counts match expectations
        if emp_count == 9 and cust_count == 91 and order_count == 830 and detail_count == 2155:
            print("🎉 All counts match expected values!")
        else:
            print("⚠️ Some counts don't match expected values")

    finally:
        conn.close()


if __name__ == "__main__":
    setup_database()
