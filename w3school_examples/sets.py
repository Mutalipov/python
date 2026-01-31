#sets are like lists, but not allows duplicates. Also they are unordered, unindexed and unchangeable*. That means you cannot change element directly
#the constructor is set()

thisset = {"apple", "banana", "cherry"}

for x in thisset:
  print(x)

#not accessing through index

#adding new items
thisset = {"apple", "banana", "cherry"}

thisset.add("orange")

print(thisset)

thisset = {"apple", "banana", "cherry"}
tropical = {"pineapple", "mango", "papaya"}

thisset.update(tropical)

print(thisset)


thisset = {"apple", "banana", "cherry"}
mylist = ["kiwi", "orange"]

thisset.update(mylist)

print(thisset)

#removing
thisset = {"apple", "banana", "cherry"}

thisset.remove("banana")

print(thisset)


thisset = {"apple", "banana", "cherry"}

thisset.discard("banana")

print(thisset)

#if element does not exist, remove will raise error, discard not

thisset = {"apple", "banana", "cherry"}

x = thisset.pop()

print(x)

print(thisset)

#pop deletes random element

thisset = {"apple", "banana", "cherry"}

thisset.clear()

print(thisset)

thisset = {"apple", "banana", "cherry"}

del thisset

print(thisset)

#loop

thisset = {"apple", "banana", "cherry"}

for x in thisset:
  print(x)


#join sets
'''
The union() and update() methods joins all items from both sets.

The intersection() method keeps ONLY the duplicates.

The difference() method keeps the items from the first set that are not in the other set(s).

The symmetric_difference() method keeps all items EXCEPT the duplicates.
'''
set1 = {"a", "b", "c"}
set2 = {1, 2, 3}

set3 = set1.union(set2)
print(set3)

set1 = {"a", "b", "c"}
set2 = {1, 2, 3}

set3 = set1 | set2
print(set3)

set1 = {"a", "b", "c"}
set2 = {1, 2, 3}
set3 = {"John", "Elena"}
set4 = {"apple", "bananas", "cherry"}

myset = set1.union(set2, set3, set4)
print(myset)

set1 = {"a", "b", "c"}
set2 = {1, 2, 3}
set3 = {"John", "Elena"}
set4 = {"apple", "bananas", "cherry"}

myset = set1 | set2 | set3 |set4
print(myset)

x = {"a", "b", "c"}
y = (1, 2, 3)

z = x.union(y)
print(z)

#update does not need in creating new set
set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set3 = set1.intersection(set2)
print(set3) #apple

set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set3 = set1 & set2
print(set3)

set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set1.intersection_update(set2)

print(set1)

set1 = {"apple", 1,  "banana", 0, "cherry"}
set2 = {False, "google", 1, "apple", 2, True}

set3 = set1.intersection(set2)

print(set3)

set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set3 = set1.difference(set2)

print(set3)


set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set3 = set1 - set2
print(set3)

set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set1.difference_update(set2)

print(set1)


set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set3 = set1.symmetric_difference(set2)

print(set3)


set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set3 = set1 ^ set2
print(set3)


set1 = {"apple", "banana", "cherry"}
set2 = {"google", "microsoft", "apple"}

set1.symmetric_difference_update(set2)

print(set1)



#frozen set
#frozen set is set, that can not be changed


#methods
'''
copy()	 	Returns a shallow copy	
difference()	-	Returns a new frozenset with the difference	
intersection()	&	Returns a new frozenset with the intersection	
isdisjoint()	 	Returns whether two frozensets have an intersection	
issubset()	<= / <	Returns True if this frozenset is a (proper) subset of another	
issuperset()	>= / >	Returns True if this frozenset is a (proper) superset of another	
symmetric_difference()	^	Returns a new frozenset with the symmetric differences	
union()	|	Returns a new frozenset containing the union
'''

#set methods
'''
add()	 	Adds an element to the set
clear()	 	Removes all the elements from the set
copy()	 	Returns a copy of the set
difference()	-	Returns a set containing the difference between two or more sets
difference_update()	-=	Removes the items in this set that are also included in another, specified set
discard()	 	Remove the specified item
intersection()	&	Returns a set, that is the intersection of two other sets
intersection_update()	&=	Removes the items in this set that are not present in other, specified set(s)
isdisjoint()	 	Returns whether two sets have a intersection or not
issubset()	<=	Returns True if all items of this set is present in another set
 	<	Returns True if all items of this set is present in another, larger set
issuperset()	>=	Returns True if all items of another set is present in this set
 	>	Returns True if all items of another, smaller set is present in this set
pop()	 	Removes an element from the set
remove()	 	Removes the specified element
symmetric_difference()	^	Returns a set with the symmetric differences of two sets
symmetric_difference_update()	^=	Inserts the symmetric differences from this set and another
union()	|	Return a set containing the union of sets
update()	|=	Update the set with the union of this set and others
'''