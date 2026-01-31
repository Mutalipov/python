n = int(input())
db = {}
for _ in range(n):
    y = input().split()
    request = y[0]
    key = y[1]
    if request == "set":
        value = " ".join(y[2:])
        db[key] = value
    elif request == "get":
        if(key in db.keys()):
            print(db[key])
        else:
            print(f"KE: no key {key} found in the document")