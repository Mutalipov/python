n = int(input())
max = -2**31
for x in input().split():
    if int(x)>max: max = int(x)
print(max)