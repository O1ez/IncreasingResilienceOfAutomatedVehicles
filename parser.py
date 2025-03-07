import pyparsing as pp


'''
CNF EBNF:
variable :: X + integer
literal :: "not" variable | variable | '(' literal ')'
clause :: variable ["or" variable]* | '(' clause ')'
formular :: clause ["and" clause]*
'''



def make_infix(fn_object):
    variable = pp.Word(pp.alphas + pp.nums)
    expr = pp.infix_notation(
        variable,
        [
        ("not", 1,  pp.OpAssoc.RIGHT, fn_object.not_),
        ("and", 2,  pp.OpAssoc.LEFT, fn_object.and_),
        ("or", 2,  pp.OpAssoc.LEFT, fn_object.or_),
        ],
    )
    return expr


class LeftAssociativeParsing:
    @staticmethod
    def not_(tokens):
        print(tokens)
        tokens = tokens[0]
        cur_op = [[tokens[0], tokens[1]]]
        print(cur_op)
        print("\n\n")
        return cur_op
    
    @staticmethod
    def and_(tokens):
        print(tokens)
        tokens = tokens[0]
        cur_op = tokens[0]
        ops = tokens[1::2]
        operands = tokens[2::2]
        for operator, operand in zip(ops, operands):
            #function = {'*': 'MUL', '/': 'DIV'}[operator]
            #cur_op = f"{function}({cur_op},{operand})"
            cur_op =  [cur_op, operator, operand]
        print(cur_op)
        print("\n\n")
        return [cur_op]

    @staticmethod
    def or_(tokens):
        print(tokens)
        tokens = tokens[0]
        cur_op = tokens[0]
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            #function = {'+': 'ADD', '-': 'SUB'}[operator]
            #cur_op = f"{function}({cur_op},{operand})"
            cur_op =  [cur_op, operator, operand]
        print(cur_op) 
        print("\n\n")
        return [cur_op]
    

if __name__=="__main__":
    #parser = make_custom_infix_notation(MakeIntoFunctions)
    #print(parser.parse_string("1+2/3+11/(12+7)"))
    
    parser = make_infix(LeftAssociativeParsing)
    
    print(("\n (X and Y and Z) or (not X and Z and not Y) or (X and not Y and Z)"))
    parsed_list = parser.parse_string("(not X and Z and not Y) or (X and not Y and Z)")
    print(parsed_list)
    
    print("\n\n-----------------------")
    parsed_list= parser.parse_string("(x and y) or (a and b) or (b and d)")
    print(parsed_list)