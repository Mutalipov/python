#creating functions
def my_function():
  print("Hello from a function")

#calling functions
def my_function():
  print("Hello from a function")

my_function()

def my_function():
  print("Hello from a function")

my_function()
my_function()
my_function()

#function names (valid)
calculate_sum()
_private_function()
myFunction2()


#why we use functions? In order to don't do same tasks several times
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)

def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))


