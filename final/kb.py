import click
import truths

possible_inputs = [
    # "    p, p & q, p-> q, r | p",
    # "p & (!q), p -> !q, r, (r|!r)->p",
    # "!p->q, q->p, p->(r&s), (!p&!r)->s",
    "r|!s, p, !q, p|q, (p|q)&!q&r&s, (!q&(p|q))->p",
    # "p|q, p<->q, (p|!q)&q, (r|s)->(p|q), !r|s"
]
not_inputs = [
    # "p, p-> r, !r, !q -> p, q",
    # "p&(!q&(!p)),q->(r | !q),r",
    # "!p->q, q->p, p->(r&s), (p&r)->!s",
    # "p|q, p<->q, (p|!q)&q, (r|s)->(p|q), !r&s",
]

symbols = ["&", "|", "!", "<->", "->", "(", ")", ",", " ", ""]


class KB(object):
    kb_show = set()
    kb_tell = set()
    base = set()
    column_mapping = {}

    def __init__(self, debug=False):
        self.debug = debug
        self.mapping = {
            "&": self.and_func,
            "|": self.or_func,
            "!": self.not_func,
            "<->": self.bi_dir_func,
            "->": self.imp_func,
            "lit": self.lit_func,
        }
        self.symbols = list(self.mapping.keys())

    def and_func(self, string_lits):
        str = string_lits
        return string_lits[0], str[1].replace("&", " and ")

    def or_func(self, string_lits):
        str = string_lits
        return string_lits[0], str[1].replace("|", " or ")

    def not_func(self, string_lits):
        str = string_lits
        return string_lits[0], str[1].replace("!", " not ")

    def imp_func(self, string_lits):
        show = string_lits[0]
        executable = " or ".join(
            [
                f" not {split}" if not (index % 2) else split
                for index, split in enumerate(string_lits[1].split("->"))
            ]
        )
        return show, executable

    def bi_dir_func(self, string_lits):
        parts = string_lits[0].split("<->")
        show = string_lits[0]
        ex = (
            f"(not {parts[0]} or {parts[1]}) and (not {parts[1]} or {parts[0]})"
        )
        return show, ex

    def lit_func(self, string):
        for char in string[1].split():
            if len(char) == 1 and char not in ["$", "(", ")"]:
                self.kb_show.add(char)
                self.kb_tell.add(char)
                self.base.add(char)
        return string[0], string[1]

    def parenthetic_contents(self, string):
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

    def convert_prop(self, part):
        tmp = [part, part]
        while True:
            sep, found = self.find_sep(tmp[1])
            tmp = [" ".join(txt.split()) for txt in self.mapping[sep](tmp)]
            if not found:
                break
        return tmp

    def find_sep(self, txt):
        for sep in self.symbols:
            parts = txt.split(sep)
            if len(parts) > 1:
                return sep, True
        return "lit", False

    def parse_parenthesis(self, res, j):
        show_out = j
        existing_keys = {}
        mapping_dict = {}
        for i, segment in enumerate(res):
            if any(substring in segment for substring in existing_keys.keys()):
                for key, value in existing_keys.items():
                    segment = segment.replace(key, value)
                    show_out = show_out.replace(key, value)
            prop = self.convert_prop(segment)
            key = f"({segment})"
            show_out = show_out.replace(key, f"({prop[0]})")
            existing_keys[key] = f"${i}"
            mapping_dict[key] = prop[1]
        prop = self.convert_prop(show_out)
        while any(
            (substring in prop[0] or substring in prop[1])
            for substring in existing_keys.values()
        ):
            for key, value in existing_keys.items():
                prop[0] = prop[0].replace(value, key)
                prop[1] = prop[1].replace(value, mapping_dict[key])
        return prop

    def parse(self, input):
        for j in input.split(","):
            prop = self.convert_prop(j)
            res = list(self.parenthetic_contents(j))
            if res and len(res) > 0:
                prop = self.parse_parenthesis(res, j)
            if prop:
                show = "".join(prop[0].split())
                show = show.replace("!!", "")
                show = "".join(show.split())
                self.kb_show.add(show.strip())
                tell = " ".join(prop[1].split())
                tell = tell.replace("not not", "")
                tell = " ".join(tell.split())
                self.kb_tell.add(tell.strip())
                self.column_mapping[tell] = show
            else:
                print(f"ERROR: {j}")

    def get_truth_table(self, clauses):
        self.parse("".join(clauses.split()))
        literals = [
            "".join(lit.split())
            for lit in clauses.split(",")
            if len("".join(lit.split())) == 1
        ]

        base_list = list(self.base)
        base_len = len(base_list)
        phrases_list = list(self.kb_tell - self.base)
        if base_len < 1:
            raise NameError
        truth_table = truths.Truths(
            base_list,
            phrases=phrases_list,
            mapping=self.column_mapping,
            debug=self.debug,
        )

        kb_table = [
            [
                el
                for i, el in enumerate(row[:base_len])
                if base_list[i] in literals
            ]
            + row[base_len:]
            for row in truth_table.table_values
        ]

        kb_show_table = literals + [
            self.column_mapping[key] if key in self.column_mapping else key
            for key in phrases_list
        ]

        return literals, truth_table, kb_table, kb_show_table

    def run(self, clause_list):
        arg = ",".join(clause_list)
        literals, truth_table, kb_table, kb_show_table = self.get_truth_table(
            arg
        )

        if self.debug:
            print("INPUT:", "\n", arg, "\n")
            print("USER ENTERED LITERALS: ", literals, "\n")
            print("TRUTH TABLE:", "\n", truth_table, "\n")
            print("VALUES: ", kb_table, "\n")

        print("Current knowledge base:", set(kb_show_table))
        result = any(sum(row) == len(row) for row in kb_table)
        print(
            "Knowledge base is satisfiable"
            if result
            else "Knowledge base isn't satisfiable",
            "\n",
        )
        return result

    def contraction(self, clauses, last_clause):
        self.reset()
        literals, truth_table, kb_table, kb_show_table = self.get_truth_table(
            ",".join(clauses + [last_clause])
        )
        index = kb_show_table.index(last_clause)
        possible_spaces = [row for row in kb_table if row[index]]

        if len(possible_spaces) == 0:
            print(
                "There was an issue with you last clause so we had to drop it from the knowledge base"
            )
            return clauses

        if len(possible_spaces) == 1:
            return self.return_clean_kb(kb_show_table, possible_spaces[0])

        index = possible_spaces.index(max(possible_spaces))
        return self.return_clean_kb(kb_show_table, possible_spaces[index])

    def return_clean_kb(self, kb_show_table, possible_spaces):
        return [
            clause
            for i, clause in enumerate(kb_show_table)
            if possible_spaces[i]
        ]

    def reset(self):
        self = KB(self.debug)
        self.kb_show.clear()
        self.kb_tell.clear()
        self.base.clear()
        self.column_mapping = {}


