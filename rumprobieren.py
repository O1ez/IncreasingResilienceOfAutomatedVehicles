import pyparsing as pp

variable = pp.Word(pp.alphas)
expr = pp.infix_notation(
    variable,
    [
        ("not", 1, pp.opAssoc.RIGHT),
        ("and", 2, pp.opAssoc.LEFT),
        ("or", 2, pp.opAssoc.LEFT),
    ],
)

input_string = "(X and Y) and not Z or Y"
parsed = expr.parse_string(input_string)


print(parsed.as_list())