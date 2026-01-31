"""
is 	Returns True if both variables are the same object	x is y	
is not	Returns True if both variables are not the same object	x is not y
"""

#Examples
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x

print(x is z) #true
print(x is y) #false
print(x == y) #true

x = ["apple", "banana"]
y = ["apple", "banana"]

print(x is not y) #True

#Difference between is and == 
x = [1, 2, 3]
y = [1, 2, 3]

print(x == y) #True
print(x is y) #False