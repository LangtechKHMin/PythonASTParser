import ast, re
import traceback
import sys
import json

class PythonASTParser:
    '''
    Class명 : astParser

    [1] Attribute
        (1) self.codes
            : Source Code Text File
        (2) self.depth_list
            : [Depth, Head, Argument]
        (3) self.var_dict
            : {변수명 : 변수 생성 라인 }
        (4) self.path
            : debugging line track
        (5) self.tree
            : code와 dump의 중간 단계 ast.parse 모듈의 output

    [2] Method
        (1) astErrorCheck(self)
            : self.codes => (구문오류 체크) => 수정된 self.codes
        (2) astDump(self, Execute = True)
            : self.codes를 ast.parse로 분석 및 컴파일 결과 출력 (True/False)
        (3)  astPreproc(self)
            : ast.Dump를 통해 lineno 및 col_offset 을 아래 parser로 분석하기 위한 전처리
        (4) elementParser(self, line)
            : 아래 objectParser 내부에서 각 요소들이 같은 head에 속한 argument인지 확인하는 부분
        (5) objectParser(self, line, depth, show = False)
            : (3)의 결과를 (HEAD)(ARGUMENT) 관계를 재귀적으로 분석하여 self.depth_list를 형성
        (6) codeParser(self, raw_code)
            : (3)의 결과를 (4)와 (5)를 통해 분석
        (7) pathTracker(self, show = True, short_path = True)
            : depth_list에서 line 정보를 정리하고 var_dict에 변수 및 함수들을 저장하여 debugging 순서인 self.path 형성
        (8) showStruct(self)
            : depth_list로부터 head 정보만 depth에 따라 출력한 것
        (9) loopFlagSetter(self.depth_list)
            : depth_list로부터 loop위치와 그곳으로 몇 번 돌아갈 지 찾기
        (10) astShow(self, DepthList, Lines)
            : 각 라인 별 코드의 구조를 \t와 \n, : 를 통해서 표현한 리스트 생성
        (11) finalPath(self, loop_dict, path)
            : loop 부분을 검출하여 path에 반영하는 코드
        (12) ast2json(self, line_struct)
            : 각 라인의 구조를 딕셔너리형식으로 변환하여, json으로 최종 변환 및 출력
    '''
    def __init__(self, _codes, depth):
        self.codes = _codes
        self.err_dict = {}  # {[line]:[error name]} => line source code & solution (compile 진행 여부 확인)

    def astErrorCheck(self):
        buffer = self.codes.split("\r")
        while True:
            self.codes = "\r".join(buffer)
            try:
                tree = ast.parse(self.codes)
                print("# Error Removed #")
                break
            except Exception as e:
                print("\r")
                ERR = traceback.format_exc().split("\r")
                # Syntax Error 처리 : 마지막 행 제외, 괄호 미충족 or 조건/제어문 콜론 미기입
                if 'SyntaxError: invalid syntax' in ERR[-2]:
                    if ''.join(buffer[:int(ERR[-5].split()[-1]) - 1]).count("(") != ''.join(
                            buffer[:int(ERR[-5].split()[-1]) - 1]).count(")"):
                        paren = True
                    else:
                        paren = False
                    if paren:
                        errline = int(ERR[-5].split()[-1]) - 2
                        print("괄호(')')를 주의하세요.")
                        print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline + 1, buffer[errline],
                                                                                    buffer[errline] + ")"))
                        self.err_dict[errline + 1] = "괄호가 닫히지 않았어요 ㅠ-ㅠ"
                        if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                            buffer[errline] = buffer[errline] + ")"
                            lines = "\r".join(buffer)
                        else:
                            sys.exit()
                    else:
                        if len(ERR[-3]) == len(ERR[-4]):
                            errline = int(ERR[-5].split()[-1]) - 1
                            print("콜론(:)을 주의하세요.")
                            print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline + 1, buffer[errline],
                                                                                        buffer[errline] + ":"))
                            self.err_dict[errline + 1] = "콜론을 쓰지 않았어요 ㅠ-ㅠ"
                            if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                                buffer[errline] = buffer[errline] + ":"
                                lines = "\n".join(buffer)
                            else:
                                sys.exit()
                        elif ERR[-4][ERR[-3].index("^")] == "=":  # v2
                            errline = int(ERR[-5].split()[-1]) - 1
                            print("비교 연산자를 주의하세요.")
                            print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline + 1, buffer[errline],
                                                                                        buffer[errline].replace(
                                                                                            ERR[-4][ERR[-3].index("^")],
                                                                                            "==")))
                            self.err_dict[errline + 1] = "잘못된 비교 연산자를 사용 하셨어요 ㅠ-ㅠ"
                            if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                                buffer[errline] = buffer[errline].replace(ERR[-4][ERR[-3].index("^")], "==")
                                lines = "\n".join(buffer)
                            else:
                                sys.exit()
                elif 'SyntaxError: unexpected EOF while parsing' in ERR[-2]:
                    errline = int(ERR[-5].split()[-1]) - 1
                    print("괄호(')')를 주의하세요.")
                    print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline + 1, buffer[errline],
                                                                                buffer[errline] + ")"))
                    self.err_dict[errline + 1] = "끝 줄 괄호가 닫히지 않았어요 ㅠ-ㅠ"
                    if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                        buffer[errline] = buffer[errline] + ")"
                        lines = "\n".join(buffer)
                    else:
                        sys.exit()

                elif 'SyntaxError: EOL while scanning string literal' in ERR[-2]:  # v2
                    errline = int(ERR[-5].split()[-1]) - 1
                    print("문자열의 Quotation('' 또는 "")을 주의하세요.")
                    temp = re.sub(r'[\"\']', '', buffer[errline])
                    result = temp.replace("(", "(\"")
                    result = result.replace(")", "\")")
                    print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline + 1, buffer[errline], result))
                    self.err_dict[errline + 1] = "문자열의 Quotation이 맞지 않아요 ㅠㅠ"
                    if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                        buffer[errline] = result
                        lines = "\n".join(buffer)
                    else:
                        sys.exit()

                elif 'IndentationError: unexpected indent' in ERR[-2]:  # v2
                    errline = int(ERR[-5].split()[-1]) - 1
                    print("들여쓰기를 주의하세요.")
                    if "    " in buffer[errline]:
                        result1 = buffer[errline][4:]
                    else:
                        result1 = ''
                    result2 = "    " + buffer[errline]
                    print(
                        "Error line [{0}]:{1}\nChange Direction : \n\n[1]\n{2}\n{3}\n{4}\n\n[2]\n{2}\n{5}\n{4}".format(
                            errline + 1, buffer[errline], buffer[errline - 1], result1, buffer[errline + 1], result2))
                    self.err_dict[errline + 1] = "들여쓰기가 맞지 않아요 ㅠㅠ"
                    if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                        line = int(input(
                            "\nWhat is the number of the direction you want to replace above the list? [LINE NUMBER]  "))
                        if line == 1:
                            buffer[errline] = result1
                            lines = "\r".join(buffer)
                        elif line == 2:
                            buffer[errline] = result2
                            lines = "\r".join(buffer)
                        else:
                            sys.exit()
                    else:
                        sys.exit()

    def astDump(self, Execute=True, Err_Check=True):
        tree = ast.parse(self.codes)
        self.tree = tree
        if Execute == True:
            print("\nPredicted Results:")
            if Err_Check == True:
                while True:
                    buffer = self.codes.split("\r")
                    self.codes = "\r".join(buffer)
                    try:
                        exec(compile(tree, '', 'exec'), {})
                        break
                    except Exception as e:
                        print("\n")
                        ERR = traceback.format_exc().split("\r")
                        err_var = ERR[-2].split()[2]
                        if 'NameError: ' in ERR[-2]:  # v2
                            errline = int(ERR[-3].split()[-3][:-1]) - 1
                            # print(errline)
                            print("선언되지 않은 변수 {0}를 사용하셨습니다. [내장함수 이름의 오류일 수 있습니다.]".format(err_var))
                            print("Error line [{0}]:{1}\nChange Direction : \n".format(errline + 1, buffer[errline]))
                            self.err_dict[errline + 1] = "선언되지 않은 변수를 썼어요 ㅇoㅇ!"
                            for n, k in enumerate(self.var_dict.keys()):
                                print("[{0}] {1}".format(n + 1, buffer[errline].replace(err_var[1:-1], k)))
                            if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                                line = int(input(
                                    "\nWhat is the number of the direction you want to replace above the list? [LINE NUMBER]  ")) - 1
                                buffer[errline] = buffer[errline].replace(err_var[1:-1],
                                                                          list(self.var_dict.keys())[line])
                                self.codes = "\r".join(buffer)
                                tree = ast.parse(self.codes)
                                self.tree = tree
                                print("Changed into : {0}".format(buffer[errline]))
                            else:
                                sys.exit()
        else:
            buffer = self.codes.split("\r")
            self.codes = "\r".join(buffer)
            exec(compile(tree, '', 'exec'), {})

    def astPreproc(self):
        C = ast.dump(self.tree, False, True)
        C = C.replace('[','')
        C = C.replace(']','')
        C = C.replace("()",'(null)')
        C = C.replace("('","(id(")
        C = C.replace("'",")")
        C = C.replace("lineno=","")
        C = C.replace("col_offset=","")
        # , )[abc] => , [abc])
        C = re.sub(r', \)([a-z]+)',r', method(\1', C)
        self.rawcode = C
        return C

    def elementParser(self, line):
        result = []
        elements = line.split(', ')
        buffer = ''
        for e in elements:
            if buffer != '':
                buffer += ", "
                buffer += e
            else:
                buffer += e
            if buffer.count("(") == buffer.count(")"):
                result.append(buffer)
                buffer = ''
        return result

    def objectParser(self, line, depth, show=False):
        # print(depth)
        import re
        object = re.compile('[A-Za-z]+?\(.*\)')
        head = re.compile('[A-Za-z]+?(?=\()')
        objs = re.findall(object, line)
        if len(objs) == 0:
            return 0
        elements = self.elementParser(objs[0])
        if len(elements) >= 2:
            for obj in elements:
                h = re.match(head, obj)[0]
                arg = re.sub(head, '', obj, 1)[1:-1]
                if show == True:
                    print("\t" * depth, h, arg)
                self.depth_list.append([depth, h, arg])
                self.objectParser(arg, depth + 1)
        else:
            h = re.match(head, objs[0])[0]
            arg = re.sub(head, '', objs[0], 1)[1:-1]
            if show == True:
                print("\t" * depth, h, arg)
            self.depth_list.append([depth, h, arg])
            self.objectParser(arg, depth + 1)

    def codeParser(self, raw_code):
        self.depth_list = []
        self.objectParser(raw_code, 0)
        # for a in self.depth_list:
        # print(a)
        # print()

    def pathTracker(self, short_path=True):
        self.var_dict = {}  # v2
        self.fun_dict = {}  # v2
        self.path = [1]
        self.lines = []
        target_list = self.depth_list[1:]
        for n, l in enumerate(target_list):
            # print(l[-1])
            N = n
            # depth list에서 line을 찾는 부분
            while True:
                if ', ' in target_list[N][-1]:
                    line = target_list[N][-1].split(", ")[-2]
                    if re.match(r'\d+?',line):
                        break
                    else:
                        N -= 1
                else:
                    N -= 1

            self.lines.append(line)
            ###################################
            # loop 처음과 끝을 찾아서 반복시키기 # loop_dict = {[start line : final line]}
            ###################################

            if short_path:
                # print(str(line)+" : ", end = '')
                if self.path[-1] != line:
                    self.path.append(line)
            else:
                self.path.append(line)

            if l[1] == 'Store':
                # print('변수 저장',target_list[n-1][2], end = '')
                self.var_dict[target_list[n - 1][2]] = line
            elif l[1] == 'FunctionDef':
                self.var_dict[target_list[n + 1][2]] = line
            elif l[1] == 'Load':
                # print("변수 또는 함수 불러오기", target_list[n-1][2], end = '')
                if target_list[n - 1][2] in self.var_dict:
                    # print('=>', self.var_dict[target_list[n-1][2]], '로 이동', end = '')
                    self.path.append(self.var_dict[target_list[n - 1][2]])
                else:
                    self.fun_dict[target_list[n - 1][2]] = line
                    # print("=> 내장 함수 호출", end = '')
            # print()
        print("Path Tracking Complete! You need to find loop point!")

    def showStruct(self):
        for l in self.depth_list:
            print("\t" * l[0], end='')
            print(l[1])

    def astShow(self, DepthList, Lines):
        DepthList = DepthList[1:]
        buf = ['' for i in range(int(Lines[-1]))]
        #print(buf)
        before = 0
        current = 0
        prior = 0
        for n in range(len(Lines)):
            current = int(Lines[n])
            if before >= DepthList[n][0]:
                if prior < current:
                    buf[prior-1] += " : "+ DepthList[n-1][2].split(", ")[0]+"}"
                    buf[prior-1] += "}" * (before-DepthList[n][0])
                else:
                    buf[current-1] += " : "+ DepthList[n-1][2].split(", ")[0]+"}"
                    buf[prior-1] += "}" * (before-DepthList[n][0])

            prior = current
            buf[current-1] += "\n"+"\t"*((DepthList[n][0])-1)+"{"+DepthList[n][1]
            before = DepthList[n][0]

        buf[-1] += " : "+ DepthList[-1][2].split(", ")[0]+"}"*(DepthList[-1][0])

        return buf

    def finalPath(self, loop_point, path):
        path_track, loop_range = [], []
        pointer = 0
        loop = False
        while True:
            if pointer == len(path):
                break
            else:
                if loop == False and len(loop_point) != 0:
                    if path[pointer] == loop_point[0][0]:
                        loop_count = loop_point[0][2]
                        loop_exit = loop_point[0][1]
                        loop = True
                        loop_range.append(path[pointer])
                        path_track.append(path[pointer])
                        pointer += 1
                    else:
                        path_track.append(path[pointer])
                        pointer += 1
                else:
                    # loop == True
                    if loop_exit == path[pointer]:
                        loop_range.append(path[pointer])
                        path_track.append(path[pointer])
                        for n in range(loop_count-1):
                            path_track.extend(loop_range)
                        loop = False
                        loop_range = []
                        loop_point.pop(0)
                        pointer += 1
                    else:
                        loop_range.append(path[pointer])
                        path_track.append(path[pointer])
                        pointer += 1

        self.path = path_track

    def ast2json(self, line_struct):
        self.json_dict = {}
        for n, line in enumerate(line_struct):
            if line == '':
                continue
            self.json_dict[n+1] = {}
            type = re.match(r'\W*?\{[A-Z]\w+(?=\n)',line)[0].split('{')[-1]
            args = re.findall(r'{.+?:.+?}',line)
            self.json_dict[n+1]['type'] = type
            for arg in args:
                tmp = arg.split(' : ')
                self.json_dict[n+1][tmp[0][1:]] = tmp[1][:-1]

            print(self.json_dict[n+1])
        struct_json = json.dumps(self.json_dict)

        return struct_json

    def loopFlagSetter(self, DepthList, Lines):
        ncount = 0
        count = False
        loop_switch = False
        self.loop_dict = []
        loop_start, loop_end = [], []
        for n,l in enumerate(DepthList):

            if count == True:
                if l[1] != 'Load':
                    ncount += 1
                else:
                    #print(ncount-4)
                    loop_count = ncount-4
                    #print(loop_end)
                    ncount = 0
                    count = False

            if loop_switch == True:
                if l[0] == loop_depth:
                    loop_end = Lines[n-2]
                    self.loop_dict.append((loop_start.pop(), loop_end, loop_count))
                    if len(loop_start)>= 1:
                        loop_switch = True
                    else:
                        loop_switch = False

            if n == len(DepthList)-1:
                if loop_switch == True:
                    loop_end = Lines[n-2]
                    self.loop_dict.append((loop_start.pop(), loop_end, loop_count))
                    if len(loop_start)>= 1:
                        loop_switch = True
                    else:
                        loop_switch = False
                else:
                    pass

            if l[1] == 'For':
                #if loop_switch == True:

                loop_start.append(Lines[n])
                #print("loop start",loop_start)
                #print(loop_start)
                loop_depth = l[0]
                loop_switch = True
                #print(DepthList[n+4])


                if DepthList[n+4][1] == "Call":
                    VAR = re.findall(r'(?<=Num\()\d{1,}(?=\,)',DepthList[n+4][2])
                    VAR = list(map(int,VAR))
                    #print(VAR)
                    if len(VAR) == 2:
                        VAR.append(1)
                    elif len(VAR) == 1:
                        VAR = [0, VAR[0], 1]

                    a, b, c = VAR
                    loop_count = (b-a-1)//c+1

                    #print("range 함수")
                elif DepthList[n+4][1] == "Tuple":
                    #print("튜플")
                    count = True
                elif DepthList[n+4][1] == "List":
                    #print("리스트")
                    count = True
            #print(l)
        #if loop_switch == True:

        #print("Loop points are detected!")

    def getResult(self):
        self.astErrorCheck()  # SyntaxError만 걸러줌
        # Name Error 내재한 채로 tree 형성
        self.astDump(False, False)
        code = self.astPreproc()
        self.codeParser(code)
        self.pathTracker(True)
        self.astDump(True, True)  # compile 결과를 낼 때, NameError가 Detection

        # Error 없는 코드로 재분석
        code = self.astPreproc()
        self.codeParser(code)
        self.pathTracker(True)
        self.loopFlagSetter(self.depth_list, self.lines)

        self.finalPath(self.loop_dict, self.path)
        print(self.path)
        line_struct = self.astShow(self.depth_list, self.lines)
        jsons = self.ast2json(line_struct)
        print(len(self.path), len(line_struct))
        path2json = []
        print(self.json_dict)
        for path in self.path:
            self.json_dict[int(path)]["lineno"] = int(path)
            path2json.append(self.json_dict[int(path)])

        # json.dumps(self.path2json) : path 라인에 따른 json
        # jsons : 전체 구조 json 객체
        return json.dumps(self.path2json), jsons
