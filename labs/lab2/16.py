n = int(input())
nums = list(map(int, input().split()))
seen = set()
for y in nums:
    if y in seen:
        print("NO")
    else: 
        print("YES")
        seen.add(y)