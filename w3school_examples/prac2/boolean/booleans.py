#Boolean values
print(10 > 9)
print(10 == 9)
print(10 < 9)
#Example
a = 200
b = 33

if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")
#Evaluate values and variables
print(bool("Hello"))
print(bool(15))

x = "Hello"
y = 15

print(bool(x))
print(bool(y))

#Most values are true
'''
Almost any value is evaluated to True if it has some sort of content.

Any string is True, except empty strings.

Any number is True, except 0.

Any list, tuple, set, and dictionary are True, except empty ones.
'''
#Example
bool("abc")
bool(123)
bool(["apple", "cherry", "banana"])

#Some values are False
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})

#Example
class myclass():
  def __len__(self):
    return 0

myobj = myclass()
print(bool(myobj))

#Functions can return Boolean
def myFunction() :
  return True

print(myFunction())

#Example
def myFunction() :
  return True

if myFunction():
  print("YES!")
else:
  print("NO!")

x = 200
print(isinstance(x, int))