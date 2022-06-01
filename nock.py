#  A noun is an atom or a cell.
#  An atom is an unsigned integer.
#  A cell is a tuple of nouns.

#  nock(a)             *a
def nock(noun): return(tar(noun))

#  [a b c]             [a [b c]]
def expand(noun):
    if type(noun) == int:
        return(noun)
    elif len(noun) == 1:
        return(expand(noun[0]))
    else:
        return(expand(noun[0]), expand(noun[1:]))

def wut(noun):
    #  ?[a b]              0
    if type(noun) == tuple:
        return(0)
    #  ?a                  1
    else:
        return(1)

def lus(noun):
    #  +[a b]              +[a b]
    if type(noun) != int: 
        raise Exception(
            "Lus: {} is not an atom.".format(noun))
    #  +a                  1 + a
    else:
        return (noun + 1)

def tis(noun):
    #  =[a a]              0
    if noun[0] == noun[1]:
        return(0)
    #  =[a b]              1
    else:
        return(1)

def slot(noun):
    noun = expand(noun)
    address = noun[0]
    subject = noun[1]
    #  /[1 a]              a
    if address == 1:
        return(subject)
    #  /[2 a b]            a
    elif address == 2:
        return(subject[0])
    #  /[3 a b]            b
    elif address == 3:
        return(subject[1])
    #  /[(a + a) b]        /[2 /[a b]]
    elif (address % 2 == 0):
        return(slot((2, slot((int(address / 2),  subject)))))
    #  /[(a + a + 1) b]    /[3 /[a b]]
    elif (address % 2 == 1):
        return(slot((3, slot((int((address - 1) / 2), subject)))))
    #  /a                  /a
    else: 
        raise Exception(
            "Slot: {} is not a valid formula.".format(noun))

def edit(noun):
    noun = expand(noun)
    address = noun[0]
    new_value = noun[1][0]
    subject = noun[1][1]
    #  #[1 a b]            a
    if address == 1:
        return(new_value)
    #  #[(a + a) b c]      #[a [b /[(a + a + 1) c]] c]
    elif (address % 2 == 0):
        new_noun = (new_value, slot((address + 1, subject)))
        return(edit((int(address / 2), new_noun, subject)))
    #  #[(a + a + 1) b c]  #[a [/[(a + a) c] b] c]
    elif (address % 2 == 1):
        new_noun = (slot((address - 1, subject)), new_value)
        return(edit((int((address - 1) / 2), new_noun, subject)))
    #  #a                  #a
    else: 
        raise Exception(
            "Edit: {} is not a valid formula.".format(noun))

def tar(noun):
    noun = expand(noun)
    subject = noun[0]
    opcode = noun[1][0]
    #  *[a [b c] d]        [*[a b c] *[a d]]
    if wut(opcode) == 0:
        op_a = opcode
        op_b = noun[1][1]
        head = tar((subject, op_a))
        tail = tar((subject, op_b))
        return(head, tail)
    #  *[a 0 b]            /[b a]
    if opcode == 0:
        address = noun[1][1]
        return(slot((address, subject)))
    #  *[a 1 b]            b
    if opcode == 1:
        result = noun[1][1]
        return(result)
    #  *[a 2 b c]          *[*[a b] *[a c]]
    if opcode == 2:
        op_a = noun[1][1][0]
        op_b = noun[1][1][1]
        result_a = tar((subject, op_a))
        result_b = tar((subject, op_b))
        return(tar((result_a, result_b)))
    #  *[a 3 b]            ?*[a b]
    if opcode == 3:
        op = noun[1][1]
        result = tar((subject, op))
        return(wut(result))
    #  *[a 4 b]            +*[a b]
    if opcode == 4:
        op = noun[1][1]
        result = tar((subject, op))
        return(lus(result))
    #  *[a 5 b c]          =[*[a b] *[a c]]
    if opcode == 5:
        op_a = noun[1][1][0]
        op_b = noun[1][1][1]
        result_a = tar((subject, op_a))
        result_b = tar((subject, op_b))
        return(tis((result_a, result_b)))
    #  *[a 6 b c d]        *[a *[[c d] 0 *[[2 3] 0 *[a 4 4 b]]]]
    if opcode == 6:
        condition = noun[1][1][0]
        options = noun[1][1][1]
        choice = tar((subject, 4, 4, condition))
        head_or_tail = tar(((2, 3), 0, choice))
        consequent = tar((options, 0, head_or_tail))
        return(tar((subject, consequent)))
    #  *[a 7 b c]          *[*[a b] c]
    if opcode == 7:
        op_a = noun[1][1][0]
        op_b = noun[1][1][1]
        new_subject = tar((subject, op_a))
        return(tar((new_subject, op_b)))
    #  *[a 8 b c]          *[[*[a b] a] c]
    if opcode == 8:
        pin = noun[1][1][0]
        op = noun[1][1][1]
        new_subject = (tar((subject, pin)), subject)
        return(tar((new_subject, op)))
    #  *[a 9 b c]          *[*[a c] 2 [0 1] 0 b]
    if opcode == 9:
        address = noun[1][1][0]
        subject_mod = noun[1][1][1]
        new_subject = tar((subject, subject_mod))
        return(tar((new_subject, 2, (0, 1), 0, address)))
    #  *[a 10 [b c] d]     #[b *[a c] *[a d]]
    if opcode == 10:
        address = noun[1][1][0][0]
        op_a = noun[1][1][0][1]
        op_b = noun[1][1][1]
        new_value = tar((subject, op_a))
        new_subject = tar((subject, op_b))
        return(edit((address, new_value, new_subject)))
    #  *[a 11 [b c] d]     *[[*[a c] *[a d]] 0 3]
    #  *[a 11 b c]         *[a c]
    if opcode == 11:
        hint = noun[1][1][0]
        if wut(hint) == 0:
            op_a = hint[1]
            op_b = noun[1][1][1]
            new_subject = (tar((subject, op_a)), tar((subject, op_b)))
            return(tar((new_subject, 0, 3)))
        else:
            op = noun[1][1][1]
            return(tar((subject, op)))
    #  *a                  *a
    else: 
        raise Exception(
            "Tar: {} is not a valid formula.".format(noun))
