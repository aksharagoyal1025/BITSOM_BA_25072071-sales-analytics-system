import os
from datetime import datetime

from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
)


def format_currency(amount):
    """Simple comma formatting with 2 decimals, e.g. 1545000.5 -> 1,545,000.50"""
    return f"{amount:,.2f}"


def generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt"):
    """
    Generates a comprehensive formatted text report as per assignment Part 4.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    total_tx = len(transactions)
    total_revenue = calculate_total_revenue(transactions)
    avg_order_value = total_revenue / total_tx if total_tx > 0 else 0.0

    # Date range
    dates = sorted({tx["Date"] for tx in transactions})
    date_min = dates[0] if dates else "N/A"
    date_max = dates[-1] if dates else "N/A"

    # Region-wise
    region_stats = region_wise_sales(transactions)

    # Top products & customers
    top_products = top_selling_products(transactions, n=5)
    cust_stats = customer_analysis(transactions)
    top_customers = list(cust_stats.items())[:5]

    # Daily trend & peak day
    trend = daily_sales_trend(transactions)
    peak_date, peak_revenue, peak_count = find_peak_sales_day(transactions)

    # Low performing
    low_products = low_performing_products(transactions, threshold=10)

    # API enrichment summary
    total_enriched = len(enriched_transactions)
    matched = sum(1 for tx in enriched_transactions if tx.get("APIMatch"))
    success_rate = (matched / total_enriched * 100) if total_enriched > 0 else 0.0
    not_enriched_products = sorted(
        {
            tx.get("ProductID")
            for tx in enriched_transactions
            if not tx.get("APIMatch")
        }
    )

    with open(output_file, "w", encoding="utf-8") as f:
        # 1. HEADER
        f.write("SALES ANALYTICS REPORT\n")
        f.write("======================\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Records Processed: {total_tx}\n\n")

        # 2. OVERALL SUMMARY
        f.write("OVERALL SUMMARY\n")
        f.write("===============\n")
        f.write(f"Total Revenue: {format_currency(total_revenue)}\n")
        f.write(f"Total Transactions: {total_tx}\n")
        f.write(f"Average Order Value: {format_currency(avg_order_value)}\n")
        f.write(f"Date Range: {date_min} to {date_max}\n\n")

        # 3. REGION-WISE PERFORMANCE
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("=======================\n")
        f.write("Region        Sales          % of Total   Transactions\n")
        f.write("------------------------------------------------------\n")
        for region, stats in region_stats.items():
            f.write(
                f"{region:<12} {format_currency(stats['total_sales']):>12} "
                f"{stats['percentage']:>10.2f}% {stats['transaction_count']:>12}\n"
            )
        f.write("\n")

        # 4. TOP 5 PRODUCTS
        f.write("TOP 5 PRODUCTS\n")
        f.write("==============\n")
        f.write("Rank  Product Name                 Quantity   Revenue\n")
        f.write("----------------------------------------------------\n")
        for idx, (name, qty, rev) in enumerate(top_products, start=1):
            f.write(
                f"{idx:<4} {name:<28} {qty:>8}   {format_currency(rev):>10}\n"
            )
        f.write("\n")

        # 5. TOP 5 CUSTOMERS
        f.write("TOP 5 CUSTOMERS\n")
        f.write("===============\n")
        f.write("Rank  CustomerID  Total Spent   Orders\n")
        f.write("--------------------------------------\n")
        for idx, (cid, stats) in enumerate(top_customers, start=1):
            f.write(
                f"{idx:<4} {cid:<10} {format_currency(stats['total_spent']):>12}   "
                f"{stats['purchase_count']:>4}\n"
            )
        f.write("\n")

        # 6. DAILY SALES TREND
        f.write("DAILY SALES TREND\n")
        f.write("=================\n")
        f.write("Date         Revenue        Transactions  Unique Customers\n")
        f.write("---------------------------------------------------------\n")
        for date in sorted(trend.keys()):
            info = trend[date]
            f.write(
                f"{date:<12} {format_currency(info['revenue']):>12} "
                f"{info['transaction_count']:>12} {info['unique_customers']:>17}\n"
            )
        f.write("\n")

        # 7. PRODUCT PERFORMANCE ANALYSIS
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("===========================\n")
        f.write(f"Best selling day: {peak_date} (Revenue: {format_currency(peak_revenue)}, "
                f"Transactions: {peak_count})\n")
        f.write("Low performing products (qty < 10):\n")
        if low_products:
            for name, qty, rev in low_products:
                f.write(
                    f"  - {name}: quantity={qty}, revenue={format_currency(rev)}\n"
                )
        else:
            f.write("  - None\n")

        f.write("\nAverage transaction value per region:\n")
        for region, stats in region_stats.items():
            avg_tx_val = (
                stats["total_sales"] / stats["transaction_count"]
                if stats["transaction_count"] > 0
                else 0.0
            )
            f.write(
                f"  - {region}: {format_currency(avg_tx_val)} per transaction\n"
            )
        f.write("\n")

        # 8. API ENRICHMENT SUMMARY
        f.write("API ENRICHMENT SUMMARY\n")
        f.write("======================\n")
        f.write(f"Total products enriched: {total_enriched}\n")
        f.write(f"Success rate: {success_rate:.2f}%\n")
        f.write("Products that couldn't be enriched:\n")
        if not_enriched_products:
            for pid in not_enriched_products:
                f.write(f"  - {pid}\n")
        else:
            f.write("  - None\n")

    print(f"[REPORT] Sales report saved to {output_file}")
