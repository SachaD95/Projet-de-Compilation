import lark
grammaire = lark.Lark(r"""
IDENTIFIER : /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE       : "int"
OPBIN      : /[+\-*\/<>]/

type : TYPE       -> type_int
     | IDENTIFIER -> type_struct

field_decl : type IDENTIFIER -> field_decl

struct_def : "typedef" "struct" "{" (field_decl ";")+ "}" IDENTIFIER ";" -> struct_def


decl : type IDENTIFIER "[" expression "]" -> decl_array
     | type IDENTIFIER                    -> decl_scalar

vars : (decl ",")* decl -> liste_vars


row : "{" [expression ("," expression)*] "}" -> row


expression : IDENTIFIER                                             -> variable
            | SIGNED_NUMBER                                          -> entier
            | expression OPBIN expression                            -> binaire
            | "(" expression ")"
            | "{" [expression ("," expression)*] "}"                 -> array_literal
            | "{" row ("," row)* "}"                                  -> array2d_literal
            | expression "[" expression "]" "[" expression "]"       -> index2d
            | expression "[" expression "]"                           -> index
            | expression "." IDENTIFIER                               -> field_access
            | "len" "(" expression ")"                                -> len
            | IDENTIFIER "(" [expression ("," expression)*] ")"       -> appel


lvalue : IDENTIFIER                                                  -> lvalue
       | lvalue "[" expression "]" "[" expression "]"                -> index2d_lvalue
       | lvalue "[" expression "]"                                    -> index_lvalue
       | lvalue "." IDENTIFIER                                        -> field_lvalue


commande : lvalue "=" expression ";"                                  -> assignation
         | type IDENTIFIER "=" expression ";"                         -> decl_init
         | decl ";"                                                    -> decl_commande
         | commande*                                                   -> sequence
         | "pass"                                                       -> pass
         | "print" "(" expression ")" ";"                              -> print
         | "if" "(" expression ")" "{" commande "}"                    -> if
         | "while" "(" expression ")" "{" commande "}"                 -> while
         | "for" "(" TYPE IDENTIFIER "=" expression ";" expression ";"IDENTIFIER "=" IDENTIFIER OPBIN expression ")""{" commande "}"-> for
 
fonction : type IDENTIFIER "(" vars ")" "{" commande "return" "(" expression ")" ";" "}" -> fonction

main : "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}" -> main

programme : struct_def* fonction* main -> programme

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="programme", ambiguity="resolve")



def pp_type(ast):
    if ast.data == "type_int":
        return "int"
    if ast.data == "type_struct":
        return ast.children[0].value



def pp_expression(ast):

    if ast.data == "variable":
        return ast.children[0].value

    if ast.data == "entier":
        return ast.children[0].value

    if ast.data == "binaire":
        gauche = pp_expression(ast.children[0])
        op     = ast.children[1].value
        droite = pp_expression(ast.children[2])
        return f"{gauche} {op} {droite}"

    if ast.data == "index":
        return f"{pp_expression(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "index2d":
        return (f"{pp_expression(ast.children[0])}"
                f"[{pp_expression(ast.children[1])}]"
                f"[{pp_expression(ast.children[2])}]")

    if ast.data == "row":
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"

    if ast.data == "array2d_literal":
        lignes = ", ".join(pp_expression(r) for r in ast.children)
        return "{" + lignes + "}"

    if ast.data == "array_literal":
        elements = ", ".join(pp_expression(c) for c in ast.children)
        return "{" + elements + "}"

    if ast.data == "len":
        return f"len({pp_expression(ast.children[0])})"

    if ast.data == "field_access":
        base  = pp_expression(ast.children[0])
        champ = ast.children[1].value
        return f"{base}.{champ}"

    if ast.data == "appel":
        #  pour les appels de fonction et les
        # constructeurs de structure : "fact(n-1)" ou "Point(2,4)"
        nom  = ast.children[0].value
        args = ", ".join(pp_expression(a) for a in ast.children[1:])
        return f"{nom}({args})"

    raise ValueError(f"pp_expression : cas non géré -> {ast.data}")




def pp_lvalue(ast):

    if ast.data == "lvalue":
        return ast.children[0].value

    if ast.data == "index_lvalue":
        return f"{pp_lvalue(ast.children[0])}[{pp_expression(ast.children[1])}]"

    if ast.data == "index2d_lvalue":
        return (f"{pp_lvalue(ast.children[0])}"
                f"[{pp_expression(ast.children[1])}]"
                f"[{pp_expression(ast.children[2])}]")

    if ast.data == "field_lvalue":
        base  = pp_lvalue(ast.children[0])
        champ = ast.children[1].value
        return f"{base}.{champ}"

    raise ValueError(f"pp_lvalue : cas non géré -> {ast.data}")



def pp_decl(ast):
    if ast.data == "decl_scalar":
        typ = pp_type(ast.children[0])
        nom = ast.children[1].value
        return f"{typ} {nom}"

    if ast.data == "decl_array":
        typ    = pp_type(ast.children[0])
        nom    = ast.children[1].value
        taille = pp_expression(ast.children[2])
        return f"{typ} {nom}[{taille}]"

    raise ValueError(f"pp_decl : cas non géré -> {ast.data}")


def pp_vars(ast):
    return ", ".join(pp_decl(d) for d in ast.children)




def pp_field_decl(ast):
    typ = pp_type(ast.children[0])
    nom = ast.children[1].value
    return f"    {typ} {nom}"


def pp_struct_def(ast):
    # children[:-1] = field_decl, children[-1] = nom de la structure
    champs = [pp_field_decl(c) for c in ast.children[:-1]]
    nom    = ast.children[-1].value
    corps  = ";\n".join(champs) + ";\n" if champs else ""
    return f"typedef struct {{\n{corps}}} {nom};\n"




def pp_commande(ast):

    if ast.data == "assignation":
        lhs = pp_lvalue(ast.children[0])
        rhs = pp_expression(ast.children[1])
        return f"{lhs} = {rhs};\n"

    if ast.data == "decl_init":
        # ex : Point p = Point(2,4);   ou   int x = 5;
        typ = pp_type(ast.children[0])
        nom = ast.children[1].value
        val = pp_expression(ast.children[2])
        return f"{typ} {nom} = {val};\n"

    if ast.data == "decl_commande":
        return pp_decl(ast.children[0]) + ";\n"

    if ast.data == "pass":
        return "pass\n"

    if ast.data == "print":
        return f"print({pp_expression(ast.children[0])});\n"

    if ast.data == "sequence":
        return "".join(pp_commande(c) for c in ast.children)

    if ast.data == "if":
        test  = pp_expression(ast.children[0])
        corps = pp_commande(ast.children[1])
        return f"if ({test}) {{\n{corps}}}\n"

    if ast.data == "while":
        test  = pp_expression(ast.children[0])
        corps = pp_commande(ast.children[1])
        return f"while ({test}) {{\n{corps}}}\n"

    if ast.data == "for":
        typ     = ast.children[0].value
        var     = ast.children[1].value
        init    = pp_expression(ast.children[2])
        cond    = pp_expression(ast.children[3])
        lhs_inc = ast.children[4].value
        src_inc = ast.children[5].value
        op_inc  = ast.children[6].value
        val_inc = pp_expression(ast.children[7])
        corps   = pp_commande(ast.children[8])
        return (f"for ({typ} {var} = {init}; {cond}; "
                f"{lhs_inc} = {src_inc} {op_inc} {val_inc}) {{\n{corps}}}\n")

    raise ValueError(f"pp_commande : cas non géré -> {ast.data}")




def pp_fonction(ast):
    # children : [type_retour, nom, vars, commande, expression_retour]
    typ    = pp_type(ast.children[0])
    nom    = ast.children[1].value
    params = pp_vars(ast.children[2])
    corps  = pp_commande(ast.children[3])
    retour = pp_expression(ast.children[4])
    return f"{typ} {nom}({params}) {{\n{corps}return ({retour});\n}}\n"


def pp_main(ast):
    # children : [vars, commande, expression_retour]
    params = pp_vars(ast.children[0])
    corps  = pp_commande(ast.children[1])
    retour = pp_expression(ast.children[2])
    return f"main({params}) {{\n{corps}return ({retour});\n}}\n"


def pp_programme(ast):
    morceaux = []
    for enfant in ast.children:
        if enfant.data == "struct_def":
            morceaux.append(pp_struct_def(enfant))
        elif enfant.data == "fonction":
            morceaux.append(pp_fonction(enfant))
        elif enfant.data == "main":
            morceaux.append(pp_main(enfant))
        else:
            raise ValueError(f"pp_programme : noeud inattendu -> {enfant.data}")
    return "\n".join(morceaux)




if __name__ == "__main__":
    src = open("test.c").read()
    t = grammaire.parse(src)

    print("******Pretty-print*********")
    print(pp_programme(t))
