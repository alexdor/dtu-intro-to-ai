import truths


possible_inputs = [
    # "p, p & q, p-> q, r | p",
    # "p & (!q), p -> !q, r, (r|!r)->p",
    # "!p->q, q->p, p->(r&s), (!p&!r)->s",
    # "r|!s, p, !q, p|q, (p|q)&!q&r&s, ((p|q)&!q)->p",
    # "p|q, p<=>q, (p|!q)&q, (r|s)->(p|q), !r|s",
]
not_inputs = [
    "p, p-> r, !r, !q -> p, q",
    # "p&(!q&(!p)),q->(r | !q),r",
    # "!p->q, q->p, p->(r&s), (p&r)->!s",
    # "p|q, p<=>q, (p|!q)&q, (r|s)->(p|q), !r&s",
]

kb_show = set()
kb_tell = set()
base = set()


def and_func(string_lits):
    str = string_lits
    return string_lits[0], str[1].replace("&", " and ")


def or_func(string_lits):
    str = string_lits
    return string_lits[0], str[1].replace("|", " or ")


def not_func(string_lits):
    str = string_lits
    return string_lits[0], str[1].replace("!", " not ")


def imp_func(string_lits):
    show = "|".join(
        [
            f"!{split}" if not (index % 2) else split
            for index, split in enumerate(string_lits[0].split("->"))
        ]
    )
    executable = " or ".join(
        [
            f" not {split}" if not (index % 2) else split
            for index, split in enumerate(string_lits[1].split("->"))
        ]
    )
    return show, executable


def bi_dir_func(string_lits):
    parts = string_lits[0].split("<=>")
    show = f"(!{parts[0]} | {parts[1]}) & (!{parts[1]} | {parts[0]})"
    ex = f"(not {parts[0]} or {parts[1]}) and (not {parts[1]} or {parts[0]})"
    return show, ex


def lit_func(string):
    for char in string[1].split():
        if len(char) == 1 and char not in ["$", "(", ")"]:
            kb_show.add(char)
            kb_tell.add(char)
            base.add(char)
    return string[0], string[1]


mapping = {
    "&": and_func,
    "|": or_func,
    "!": not_func,
    "->": imp_func,
    "<=>": bi_dir_func,
    "lit": lit_func,
}

symbols = list(mapping.keys())


def parenthetic_contents(string):
    """
    Generate parenthesized contents in string as pairs (level, contents).
    """
    stack = []
    for i, c in enumerate(string):
        if c == "(":
            stack.append(i)
        elif c == ")" and stack:
            start = stack.pop()
            yield (string[start + 1 : i])


def convert_prop(part):
    tmp = [part, part]
    while True:
        sep, found = find_sep(tmp[1])
        tmp = [" ".join(txt.split()) for txt in mapping[sep](tmp)]
        if not found:
            break
    return tmp


def find_sep(txt):
    for sep in symbols:
        parts = txt.split(sep)
        if len(parts) > 1:
            return sep, True
    return "lit", False


def parse_parenthesis(res, j):
    show_out = j
    existing_keys = {}
    mapping_dict = {}
    for i, segment in enumerate(res):
        if any(substring in segment for substring in existing_keys.keys()):
            for key, value in existing_keys.items():
                segment = segment.replace(key, value)
                show_out = show_out.replace(key, value)
        prop = convert_prop(segment)
        key = f"({segment})"
        show_out = show_out.replace(key, f"({prop[0]})")
        existing_keys[key] = f"${i}"
        mapping_dict[key] = prop[1]
    prop = convert_prop(show_out)
    while any(
        (substring in prop[0] or substring in prop[1])
        for substring in existing_keys.values()
    ):
        for key, value in existing_keys.items():
            prop[0] = prop[0].replace(value, key)
            prop[1] = prop[1].replace(value, mapping_dict[key])
    return prop


column_mapping = {}


def parse(input):
    for j in input.split(","):
        prop = convert_prop(j)
        res = list(parenthetic_contents(j))
        if res and len(res) > 0:
            prop = parse_parenthesis(res, j)
        if prop:
            show = "".join(prop[0].split())
            show = show.replace("!!", "")
            show = "".join(show.split())
            kb_show.add(show.strip())
            tell = " ".join(prop[1].split())
            tell = tell.replace("not not", "")
            tell = " ".join(tell.split())
            kb_tell.add(tell.strip())
            column_mapping[show] = tell
        else:
            print(f"ERROR: {j}")


def create_truth_table(base, kb_tell):
    t = truths.Truths(list(base), phrases=[s for s in kb_tell if s not in base])

    truth_table = []
    for conditions_set in t.base_conditions:
        truth_table.append(t.calculate(*conditions_set))

    return truth_table


# print("POSSIBLE INPUTS")
for i in possible_inputs + not_inputs:
    parse("".join(i.split()))


print("\nKB_SHOW:")
print(kb_show)

# print("\nKB_TELL:")
# print(kb_tell)


truth_table = create_truth_table(base, kb_tell)

print(truths.Truths(list(base), phrases=[s for s in kb_tell if s not in base]))
