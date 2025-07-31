# This is an empty Python file. Add your code below.

def welcome_message():
    print("Welcome to the Python program!")
    name = input("Enter your name: ")
    print(f"Hello, {name}!")
    print("Take input from user to calculate gross pay.")
    hours_worked = float(input("Enter hours worked: "))
    hourly_rate = float(input("Enter hourly rate: "))
    gross_pay = hours_worked * hourly_rate
    print(f"Gross pay for {name} is: {gross_pay}")


if __name__ == "__main__":
    welcome_message()