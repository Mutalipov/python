from collections import defaultdict
n = int(input())
total = defaultdict(int)

for _ in range(n):
    line = input().split()
    name = line[0]
    value = int(line[1])
    total[name]+=value

for name in sorted(total.keys()):
    print(name,total[name])