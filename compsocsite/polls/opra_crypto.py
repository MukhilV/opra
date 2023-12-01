import random

def corresp_num(link_char):
    upper_list = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    lower = False
    local_char = link_char
    if link_char.islower():
        lower = True
        local_char = local_char.upper()
    result = upper_list.index(local_char) + 1
    if lower:
        result = -result
    return result
    
def corresp_char(linknum):
    link_num = linknum
    print(linknum)
    upper_list = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    lower_list = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    if link_num == 0:
        return "0"
    if link_num < 0:
        link_num = -link_num
        return lower_list[link_num-1]
    if link_num > 0:
        return upper_list[link_num-1]
    
def corresp_num_for_head(link_char):
    upper_list = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    lower = False
    local_char = link_char
    if link_char.islower():
        lower = True
        local_char = local_char.upper()
    result = upper_list.index(local_char) + 26
    if lower:
        result -= 26
    return result
    
def encrypt_head(base):
    upper_list = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    result = ""
    if base > 25:
        result = upper_list[base-26]
    else:
        result = upper_list[base].lower()
    return result
    
def replace_num_greater(codelist,diff):
    for x in range(len(codelist)):
        if codelist[x] > 0:
            if codelist[x] + 26 >= diff:
                codelist[x] -= diff
            else:
                codelist[x] = -codelist[x]
            break
    return codelist
    
def replace_num_smaller(codelist,diff):
    no_neg = True
    for x in range(len(codelist)):
        if codelist[x] < 0:
            no_neg = False
            if -codelist[x] + 26 >= diff:
                codelist[x] += diff
            else:
                codelist[x] = -codelist[x]
            break
    if no_neg:
        num = random.randint(0,len(codelist)-1)
        if 26 - codelist[num] >= diff:
            codelist[num] += diff
        else:
            codelist[num] = random.randint(codelist[num]+1,26)
    return codelist

def encrypt(id):
    code_length = 20
    code = ""
    base = id//300
    code += encrypt_head(base)
    base *= 300
    codelist = []
    for x in range(0,code_length):
        flag = random.randint(0,1)
        if flag == 0:
            codelist.append(-(random.randint(0,25)+1))
        else:
            codelist.append(random.randint(0,25)+1)
    while sum(codelist) != id - base:
        temp = sum(codelist)
        diff = temp - (id-base)
        if diff > 0:
            codelist = replace_num_greater(codelist,diff)
        else:
            codelist = replace_num_smaller(codelist,-diff)
    for item in codelist:
        code += corresp_char(item)
    return code
    
def decrypt(code):
    if code == "":
        return 0
    id = corresp_num_for_head(code[0])*300
    for item in code[1:]:
        id += corresp_num(item)
    return id