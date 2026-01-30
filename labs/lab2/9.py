n = int(input())
nums = list(map(int, input().split()))

max_value = max(nums)
min_value = min(nums)

nums = [min_value if x==max_value else x for x in nums]
print(*nums)