def mysum(a, b):
    return a+b

A = 5
B = 9
C = 10
if C == 10:
    print("True")
    C = A
    for i in range(C):
        print(i)
elif B == 10:
    print("True")
    C = B
    for i in range(C):
        print(i)
else:
    print(mysum(A, B))
    print("False")
