import math
n = int(input())
if n<2: print("No")
else: 
    prime = True
    for x in range(2,int(math.sqrt(n))+1):
        if n%x==0:
            prime = False
            break
if prime: print("Yes")
else: print("No")