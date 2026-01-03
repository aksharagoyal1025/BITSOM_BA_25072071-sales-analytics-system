from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    daily_sales_trend,
    top_selling_products,
    customer_analysis,
    find_peak_sales_day,
    low_performing_products,
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data,
)
from utils.report_generator import generate_sales_report


def main():
    print("===================================")
    print("        SALES ANALYTICS SYSTEM     ")
    print("===================================\n")

    
    print("[1/10] Reading sales data...")
    raw_lines = read_sales_data()
    print(f"✓ Successfully read {len(raw_lines)} raw lines\n")

   
    print("[2/10] Parsing and cleaning data...")
    transactions = parse_transactions(raw_lines)
    print(f"✓ Parsed {len(transactions)} records\n")

    
    print("[3/10] Filter Options Available:")
    regions = sorted({tx["Region"] for tx in transactions if "Region" in tx})
    print(f"  Regions: {', '.join(regions)}")

    amounts = [int(tx["Quantity"]) * float(tx["UnitPrice"]) for tx in transactions]
    min_amt = min(amounts) if amounts else 0
    max_amt = max(amounts) if amounts else 0
    print(f"  Amount Range: {min_amt} to {max_amt}")

    choice = input("\nDo you want to filter data? (y/n): ").strip().lower()
    filter_region = None
    min_amount = None
    max_amount = None

    if choice == "y":
        region_in = input("Enter region to filter (or press Enter to skip): ").strip()
        filter_region = region_in or None

        min_in = input("Enter minimum amount (or press Enter to skip): ").strip()
        max_in = input("Enter maximum amount (or press Enter to skip): ").strip()

        if min_in:
            try:
                min_amount = float(min_in)
            except ValueError:
                min_amount = None
        if max_in:
            try:
                max_amount = float(max_in)
            except ValueError:
                max_amount = None

    
    print("\n[4/10] Validating transactions...")
    valid_tx, invalid_count, summary = validate_and_filter(
        transactions,
        region=filter_region,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    print(
        f"✓ Valid: {summary['final_count']} | "
        f"Invalid: {summary['invalid']}"
    )
    print(f"  Filtered by region: {summary['filtered_by_region']}")
    print(f"  Filtered by amount: {summary['filtered_by_amount']}\n")

    
    print("[5/10] Analyzing sales data...")
    total_revenue = calculate_total_revenue(valid_tx)
    region_stats = region_wise_sales(valid_tx)
    trend = daily_sales_trend(valid_tx)
    peak_date, peak_revenue, peak_count = find_peak_sales_day(valid_tx)
    top_products = top_selling_products(valid_tx, n=5)
    cust_stats = customer_analysis(valid_tx)
    low_products = low_performing_products(valid_tx, threshold=10)
    print("✓ Analysis complete\n")

   
    print("[Sales Summary] Peak sales day:")
    print(f"Date={peak_date}, revenue={peak_revenue}, transactions={peak_count}\n")

    print("[Sales Summary] Top selling products:")
    for name, qty, revenue in top_products:
        print(f"{name}: quantity={qty}, revenue={revenue}")
    print()

    print("[Sales Summary] Top customers:")
    count = 0
    for cid, stats in cust_stats.items():
        print(
            f"{cid}: total_spent={stats['total_spent']}, "
            f"orders={stats['purchase_count']}, "
            f"avg_order_value={stats['avg_order_value']}, "
            f"products={stats['products_bought']}"
        )
        count += 1
        if count >= 5:
            break
    print()

    print("[Sales Summary] Low performing products (qty < 10):")
    for name, qty, revenue in low_products[:5]:
        print(f"{name}: quantity={qty}, revenue={revenue}")
    print()

    
    print("[6/10] Fetching product data from API...")
    api_products = fetch_all_products(limit=100)
    product_mapping = create_product_mapping(api_products)
    print(f"✓ Fetched {len(api_products)} products\n")

    
    print("[7/10] Enriching sales data...")
    enriched_tx = enrich_sales_data(valid_tx, product_mapping)
    matched = sum(1 for tx in enriched_tx if tx.get("APIMatch"))
    success_rate = (matched / len(enriched_tx) * 100) if enriched_tx else 0.0
    print(
        f"✓ Enriched {matched}/{len(enriched_tx)} transactions "
        f"({success_rate:.1f}%)\n"
    )

    
    print("[8/10] Saving enriched data...")
    save_enriched_data(enriched_tx, filename="data/enriched_salesdata.txt")
    print("✓ Saved to: data/enriched_salesdata.txt\n")

    
    print("[9/10] Generating report...")
    generate_sales_report(valid_tx, enriched_tx, output_file="output/sales_report.txt")
    print("✓ Report saved to: output/sales_report.txt\n")

    print("[10/10] Process Complete!")
    print("All steps finished successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n[ERROR] Something went wrong during processing.")
        print(f"Details: {e}")
