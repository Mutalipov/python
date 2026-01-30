n = int(input())
nums = list(map(int, input().split()))

max_value = -2**31
max_index = -1

for i, num in enumerate(nums):
    if num > max_value:
        max_value = num
        max_index = i+1

print(max_index)
