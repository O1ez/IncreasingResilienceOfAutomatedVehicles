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
    expr = pp.infixNotation(
        variable,
        [
        ("not", 1,  pp.opAssoc.RIGHT, fn_object.not_),
        ("and", 2,  pp.opAssoc.LEFT, fn_object.and_),
        ("or", 2,  pp.opAssoc.LEFT, fn_object.or_),
        ],
    )
    return expr

def parse_line(line: str):
    parser = make_infix(LeftAssociativeParsing)
    parsed_list = parser.parse_string(line)
    return parsed_list.as_list()[0]

class LeftAssociativeParsing:
    @staticmethod
    def not_(tokens):
        tokens = tokens[0]
        cur_op = [tokens[0], tokens[1]]
        return [cur_op]
    
    @staticmethod
    def and_(tokens):
        tokens = tokens[0]
        cur_op = tokens[0]
        ops = tokens[1::2]
        operands = tokens[2::2]
        for operator, operand in zip(ops, operands):
            cur_op =  [cur_op, operator, operand]
        return [cur_op]

    @staticmethod
    def or_(tokens):
        tokens = tokens[0]
        cur_op = tokens[0]
        for operator, operand in zip(tokens[1::2], tokens[2::2]):
            cur_op =  [cur_op, operator, operand]
        return [cur_op]