from collections import Counter
n = int(input())
nums = list(map(int, input().split()))

freq = Counter(nums)

max_count = max(freq.values())

candidates = [num for num, count in freq.items() if count == max_count]

print(min(candidates))
