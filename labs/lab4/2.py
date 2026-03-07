import re
s = input()
pattern = input()
smt = input()
t = re.sub(pattern,smt,s)
print(t)