def cleanup_input(tmp, debug):
    if str(tmp).lower() in ["quit", "exit", "break"]:
        click.echo("\nExiting program")
        return True, False, ""
    special_chars = tmp.translate(
        {
            ord(c): " "
            for c in "asdfghjklzxcvbnmqwertyuiopASDFGHJKLQWERTYUIOPZXCVBNM"
        }
    )
    if debug:
        print(special_chars)
    if len(special_chars.strip()) > 0 and not any(
        ((char in symbols) or any(c in symbols for c in char))
        for char in special_chars.split()
    ):
        click.echo("\nYou have added an unsupported character")
        return False, True, tmp
    while True:
        if tmp[-1:] == ",":
            tmp = tmp[:-1]
        else:
            click.echo()
            return False, False, tmp


@click.command()
@click.option("--debug", is_flag=True, default=False, help="Debug program")
def cli(debug):
    res = []
    kb = KB(debug)
    while True:
        try:
            tmp = click.prompt("Enter a new clause")
            tmp = ", ".join([val for val in tmp.split(",")])
            should_break, should_con, output = cleanup_input(tmp, debug)
            if should_break:
                break
            if should_con:
                continue
            tmp = [i.strip() for i in output.split(",")]
            res += tmp
            if kb.run(res):
                continue
            last_el = res.pop()
            res = list(set(res))
            tmp = kb.contraction(res, last_el)
            kb.reset()
            deleted_clauses = set([i for i in res + [last_el] if i not in tmp])
            print(
                "The following clauses were dropped in order to have a satisfiable knowledge base",
                deleted_clauses,
                "\n",
            )
            res = tmp
            print("Updated knowledge base:", set(res), "\n")
        except (NameError, SyntaxError) as err:
            click.echo(
                "Please use 1 character long literals"
                if err == NameError
                else "Your syntax is invalid, please try again"
            )
            res.pop()
            res = [v for v in res if v not in tmp]
            kb.reset()
            continue


if __name__ == "__main__":
    cli()
