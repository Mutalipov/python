#tuples
mytuple = ("apple", "banana", "cherry")

thistuple = ("apple", "banana", "cherry")
print(thistuple)

#tupples are same with lists but unchangeable
#tuple() is constructor


#accessing tuple elements is same with list accessing


#changing tuples
x = ("apple", "banana", "cherry")
y = list(x)
y[1] = "kiwi"
x = tuple(y)

print(x)

#firstable changing its type to changeable(list, because set do not allows duplicates, but tuple allows), then rechangin into tuple


#unpack
fruits = ("apple", "banana", "cherry")

(green, yellow, red) = fruits

print(green) #apple
print(yellow) #banana
print(red)#cherry

#using asteriks *
fruits = ("apple", "banana", "cherry", "strawberry", "raspberry")

(green, yellow, *red) = fruits

print(green)
print(yellow)
print(red)

"""
apple
banana
['cherry', 'strawberry', 'raspberry']
"""

fruits = ("apple", "mango", "papaya", "pineapple", "cherry")

(green, *tropic, red) = fruits

print(green)
print(tropic)
print(red)
'''
apple
[mango,papaya,pineapple]
cherry
'''

#loop tuples
#looping through tuples are looks like looping over lists
thistuple = ("apple", "banana", "cherry")
i = 0
while i < len(thistuple):
  print(thistuple[i])
  i = i + 1

#join tuples
tuple1 = ("a", "b" , "c")
tuple2 = (1, 2, 3)

tuple3 = tuple1 + tuple2
print(tuple3)

#tuple methods: count(), index()