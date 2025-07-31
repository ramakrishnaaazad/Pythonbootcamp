from datetime import datetime, timedelta

def add_months(start_date, months):
    """
    Adds the specified number of months to the start_date.
    Handles year and month rollover.
    """
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1
    day = min(start_date.day, [31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][month-1])
    return datetime(year, month, day)

if __name__ == "__main__":
    # Example usage
    date_str = input("Enter start date (YYYY-MM-DD): ")
    months_to_add = int(input("Enter number of months to add: "))
    start_date = datetime.strptime(date_str, "%Y-%m-%d")
    new_date = add_months(start_date, months_to_add)
    print(f"New date: {new_date.strftime('%Y-%m-%d')}")