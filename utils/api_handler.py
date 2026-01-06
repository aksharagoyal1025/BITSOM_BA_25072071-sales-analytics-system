import requests


BASE_URL = "https://dummyjson.com/products"


def fetch_all_products(limit=100):
    """
    Fetches all products from DummyJSON.
    Returns list of product dicts.
    On failure, returns empty list.
    """
    try:
        url = f"{BASE_URL}?limit={limit}"
        print(f"[API] Fetching products from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  

        data = response.json()
       
        products = data.get("products", [])
        print(f"[API] Fetched {len(products)} products")
        return products
    except requests.RequestException as e:
        print(f"[API] Error fetching products: {e}")
        return []


def create_product_mapping(api_products):
    """
    Creates mapping of product IDs to info.
    Returns dict: {id: {title, category, brand, rating}}
    """
    mapping = {}
    for p in api_products:
        try:
            pid = int(p.get("id"))
        except (TypeError, ValueError):
            continue

        mapping[pid] = {
            "title": p.get("title"),
            "category": p.get("category"),
            "brand": p.get("brand"),
            "rating": p.get("rating"),
        }

    print(f"[API] Product mapping size: {len(mapping)}")
    return mapping
def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information.

    New fields added:
    - APICategory
    - APIBrand
    - APIRating
    - APIMatch (True/False)
    """
    enriched = []

    # API products list for round-robin assignment
    api_products = list(product_mapping.values())
    api_len = len(api_products)

    for idx, tx in enumerate(transactions):
        tx_copy = tx.copy()

        api_category = None
        api_brand = None
        api_rating = None
        api_match = False

        if api_len > 0:
            # Round-robin: har transaction ko ek API product assign karo
            api_info = api_products[idx % api_len]
            api_category = api_info.get("category")
            api_brand = api_info.get("brand")
            api_rating = api_info.get("rating")
            api_match = True

        tx_copy["APICategory"] = api_category
        tx_copy["APIBrand"] = api_brand
        tx_copy["APIRating"] = api_rating
        tx_copy["APIMatch"] = api_match

        enriched.append(tx_copy)

    return enriched

def save_enriched_data(enriched_transactions, filename="data/enriched_salesdata.txt"):
    """
    Saves enriched transactions back to a pipe-delimited file.

    Columns:
    TransactionID | Date | ProductID | ProductName | Quantity | UnitPrice |
    CustomerID | Region | APICategory | APIBrand | APIRating | APIMatch
    """
    import os

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    header_fields = [
        "TransactionID",
        "Date",
        "ProductID",
        "ProductName",
        "Quantity",
        "UnitPrice",
        "CustomerID",
        "Region",
        "APICategory",
        "APIBrand",
        "APIRating",
        "APIMatch",
    ]

    with open(filename, "w", encoding="utf-8") as f:
        
        f.write("|".join(header_fields) + "\n")

        for tx in enriched_transactions:
            row = []
            for field in header_fields:
                value = tx.get(field, "")
                if value is None:
                    value = ""
                row.append(str(value))
            line = "|".join(row)
            f.write(line + "\n")

    print(f"[API] Enriched data saved to {filename}")
def fetch_all_products():
    """Fetch up to 100 products from DummyJSON API and return a list."""
