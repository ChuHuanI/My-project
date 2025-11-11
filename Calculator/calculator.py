import sys

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error! Division by zero."
    return x / y

if len(sys.argv) != 4:
    print("Usage: python calculator.py <num1> <operator> <num2>")
    print("Operators: + - * /")
    sys.exit(1)

try:
    num1 = float(sys.argv[1])
    operator = sys.argv[2]
    num2 = float(sys.argv[3])
except ValueError:
    print("Invalid input. Please enter a number for num1 and num2.")
    sys.exit(1)

if operator == '+':
    print(num1, "+", num2, "=", add(num1, num2))
elif operator == '-':
    print(num1, "-", num2, "=", subtract(num1, num2))
elif operator == '*':
    print(num1, "*", num2, "=", multiply(num1, num2))
elif operator == '/':
    print(num1, "/", num2, "=", divide(num1, num2))
else:
    print("Invalid operator. Please use one of the following: + - * /")
    sys.exit(1)