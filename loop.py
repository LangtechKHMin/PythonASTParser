A = [1,1,2,3,4,5,6,7,8,9]
loop_point = [(1,4,5), (6,8,2)]
# 1에서 시작해서 4에서 끝나고 5번 도는 루프

path_track, loop_range = [], []
pointer = 0
loop = False
while True:
    if pointer == len(A):
        break
    else:
        if loop == False and len(loop_point) != 0:
            if A[pointer] == loop_point[0][0]:
                loop_count = loop_point[0][2]
                loop_exit = loop_point[0][1]
                loop = True
                loop_range.append(A[pointer])
                path_track.append(A[pointer])
                pointer += 1
            else:
                path_track.append(A[pointer])
                pointer += 1
        else:
            # loop == True
            if loop_exit == A[pointer]:
                loop_range.append(A[pointer])
                path_track.append(A[pointer])
                for n in range(loop_count-1):
                    path_track.extend(loop_range)
                loop = False
                loop_range = []
                loop_point.pop(0)
                pointer += 1
            else:
                loop_range.append(A[pointer])
                path_track.append(A[pointer])
                pointer += 1

print(path_track)
