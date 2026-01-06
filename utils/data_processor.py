def calculate_total_revenue(transactions):
   def calculate_total_revenue(transactions):
    """Return total revenue as sum of quantity * unit price for all transactions."""

    """
    Calculates total revenue from all transactions.
    Revenue per transaction = Quantity * UnitPrice
    Returns: float (total revenue)
    """
    total = 0.0
    for tx in transactions:
        try:
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            total += qty * price
        except (KeyError, TypeError, ValueError):
            
            continue
    return total


def region_wise_sales(transactions):
    """
    Analyzes sales by region.
    Returns dict:
    {
        "North": {
            "total_sales": 450000.0,
            "transaction_count": 15,
            "percentage": 29.13
        },
        ...
    }
    """
    region_stats = {}
    total_revenue = 0.0

  
    for tx in transactions:
        try:
            region = tx["Region"]
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            revenue = qty * price
        except (KeyError, TypeError, ValueError):
            continue

        total_revenue += revenue

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_stats[region]["total_sales"] += revenue
        region_stats[region]["transaction_count"] += 1

    
    for region, stats in region_stats.items():
        if total_revenue > 0:
            perc = (stats["total_sales"] / total_revenue) * 100
        else:
            perc = 0.0
        
        stats["percentage"] = round(perc, 2)

    
    sorted_regions = sorted(
        region_stats.items(),
        key=lambda item: item[1]["total_sales"],
        reverse=True,
    )

    
    sorted_dict = {region: stats for region, stats in sorted_regions}
    return sorted_dict


def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date.
    Returns dictionary sorted by date.
    """
    daily_data = {}

    for tx in transactions:
        try:
            date = tx["Date"]
            customer = tx["CustomerID"]
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            revenue = qty * price
        except (KeyError, TypeError, ValueError):
            continue

        if date not in daily_data:
            daily_data[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "customers": set()
            }

        daily_data[date]["revenue"] += revenue
        daily_data[date]["transaction_count"] += 1
        daily_data[date]["customers"].add(customer)

    sorted_dates = sorted(daily_data.keys())
    result = {}

    for date in sorted_dates:
        info = daily_data[date]
        result[date] = {
            "revenue": info["revenue"],
            "transaction_count": info["transaction_count"],
            "unique_customers": len(info["customers"])
        }

    return result
def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue.
    Returns tuple: (date, revenue, transaction_count)
    """
    
    daily = daily_sales_trend(transactions)

    if not daily:
        return None, 0.0, 0

    
    peak_date, peak_info = max(
        daily.items(),
        key=lambda item: item[1]["revenue"]
    )

    return peak_date, peak_info["revenue"], peak_info["transaction_count"]

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold.
    Returns list of tuples:
    [(ProductName, TotalQuantity, TotalRevenue), ...]
    """
    product_stats = {}

    for tx in transactions:
        try:
            name = tx["ProductName"]
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            revenue = qty * price
        except (KeyError, TypeError, ValueError):
            continue

        if name not in product_stats:
            product_stats[name] = {
                "quantity": 0,
                "revenue": 0.0
            }

        product_stats[name]["quantity"] += qty
        product_stats[name]["revenue"] += revenue

    
    products_list = []
    for name, stats in product_stats.items():
        products_list.append(
            (name, stats["quantity"], stats["revenue"])
        )

    
    products_list.sort(key=lambda x: x[1], reverse=True)

    
    return products_list[:n]
def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales.
    Returns list of tuples:
    [(ProductName, TotalQuantity, TotalRevenue), ...]
    Only includes products with total quantity < threshold.
    """
    product_stats = {}

    for tx in transactions:
        try:
            name = tx["ProductName"]
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            revenue = qty * price
        except (KeyError, TypeError, ValueError):
            continue

        if name not in product_stats:
            product_stats[name] = {
                "quantity": 0,
                "revenue": 0.0
            }

        product_stats[name]["quantity"] += qty
        product_stats[name]["revenue"] += revenue

    
    low_products = []
    for name, stats in product_stats.items():
        if stats["quantity"] < threshold:
            low_products.append(
                (name, stats["quantity"], stats["revenue"])
            )

   
    low_products.sort(key=lambda x: x[1])

    return low_products

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns.
    Returns dict:
    {
        "C001": {
            "total_spent": 95000.0,
            "purchase_count": 3,
            "avg_order_value": 31666.67,
            "products_bought": ["Laptop", "Mouse", "Keyboard"]
        },
        ...
    }
    """
    customer_stats = {}

    for tx in transactions:
        try:
            cid = tx["CustomerID"]
            product = tx["ProductName"]
            qty = int(tx["Quantity"])
            price = float(tx["UnitPrice"])
            amount = qty * price
        except (KeyError, TypeError, ValueError):
            continue

        if cid not in customer_stats:
            customer_stats[cid] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products": set(),
            }

        customer_stats[cid]["total_spent"] += amount
        customer_stats[cid]["purchase_count"] += 1
        customer_stats[cid]["products"].add(product)

    # avg_order_value + products_bought (list) calculate
    for cid, stats in customer_stats.items():
        if stats["purchase_count"] > 0:
            avg = stats["total_spent"] / stats["purchase_count"]
        else:
            avg = 0.0

        stats["avg_order_value"] = round(avg, 2)
        # set → sorted list
        stats["products_bought"] = sorted(stats["products"])
        del stats["products"]

    
    sorted_items = sorted(
        customer_stats.items(),
        key=lambda item: item[1]["total_spent"],
        reverse=True,
    )

    
    sorted_dict = {cid: stats for cid, stats in sorted_items}
    return sorted_dict
