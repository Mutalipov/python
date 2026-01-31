n = int(input())
ar = [input().strip() for _ in range(n)]

first = {}
for i,s in enumerate(ar):
    if s not in first:
        first[s] = i
for s in sorted(first):
    print(s, first[s]+1)