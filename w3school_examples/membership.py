"""
Docstring for w3school_examples.membership

in 	Returns True if a sequence with the specified value is present in the object	x in y	
not in	Returns True if a sequence with the specified value is not present in the object	x not in y

"""

#examples
fruits = ["apple", "banana", "cherry"]

print("banana" in fruits) #true

fruits = ["apple", "banana", "cherry"]

print("pineapple" not in fruits) #false

#membership in string
text = "Hello World"

print("H" in text)#true
print("hello" in text)#false
print("z" not in text)#true
