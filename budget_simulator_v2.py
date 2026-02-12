# budget_simulator_v2.py
# Budget Simulator (CLI) - V2
#  Savings goal + hit month/date, CSV export (added) 

from __future__ import annotations
from datetime import date
import csv

WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12

def money(x: float) -> str:
    return f"£{x:,.2f}"

def ask_float(prompt: str, min_value: float | None = None) -> float:
    while True:
        try:
            value = float(input(prompt).strip())
            if min_value is not None and value < min_value:
                print(f"Please enter a number ≥ {min_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number (e.g. 123 or 123.45).")

def ask_int(prompt: str, min_value: int | None = None) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if min_value is not None and value < min_value:
                print(f"Please enter a whole number ≥ {min_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number (e.g. 12).")

def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
    default = "Y/n" if default_yes else "y/N"
    while True:
        raw = input(f"{prompt} ({default}): ").strip().lower()
        if raw == "":
            return default_yes
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please enter y or n.")

def weekly_gross(hourly_rate: float, base_hours: float, ot_hours: float, ot_mult: float) -> float:
    base_pay = hourly_rate * base_hours
    ot_pay = hourly_rate * ot_mult * ot_hours
    return base_pay + ot_pay

def monthly_from_weekly(weekly_amount: float) -> float:
    return weekly_amount * (WEEKS_PER_YEAR / MONTHS_PER_YEAR)

def add_months(d: date, months: int) -> date:
    # Adds months without extra libraries.
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    # Clamp day to last valid day of target month
    # Find last day by stepping into next month and subtracting days
    # Simple manual approach:
    days_in_month = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    day = min(d.day, days_in_month)
    return date(y, m, day)

def main():
    print("\n=== Budget Simulator (CLI) V2 ===\n")

    # Inputs
    hourly_rate = ask_float("Hourly rate (£): ", 0)
    base_hours = ask_float("Base hours per week: ", 0)
    ot_hours = ask_float("Overtime hours per week: ", 0)
    ot_mult = ask_float("Overtime multiplier (e.g. 1.5): ", 0)

    tax_percent = ask_float("Estimated tax/NI % (simple, e.g. 20): ", 0)

    monthly_outgoings = ask_float("Monthly fixed outgoings (rent/bills/subs) (£): ", 0)
    monthly_loan = ask_float("Monthly loan payments (£): ", 0)
    weekly_isa = ask_float("Weekly ISA contribution (£): ", 0)

    starting_savings = ask_float("Starting savings (£): ", 0)
    months = ask_int("Months to project: ", 1)

    target_savings = ask_float("Savings goal / target (£): ", 0)

    # Calculations
    gross_week = weekly_gross(hourly_rate, base_hours, ot_hours, ot_mult)
    gross_month = monthly_from_weekly(gross_week)

    tax_rate = tax_percent / 100.0
    net_month = gross_month * (1 - tax_rate)

    isa_month = monthly_from_weekly(weekly_isa)
    expenses_month = monthly_outgoings + monthly_loan + isa_month
    leftover_month = net_month - expenses_month

    print("\n--- Monthly Summary (Estimated) ---")
    print(f"Gross monthly income: {money(gross_month)}")
    print(f"Net monthly income (after {tax_percent:.1f}%): {money(net_month)}")
    print(f"ISA per month (from weekly): {money(isa_month)}")
    print(f"Fixed outgoings: {money(monthly_outgoings)}")
    print(f"Loan payments: {money(monthly_loan)}")
    print(f"Total monthly expenses + ISA: {money(expenses_month)}")
    print(f"Monthly leftover (net - expenses): {money(leftover_month)}")

    # Projection table + goal tracking + rows for CSV
    print("\n--- Savings Projection ---")
    savings = starting_savings
    print(f"Starting savings: {money(savings)}\n")
    print(f"{'Month':>5} | {'Savings End (£)':>15} | {'Change (£)':>12}")
    print("-" * 40)

    start_date = date.today()
    goal_hit_month_index = None
    rows = []

    for m in range(1, months + 1):
        savings_before = savings
        savings += leftover_month
        change = savings - savings_before

        print(f"{m:>5} | {savings:>15,.2f} | {change:>12,.2f}")

        month_date = add_months(start_date, m - 1)
        rows.append({
            "month_number": m,
            "month_date": month_date.isoformat(),  # YYYY-MM-DD
            "gross_month": round(gross_month, 2),
            "net_month": round(net_month, 2),
            "isa_month": round(isa_month, 2),
            "fixed_outgoings": round(monthly_outgoings, 2),
            "loan_payments": round(monthly_loan, 2),
            "total_expenses_plus_isa": round(expenses_month, 2),
            "leftover_month": round(leftover_month, 2),
            "savings_end": round(savings, 2),
        })

        if goal_hit_month_index is None and savings >= target_savings:
            goal_hit_month_index = m

    print("\n--- Result ---")
    print(f"Final savings after {months} months: {money(savings)}")

    # Goal result
    print("\n--- Goal Tracking ---")
    print(f"Target savings: {money(target_savings)}")
    if goal_hit_month_index is not None:
        hit_date = add_months(start_date, goal_hit_month_index - 1)
        print(f"✅ Goal hit in month {goal_hit_month_index} (around {hit_date.strftime('%B %Y')}).")
    else:
        short_by = target_savings - savings
        print(f"❌ Goal not hit within {months} months. You’d be short by {money(short_by)}.")

    if leftover_month < 0:
        print("\n⚠️ Your monthly leftover is negative — savings will go down over time.")
        print("Try reducing outgoings/ISA, increasing hours, or adjusting the tax estimate.\n")

    # CSV export
    if ask_yes_no("\nExport projection to CSV?", default_yes=True):
        filename = input("CSV filename (default: projection.csv): ").strip() or "projection.csv"
        fieldnames = list(rows[0].keys()) if rows else []
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"✅ Saved: {filename} (in the same folder as this script)")
        except OSError as e:
            print(f"❌ Could not write CSV file: {e}")

if __name__ == "__main__":

    main()
