import os

DATA_FILE_PATH = os.path.join("data", "sales_data.txt")


def read_sales_data(filename=DATA_FILE_PATH):
    """
    Reads sales data from file handling encoding issues.
    - Tries utf-8, latin-1, cp1252
    - Skips header row
    - Removes empty lines
    Returns: list of raw lines (strings)
    """
    encodings_to_try = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings_to_try:
        try:
            raw_lines = []
            with open(filename, "r", encoding=enc, errors="ignore") as f:
                first = True
                for line in f:
                    line = line.strip()
                    if first:
                       
                        first = False
                        continue
                    if not line:
                        
                        continue
                    raw_lines.append(line)
            print(f"[read_sales_data] Loaded file with encoding: {enc}, lines: {len(raw_lines)}")
            return raw_lines
        except FileNotFoundError:
            print(f"[read_sales_data] File not found: {filename}")
            return []
        except UnicodeDecodeError:
            
            print(f"[read_sales_data] Failed with encoding: {enc}, trying next...")
            continue

    
    print("[read_sales_data] Could not read file with given encodings.")
    return []


def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries.
    Handles:
    - Pipe '|' delimiter
    - Commas in ProductName (remove)
    - Commas in numeric fields (e.g. 1,500 -> 1500)
    - Quantity -> int
    - UnitPrice -> float
    Skips rows with incorrect number of fields.
    Returns: list of dicts with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    """
    transactions = []

    for line in raw_lines:
        parts = line.split("|")
        if len(parts) != 8:
            
            continue

        transaction_id, date, product_id, product_name, qty_str, price_str, customer_id, region = parts

        
        product_name_clean = product_name.replace(",", "")

       
        qty_str = qty_str.replace(",", "")
        price_str = price_str.replace(",", "")

        try:
            quantity = int(qty_str)
            unit_price = float(price_str)
        except ValueError:
            
            continue

        tx = {
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name_clean,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id,
            "Region": region,
        }
        transactions.append(tx)

    print(f"[parse_transactions] Parsed valid transactions: {len(transactions)}")
    return transactions 
def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters.
    Returns: (valid_transactions, invalid_count, filter_summary)
    """
    valid_transactions = []
    invalid_count = 0

    for tx in transactions:
        required_keys = ["TransactionID", "ProductID", "CustomerID", "Region", "Quantity", "UnitPrice"]
        if any(not tx.get(k) for k in required_keys):
            invalid_count += 1
            continue

        if not tx["TransactionID"].startswith("T"):
            invalid_count += 1
            continue
        if not tx["ProductID"].startswith("P"):
            invalid_count += 1
            continue
        if not tx["CustomerID"].startswith("C"):
            invalid_count += 1
            continue

        if tx["Quantity"] <= 0 or tx["UnitPrice"] <= 0:
            invalid_count += 1
            continue

        amount = tx["Quantity"] * tx["UnitPrice"]

        if region is not None and tx["Region"] != region:
            continue
        if min_amount is not None and amount < min_amount:
            continue
        if max_amount is not None and amount > max_amount:
            continue

        valid_transactions.append(tx)

    total_input = len(transactions)
    final_count = len(valid_transactions)

    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": len([t for t in valid_transactions if region is not None]),
        "filtered_by_amount": 0,
        "final_count": final_count,
    }

    return valid_transactions, invalid_count, filter_summary
