import decimal
import math


def convertScientificNotation2Decimal(num: decimal.Decimal | str) -> str:

    num = decimal.Decimal(num)
    str_num = str(num).upper()
    max_digit = len(str_num)
    if str_num.find("E") != -1:
        max_digit += abs(int(str_num.split(sep="E")[1]))
    decimal.getcontext().prec = max_digit
    num += decimal.Decimal("1")
    res = str(num)
    if res.find(".") == -1:
        tmp = int(res)
        tmp -= 1
        res = str(tmp)
        return res
    tmp = res.split(sep=".")
    t1 = int(tmp[0])
    t2 = tmp[1]
    t1 -= 1
    res = str(t1) + "." + t2
    return res

def execute(cmd: str, precision: int = 6) -> str:

    PREC = 1000000
    decimal.getcontext().prec = PREC

    cmd = cmd.strip()
    if cmd == "":
        return ""
    processed:list[str | decimal.Decimal] = []
    i = 0
    positive = True
    while i < len(cmd):
        ch = cmd[i]
        if ch.isdigit():
            if i > 0 and (cmd[i-1].isdigit() or cmd[i-1].isalpha() or cmd[i-1] == "."):
                ch = processed[-1]+ch
                processed.pop()
            else:
                if not positive:
                    ch = "-" + ch
            processed.append(ch)
        elif ch.isalpha():
            if i > 0 and cmd[i-1].isalpha():
                ch = processed[-1]+ch
                processed.pop()
            processed.append(ch)
        elif ch == "(":
            ii = i
            bracket = -1
            for j in range(i, len(cmd)):
                if cmd[j] == "(":
                    bracket += 1
                if cmd[j] == ",":
                    processed.append(execute(cmd[ii+1:j]))
                    ii = j
                if bracket == 0 and cmd[j] == ")":
                    processed.append(execute(cmd[ii+1:j]))
                    break
                if cmd[j] == ")":
                    bracket -= 1
            else:
                raise ValueError("语法错误: 左括号未匹配")
            i = j
        elif ch == ")":
            raise ValueError("语法错误: 右括号未匹配")
        else:
            if ch == ".":
                if processed[-1].isdigit():
                    processed[-1] += "."
                else:
                    raise ValueError("语法错误: 小数点单独出现")
            elif ch == "-":
                if i > 0 and cmd[i-1] == "-":
                    positive = False if positive else True
                elif i == 0:
                    positive = False
                else:
                    processed.append(ch)
            else:
                processed.append(ch)
        if ch != "-":
            positive = True
        i += 1

    i = 0
    while i < len(processed): # 第一优先级: 函数
        ch = processed[i]
        if ch.isalpha():
            if ch == "sqrt":
                if i < len(processed) - 1:
                    decimal.getcontext().prec = PREC
                    processed.pop(i)
                    processed[i] = decimal.Decimal(math.sqrt(decimal.Decimal(processed[i])))
                else:
                    raise ValueError("语法错误: 平方根函数单独出现")
            elif ch == "abs":
                if i < len(processed) - 1:
                    decimal.getcontext().prec = PREC
                    processed.pop(i)
                    processed[i] = decimal.Decimal(abs(decimal.Decimal(processed[i])))
                else:
                    raise ValueError("语法错误: 绝对值函数单独出现")
            else:
                raise ValueError("未定义错误: 没有定义函数 `%s`" % ch)
        i += 1

    i = 0
    while i < len(processed): # 第二优先级: 乘方
        ch = processed[i]
        if ch == "^":
            if i > 0 and i < len(processed) - 1:
                decimal.getcontext().prec = PREC
                processed.pop(i)
                x = decimal.Decimal(processed[i-1])
                y = decimal.Decimal(processed[i])
                processed[i] = 1
                if y < 0:
                    for j in range(-int(y)):
                        processed[i] *= x
                    processed[i] = decimal.Decimal("1") / processed[i]
                else:
                    for j in range(int(y)):
                        processed[i] *= x
                processed.pop(i-1)
                i -= 1
            else:
                raise ValueError("语法错误: 幂单独出现")
        i += 1

    i = 0
    while i < len(processed): # 第三优先级: 乘除
        ch = processed[i]
        if ch == "*":
            if i > 0 and i < len(processed) - 1:
                decimal.getcontext().prec = PREC
                processed.pop(i)
                processed[i] = decimal.Decimal(processed[i])
                processed[i] *= decimal.Decimal(processed[i-1])
                processed.pop(i-1)
                i -= 1
            else:
                raise ValueError("语法错误: 乘号单独出现")
        if ch == "/":
            if i > 0 and i < len(processed) - 1:
                decimal.getcontext().prec = PREC
                processed.pop(i)
                x = decimal.Decimal(processed[i-1])
                y = decimal.Decimal(processed[i])
                processed[i] = x / y
                processed.pop(i-1)
                i -= 1
            else:
                raise ValueError("语法错误: 除号单独出现")
        i += 1

    i = 0
    while i < len(processed): # 第四优先级: 加减
        ch = processed[i]
        if ch == "+":
            if i > 0 and i < len(processed) - 1:
                decimal.getcontext().prec = PREC
                processed.pop(i)
                processed[i] = decimal.Decimal(processed[i])
                processed[i] += decimal.Decimal(processed[i-1])
                processed.pop(i-1)
                i -= 1
            else:
                raise ValueError("语法错误: 加号单独出现")
        if ch == "-":
            if i > 0 and i < len(processed) - 1:
                decimal.getcontext().prec = PREC
                processed.pop(i)
                x = decimal.Decimal(processed[i-1])
                y = decimal.Decimal(processed[i])
                processed[i] = x - y
                processed.pop(i-1)
                i -= 1
            else:
                raise ValueError("语法错误: 减号单独出现")
        i += 1

    # def real_str(string: decimal.Decimal | float | int) -> str:
    #     print(type(string), string)
    #     tmp = decimal.Decimal(string)
    #     tmp = "%f" % tmp
    #     if tmp.find(".") == -1:
    #         return tmp
    #     tmp = tmp.split(sep=".")
    #     t1 = tmp[0]
    #     t2 = tmp[1]
    #     return t1 + "." + t2[:precision]
    ans = convertScientificNotation2Decimal(processed[0])
    if ans.find(".") == -1:
        return ans
    else:
        ans = "".join([ans.split(sep=".")[0], ".", ans.split(sep=".")[-1][:precision]])
    while ans.find(".") != -1 and len(ans) > 0 and ans[-1] == "0":
        ans = ans[:-1]
    if ans[-1] == ".":
        ans = ans[:-1]
    return ans

# print(execute("(1/sqrt(5))*(((1+sqrt(5))/2)^5-((1-sqrt(5))/2)^5)"))
