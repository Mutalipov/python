main = list(map(int, input().split()))
l = main[1]-1
r = main[2]-1
nums = list(map(int, input().split()))
nums[l:r+1] = nums[l:r+1][::-1]
print(*nums)