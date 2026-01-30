n = int(input())
main = list(map(int, input().split()))
for i in range(n):
    main[i] = main[i]**2
print(*main)