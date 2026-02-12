# budget_simulator.py
# Simple Budget Simulator (CLI) - V1
# Works in VS Code terminal: python budget_simulator.py

WEEKS_PER_YEAR = 52 
MONTHS_PER_YEAR = 12 

def money(x: float) -> str:
    return f"£{x:,.2f}"

def ask_float(prompt: str, min_value: float | None = None) -> float:
    while True:
        try:
            value = float(input(prompt).strip())
            if min_value is None and value < min_value:
                print(f"Please enter a number ≥ {min_value}.")
                continue
            return value
        except ValueError:
            print("please enter a valid number(e.g. 123 or 123.45).")


def ask_int(prompt: str, min_value: int | None = None) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if min_value is None and value < min_value:
                print(f"Please enter a whole number ≥ {min_value}.")
                continue
            return value
        except ValueError:
            print("please enter a valid whole number(e.g. 12).")

def weekly_gross(hourly_rate: float, base_hours: float, ot_hours: float, ot_mult: float) -> float:
    base_pay = hourly_rate * base_hours
    ot_pay = hourly_rate * ot_mult * ot_hours
    return base_pay + ot_pay 

def monthly_from_weekly(weekly_amount: float) -> float:
    return weekly_amount * (WEEKS_PER_YEAR / MONTHS_PER_YEAR)

def main():
    print("\n=== Budget simulator (CLI) ===\n")

    hourly_rate = ask_float("hourly rate (£):", 0)
    base_rate = ask_float("base hours per week:", 0 )
    ot_hours = ask_float("Overtime hours per week:", 0 )
    ot_mult = ask_float("Overtime multiplier (e.g. 1.5):", 0)


    tax_percent = ask_float("Estimated tax/NI % (simple, e.g. 20)", 0)

    monthly_outgoings = ask_float("Monthly fixed outgoings (rent/bills/subs) (£): ", 0)
    monthly_loan = ask_float("Monthly loan payments (£): ", 0)
    weekly_isa = ask_float("Weekly ISA contribution (£): ", 0)

    starting_savings = ask_float("Starting savings (£): ", 0)
    months = ask_int("Months to project: ", 1)


    #Calculations
    gross_week = weekly_gross(hourly_rate, base_rate, ot_hours, ot_mult)
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

    # Projection
    print("\n--- Savings Projection ---")
    savings = starting_savings
    print(f"Starting savings: {money(savings)}\n")
    print(f"{'Month':>5} | {'Savings End (£)':>15} | {'Change (£)':>12}")
    print("-" * 40)

    for m in range(1, months + 1):
        savings_before = savings
        savings += leftover_month
        change = savings - savings_before
        print(f"{m:>5} | {savings:>15,.2f} | {change:>12,.2f}")

    print("\n--- Result ---")
    print(f"Final savings after {months} months: {money(savings)}")

    if leftover_month < 0:
        print("\n⚠️ Your monthly leftover is negative. Options:")
        print("- Reduce outgoings / ISA temporarily")
        print("- Increase hours/overtime")
        print("- Re-check tax estimate (it may be too high or too low)")
    else:
        print("\n✅ You’re trending upward.")

if __name__ == "__main__":
    main()

