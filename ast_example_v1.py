import re, ast, sys, traceback
def main():
    AST = astParser("example.py",7)
    AST.astErrorCheck()
    AST.astDump(True)
    code = AST.astPreproc()
    AST.codeParser(code)
    AST.pathTracker()
    AST.showStruct()
    print(AST.var_dict)
    for l in AST.depth_list:
        print(l)


class astParser():
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
            : depth_list로 부터 head 정보만 depth에 따라 출력한 것
    '''
    import re, ast, sys, traceback
    def __init__(self, codes, depth):
        with open(codes, "r") as source:
            lines = source.read()
        self.codes = lines
        self.depth_list = []
        self.var_dict = {}
        self.path = [1]

    def astErrorCheck(self):
        buffer = self.codes.split("\n")
        while True:
            self.codes = "\n".join(buffer)
            try:
                tree = ast.parse(self.codes)
                print("# Error Removed #")
                break
            except Exception as e:
                print("\n")
                ERR = traceback.format_exc().split("\n")
                # Syntax Error 처리 : 마지막 행 제외, 괄호 미충족 or 조건/제어문 콜론 미기입
                if 'SyntaxError: invalid syntax' in ERR[-2]:
                    if ''.join(buffer[:int(ERR[-5].split()[-1])-1]).count("(") != ''.join(buffer[:int(ERR[-5].split()[-1])-1]).count(")"):
                        paren = True
                    else:
                        paren = False
                    if paren:
                        errline = int(ERR[-5].split()[-1])-2
                        print("괄호(')')를 주의하세요.")
                        print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline+1,buffer[errline],buffer[errline]+")"))
                        if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                            buffer[errline] = buffer[errline]+")"
                            lines = "\n".join(buffer)
                        else:
                            sys.exit()
                    else:
                        errline = int(ERR[-5].split()[-1])-1
                        print("콜론(:)을 주의하세요.")
                        print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline+1,buffer[errline],buffer[errline]+":"))
                        if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                            buffer[errline] = buffer[errline]+":"
                            lines = "\n".join(buffer)
                        else:
                            sys.exit()
                elif 'SyntaxError: unexpected EOF while parsing' in ERR[-2]:
                    errline = int(ERR[-5].split()[-1])-1
                    print("괄호(')')를 주의하세요.")
                    print("Error line [{0}]:{1}\nChange Direction : {2}".format(errline+1,buffer[errline],buffer[errline]+")"))
                    if input("\nDo you want to automatically change above line? [y/n]  ") == 'y':
                        buffer[errline] = buffer[errline]+")"
                        lines = "\n".join(buffer)
                    else:
                        sys.exit()

    def astDump(self, Execute = True):
        tree = ast.parse(self.codes)
        self.tree = tree
        if Execute == True:
            print("\nPredicted Results:")
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


    def objectParser(self, line, depth, show = False):
        #print(depth)
        import re
        object = re.compile('[A-Za-z]+?\(.*\)')
        head = re.compile('[A-Za-z]+?(?=\()')
        objs = re.findall(object, line)
        if len(objs) ==0:
            return 0
        elements = self.elementParser(objs[0])
        if len(elements) >= 2:
            for obj in elements:
                h = re.match(head, obj)[0]
                arg = re.sub(head, '', obj,1)[1:-1]
                if show == True:
                    print("\t"*depth, h, arg)
                self.depth_list.append([depth,h,arg])
                self.objectParser(arg, depth+1)
        else:
            h = re.match(head, objs[0])[0]
            arg = re.sub(head, '', objs[0],1)[1:-1]
            if show == True:
                print("\t"*depth, h, arg)
            self.depth_list.append([depth,h,arg])
            self.objectParser(arg, depth+1)

    def codeParser(self, raw_code):
        self.objectParser(raw_code,0)
        #for a in self.depth_list:
            #print(a)
            #print()

    def pathTracker(self, show = True, short_path = True):

        target_list = self.depth_list[1:]
        for n, l in enumerate(target_list):
            #print(l[-1])
            N = n
            while True:
                if ', ' in target_list[N][-1]:
                    line = target_list[N][-1].split(", ")[-2]
                    if line != 'None':
                        break
                    else:
                        N-=1
                else:
                    N -= 1

            if short_path:
            #print(str(line)+" : ", end = '')
                if self.path[-1] != line:
                    self.path.append(line)
            else:
                self.path.append(line)

            if l[1] == 'Store':
                #print('변수 저장',target_list[n-1][2], end = '')
                self.var_dict[target_list[n-1][2]] = line
            elif l[1] == 'FunctionDef':
                self.var_dict[target_list[n+1][2]] = line
            elif l[1] == 'Load':
                #print("변수 또는 함수 불러오기", target_list[n-1][2], end = '')
                if target_list[n-1][2] in self.var_dict:
                    #print('=>', self.var_dict[target_list[n-1][2]], '로 이동', end = '')
                    self.path.append(self.var_dict[target_list[n-1][2]])
                else:
                    pass
                    #print("=> 내장 함수 호출", end = '')
            #print()
        if show:
            for p in self.path:
                print(p)
        else:
            pass

    def showStruct(self):
        for l in self.depth_list:
            print("\t"*l[0], end = '')
            print(l[1])



if __name__ == "__main__":
    main()
