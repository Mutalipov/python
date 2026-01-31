n = int(input())
nums = [input() for _ in range(n)]
num = 0
checked = set()

for i in range(n):
    if nums[i] not in checked:
        count = nums.count(nums[i])
        if count == 3:
            num+=1
        checked.add(nums[i])
print(num)