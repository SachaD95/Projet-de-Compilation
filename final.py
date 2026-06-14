import lark
import os

grammaire = lark.Lark(r"""
IDENTIFIER : /[a-zA-Z_][a-zA-Z_0-9]*/
TYPE       : "int"
OPBIN      : /[+\-*\/<>]/

type : TYPE       -> type_int
     | IDENTIFIER -> type_struct

field_decl : type IDENTIFIER "[" expression "]" -> field_decl_array
           | type IDENTIFIER                    -> field_decl_scalar

struct_def : "typedef" "struct" "{" (field_decl ";")+ "}" IDENTIFIER ";" -> struct_def

decl : type IDENTIFIER "[" expression "]" -> decl_array
     | type IDENTIFIER                    -> decl_scalar

vars : (decl ",")* decl -> liste_vars
     |                  -> liste_vide

row : "{" [expression ("," expression)*] "}" -> row

expression : IDENTIFIER                                               -> variable
           | SIGNED_NUMBER                                            -> entier
           | expression OPBIN expression                              -> binaire
           | "(" expression ")"
           | "{" [expression ("," expression)*] "}"                  -> array_literal
           | "{" row ("," row)* "}"                                  -> array2d_literal
           | expression "[" expression "]" "[" expression "]"        -> index2d
           | expression "[" expression "]"                           -> index
           | expression "." IDENTIFIER                               -> field_access
           | "len" "(" expression ")"                                -> len
           | expression "(" [expression ("," expression)*] ")"       -> appel

lvalue : IDENTIFIER                                         -> lvalue
       | lvalue "[" expression "]" "[" expression "]"       -> index2d_lvalue
       | lvalue "[" expression "]"                          -> index_lvalue
       | lvalue "." IDENTIFIER                              -> field_lvalue

instruction : lvalue "=" expression ";"                                  -> assignation
            | type IDENTIFIER "=" expression ";"                         -> decl_init
            | decl ";"                                                   -> decl_commande
            | "pass"                                                     -> pass_cmd
            | "print" "(" expression ")" ";"                             -> print
            | "if" "(" expression ")" "{" commande "}"                   -> if
            | "while" "(" expression ")" "{" commande "}"                -> while
            | "for" "(" TYPE IDENTIFIER "=" expression ";" expression ";" IDENTIFIER "=" IDENTIFIER OPBIN expression ")""{" commande "}" -> for

commande : instruction* -> sequence

fonction : type IDENTIFIER "(" [vars] ")" "{" commande "return" "(" expression ")" ";" "}" -> fonction

main : "main" "(" [vars] ")" "{" commande "return" "(" expression ")" ";" "}" -> main

programme : struct_def* fonction* main -> programme

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start="programme", ambiguity="resolve")


class PrettyPrinterC:
    def __init__(self):
        self.indent_lvl = 0

    def indent(self):
        return "    " * self.indent_lvl

    def format(self, node):
        if not isinstance(node, lark.Tree):
            return str(node.value)
        
        d = node.data
        c = node.children

        if d == "programme": return "\n\n".join(self.format(x) for x in c)
        
        elif d == "struct_def":
            fields = "".join(f"    {self.format(x)};\n" for x in c[:-1])
            return f"typedef struct {{\n{fields}}} {c[-1].value};"
        elif d == "type_int": return "int"
        elif d == "type_struct": return str(c[0].value)
        elif d == "field_decl_scalar": return f"{self.format(c[0])} {c[1].value}"
        elif d == "field_decl_array": return f"{self.format(c[0])} {c[1].value}[{self.format(c[2])}]"
        elif d == "decl_scalar": return f"{self.format(c[0])} {c[1].value}"
        elif d == "decl_array": return f"{self.format(c[0])} {c[1].value}[{self.format(c[2])}]"
        elif d == "liste_vars": return ", ".join(self.format(x) for x in c)
        elif d == "liste_vide": return ""
        elif d == "sequence": return "".join(self.format(x) for x in c)
        
        elif d == "entier": return str(c[0].value)
        elif d == "variable": return str(c[0].value)
        elif d == "binaire": return f"{self.format(c[0])} {c[1].value} {self.format(c[2])}"
        elif d == "array_literal": return "{" + ", ".join(self.format(x) for x in c) + "}"
        elif d == "row": return "{" + ", ".join(self.format(x) for x in c) + "}"
        elif d == "array2d_literal": return "{" + ", ".join(self.format(x) for x in c) + "}"
        elif d == "index": return f"{self.format(c[0])}[{self.format(c[1])}]"
        elif d == "index2d": return f"{self.format(c[0])}[{self.format(c[1])}][{self.format(c[2])}]"
        elif d == "field_access": return f"{self.format(c[0])}.{c[1].value}"
        elif d == "len": return f"len({self.format(c[0])})"
        elif d == "appel": return f"{self.format(c[0])}(" + ", ".join(self.format(x) for x in c[1:]) + ")"
        
        elif d == "lvalue": return str(c[0].value)
        elif d == "index_lvalue": return f"{self.format(c[0])}[{self.format(c[1])}]"
        elif d == "index2d_lvalue": return f"{self.format(c[0])}[{self.format(c[1])}][{self.format(c[2])}]"
        elif d == "field_lvalue": return f"{self.format(c[0])}.{c[1].value}"

        elif d == "assignation": return f"{self.indent()}{self.format(c[0])} = {self.format(c[1])};\n"
        elif d == "decl_init": return f"{self.indent()}{self.format(c[0])} {c[1].value} = {self.format(c[2])};\n"
        elif d == "decl_commande": return f"{self.indent()}{self.format(c[0])};\n"
        elif d == "pass_cmd": return f"{self.indent()}pass;\n"
        elif d == "print": return f"{self.indent()}print({self.format(c[0])});\n"
        elif d == "if":
            res = f"{self.indent()}if ({self.format(c[0])}) {{\n"
            self.indent_lvl += 1
            res += self.format(c[1])
            self.indent_lvl -= 1
            res += f"{self.indent()}}}\n"
            return res
        elif d == "while":
            res = f"{self.indent()}while ({self.format(c[0])}) {{\n"
            self.indent_lvl += 1
            res += self.format(c[1])
            self.indent_lvl -= 1
            res += f"{self.indent()}}}\n"
            return res
        elif d == "for":
            res = f"{self.indent()}for ({c[0].value} {c[1].value} = {self.format(c[2])}; {self.format(c[3])}; {c[4].value} = {c[5].value} {c[6].value} {self.format(c[7])}) {{\n"
            self.indent_lvl += 1
            res += self.format(c[8])
            self.indent_lvl -= 1
            res += f"{self.indent()}}}\n"
            return res

        elif d == "fonction":
            has_args = len(c) > 4 and c[2].data in ("liste_vars", "liste_vide")
            args = self.format(c[2]) if has_args else ""
            body_idx = 3 if has_args else 2
            ret_idx = 4 if has_args else 3
            res = f"{self.format(c[0])} {c[1].value}({args}) {{\n"
            self.indent_lvl += 1
            res += self.format(c[body_idx])
            res += f"{self.indent()}return ({self.format(c[ret_idx])});\n"
            self.indent_lvl -= 1
            return res + "}"

        elif d == "main":
            has_args = len(c) > 3 and c[0].data in ("liste_vars", "liste_vide")
            args = self.format(c[0]) if has_args else ""
            body_idx = 1 if has_args else 0
            ret_idx = 2 if has_args else 1
            res = f"main({args}) {{\n"
            self.indent_lvl += 1
            res += self.format(c[body_idx])
            res += f"{self.indent()}return ({self.format(c[ret_idx])});\n"
            self.indent_lvl -= 1
            return res + "}"

        return ""


structures = {}
structures_tailles = {}
array_lengths = {}
liste_fonctions = set()
fonction_types = {}
label_counter = 0

def get_new_label(prefix):
    global label_counter
    label_counter += 1
    return f"{prefix}_{label_counter}"

class Context:
    def __init__(self):
        self.vars = {}
        self.current_offset = 0

    def add_var(self, nom, typ, count=1):
        if nom in self.vars: return self.vars[nom]["offset"]
        size_unit = structures_tailles.get(typ, 8) if typ != "int" else 8
        total_size = size_unit * count
        self.current_offset -= total_size
        self.vars[nom] = {"offset": self.current_offset, "type": typ, "size": total_size, "count": count}
        return self.current_offset

    def get_var(self, nom):
        if nom not in self.vars: self.add_var(nom, "int")
        return self.vars[nom]

def resolve_expr_type(ast, ctx):
    if not isinstance(ast, lark.Tree): return "int", False
    if ast.data == "entier": return "int", False
    if ast.data in ("variable", "lvalue"):
        name = ast.children[0].value
        if name in liste_fonctions: return "int", False
        var = ctx.get_var(name)
        return var["type"], (var["count"] > 1 or var["type"] in structures)
    if ast.data == "binaire": return "int", False
    if ast.data in ("field_access", "field_lvalue"):
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        if base_type not in structures: return "int", False
        field_name = ast.children[1].value
        f_info = structures[base_type][field_name]
        return f_info["type"], (f_info["count"] > 1 or f_info["type"] in structures)
    if ast.data in ("index", "index_lvalue"):
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        return base_type, (base_type in structures)
    if ast.data in ("index2d", "index2d_lvalue"):
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        return base_type, (base_type in structures)
    if ast.data == "appel":
        func_expr = ast.children[0]
        if func_expr.data == "variable" and func_expr.children[0].value in fonction_types:
            ftype = fonction_types[func_expr.children[0].value]
            return ftype, (ftype in structures)
        return "int", False
    return "int", False

def compile_expression(ast, ctx):
    if not isinstance(ast, lark.Tree): return ""
    
    if ast.data == "entier":
        return f"    mov rax, {ast.children[0].value}\n"
        
    if ast.data == "variable":
        name = ast.children[0].value
        if name in liste_fonctions:
            return f"    mov rax, {name}\n"
        var = ctx.get_var(name)
        if var["count"] > 1 or var["type"] in structures:
            return f"    lea rax, [rbp{var['offset']}]\n"
        return f"    mov rax, [rbp{var['offset']}]\n"
        
    if ast.data == "binaire":
        asm = compile_expression(ast.children[0], ctx) + "    push rax\n"
        asm += compile_expression(ast.children[2], ctx) + "    mov rbx, rax\n    pop rax\n"
        op = ast.children[1].value
        if op == '+':   asm += "    add rax, rbx\n"
        elif op == '-': asm += "    sub rax, rbx\n"
        elif op == '*': asm += "    imul rax, rbx\n"
        elif op == '/': asm += "    cqo\n    idiv rbx\n"
        elif op == '<': asm += "    cmp rax, rbx\n    setl al\n    movzx rax, al\n"
        elif op == '>': asm += "    cmp rax, rbx\n    setg al\n    movzx rax, al\n"
        return asm
        
    if ast.data == "field_access":
        asm = compile_expression(ast.children[0], ctx)
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        field_name = ast.children[1].value
        if base_type in structures and field_name in structures[base_type]:
            f_info = structures[base_type][field_name]
            asm += f"    add rax, {f_info['offset']}\n"
            if f_info["count"] == 1 and f_info["type"] == "int":
                asm += "    mov rax, [rax]\n"
        return asm
        
    if ast.data == "index":
        asm = compile_expression(ast.children[0], ctx) + "    push rax\n"
        asm += compile_expression(ast.children[1], ctx) + "    push rax\n"
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        elem_size = 8 if base_type == "int" else structures_tailles.get(base_type, 8)
        asm += f"    pop rax\n    imul rax, {elem_size}\n    pop rbx\n    sub rbx, rax\n"
        if base_type in structures:
            asm += "    mov rax, rbx\n"
        else:
            asm += "    mov rax, [rbx]\n"
        return asm

    if ast.data == "index2d":
        asm = compile_expression(ast.children[0], ctx) + "    push rax\n"
        asm += compile_expression(ast.children[1], ctx) + "    shl rax, 3\n    pop rbx\n    sub rbx, rax\n    mov rbx, [rbx]\n    push rbx\n"
        asm += compile_expression(ast.children[2], ctx) + "    shl rax, 3\n    pop rbx\n    sub rbx, rax\n    mov rax, [rbx]\n"
        return asm
        
    if ast.data == "len":
        sub_expr = ast.children[0]
        if sub_expr.data == "variable": return f"    mov rax, {array_lengths.get(sub_expr.children[0].value, 1)}\n"
        return "    mov rax, 1\n"
        
    if ast.data == "appel":
        asm = compile_expression(ast.children[0], ctx) + "    push rax\n"
        regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
        for arg in ast.children[1:]: asm += compile_expression(arg, ctx) + "    push rax\n"
        for i in reversed(range(len(ast.children[1:]))):
            if i < len(regs): asm += f"    pop {regs[i]}\n"
        asm += "    pop rax\n    call rax\n"
        return asm
        
    if ast.data in ("array_literal", "row"):
        asm = ""
        for child in reversed(ast.children): asm += compile_expression(child, ctx) + "    push rax\n"
        return asm
        
    return "    mov rax, 0\n"

def compile_lvalue_address(ast, ctx):
    if ast.data == "lvalue":
        return f"    lea rcx, [rbp{ctx.get_var(ast.children[0].value)['offset']}]\n"
    if ast.data == "field_lvalue":
        asm = compile_lvalue_address(ast.children[0], ctx)
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        field_name = ast.children[1].value
        if base_type in structures and field_name in structures[base_type]:
            f_info = structures[base_type][field_name]
            asm += f"    add rcx, {f_info['offset']}\n"
        return asm
    if ast.data == "index_lvalue":
        asm = compile_lvalue_address(ast.children[0], ctx) + "    push rcx\n"
        asm += compile_expression(ast.children[1], ctx) + "    push rax\n"
        base_type, _ = resolve_expr_type(ast.children[0], ctx)
        elem_size = 8 if base_type == "int" else structures_tailles.get(base_type, 8)
        return asm + f"    pop rax\n    imul rax, {elem_size}\n    pop rbx\n    sub rbx, rax\n    mov rcx, rbx\n"
    if ast.data == "index2d_lvalue":
        asm = compile_lvalue_address(ast.children[0], ctx) + "    push rcx\n"
        asm += compile_expression(ast.children[1], ctx) + "    shl rax, 3\n    pop rcx\n    sub rcx, rax\n    mov rcx, [rcx]\n    push rcx\n"
        asm += compile_expression(ast.children[2], ctx) + "    shl rax, 3\n    pop rcx\n    sub rcx, rax\n"
        return asm
    return ""

def compile_commande(ast, ctx):
    if ast.data == "sequence": return "".join(compile_commande(c, ctx) for c in ast.children)
    
    if ast.data == "decl_init":
        typ = "int" if ast.children[0].data == "type_int" else ast.children[0].children[0].value
        nom = ast.children[1].value
        ctx.add_var(nom, typ)
        var = ctx.get_var(nom)
        asm = compile_expression(ast.children[2], ctx)
        if typ in structures_tailles:
            asm += f"    lea rcx, [rbp{var['offset']}]\n"
            qwords = structures_tailles[typ] // 8
            for i in range(qwords):
                asm += f"    mov rsi, [rax - {i*8}]\n    mov [rcx - {i*8}], rsi\n"
            return asm
        return asm + f"    mov [rbp{var['offset']}], rax\n"
        
    if ast.data == "decl_commande":
        d = ast.children[0]
        typ = "int" if d.children[0].data == "type_int" else d.children[0].children[0].value
        nom = d.children[1].value
        count = 1
        if d.data == "decl_array":
            if d.children[2].data == "entier": count = int(d.children[2].children[0].value)
            array_lengths[nom] = count
        ctx.add_var(nom, typ, count)
        return ""
        
    if ast.data == "assignation":
        lhs, rhs = ast.children[0], ast.children[1]
        if rhs.data in ("array_literal", "row"):
            asm = compile_expression(rhs, ctx) + compile_lvalue_address(lhs, ctx)
            for i in range(len(rhs.children)): asm += f"    pop rax\n    mov [rcx - {i*8}], rax\n"
            return asm
        asm = compile_expression(rhs, ctx) + "    push rax\n" + compile_lvalue_address(lhs, ctx) + "    pop rax\n"
        lhs_type, is_comp = resolve_expr_type(lhs, ctx)
        if is_comp and lhs_type in structures_tailles:
            qwords = structures_tailles[lhs_type] // 8
            for i in range(qwords): asm += f"    mov rsi, [rax - {i*8}]\n    mov [rcx - {i*8}], rsi\n"
            return asm
        return asm + "    mov [rcx], rax\n"
        
    if ast.data == "print": return compile_expression(ast.children[0], ctx) + "    mov rdi, format\n    mov rsi, rax\n    xor rax, rax\n    call printf\n"
    if ast.data == "if":
        l_fin = get_new_label(".end_if")
        return compile_expression(ast.children[0], ctx) + f"    cmp rax, 0\n    je {l_fin}\n" + compile_commande(ast.children[1], ctx) + f"{l_fin}:\n"
    if ast.data == "while":
        l_cond, l_fin = get_new_label(".w_cond"), get_new_label(".w_end")
        return f"{l_cond}:\n" + compile_expression(ast.children[0], ctx) + f"    cmp rax, 0\n    je {l_fin}\n" + compile_commande(ast.children[1], ctx) + f"    jmp {l_cond}\n{l_fin}:\n"
    if ast.data == "for":
        l_cond, l_fin, c = get_new_label(".f_cond"), get_new_label(".f_end"), ast.children
        ctx.add_var(c[1].value, c[0].value)
        asm = compile_expression(c[2], ctx) + f"    mov [rbp{ctx.get_var(c[1].value)['offset']}], rax\n{l_cond}:\n"
        asm += compile_expression(c[3], ctx) + f"    cmp rax, 0\n    je {l_fin}\n" + compile_commande(c[8], ctx)
        asm += f"    mov rax, [rbp{ctx.get_var(c[5].value)['offset']}]\n    push rax\n" + compile_expression(c[7], ctx) + "    mov rbx, rax\n    pop rax\n"
        if c[6].value == '+':   asm += "    add rax, rbx\n"
        elif c[6].value == '-': asm += "    sub rax, rbx\n"
        return asm + f"    mov [rbp{ctx.get_var(c[4].value)['offset']}], rax\n    jmp {l_cond}\n{l_fin}:\n"
    return ""

def compile_fonction(ast):
    nom, ctx, regs = ast.children[1].value, Context(), ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
    init_params_asm = ""
    if len(ast.children) > 4 and ast.children[2].data == "liste_vars":
        for i, d in enumerate(ast.children[2].children):
            typ = "int" if d.children[0].data == "type_int" else d.children[0].children[0].value
            ctx.add_var(d.children[1].value, typ)
            if i < len(regs): init_params_asm += f"    mov [rbp{ctx.get_var(d.children[1].value)['offset']}], {regs[i]}\n"
    body_idx, ret_idx = (3, 4) if len(ast.children) > 4 else (2, 3)
    asm = f"{nom}:\n    push rbp\n    mov rbp, rsp\n    sub rsp, 512\n" + init_params_asm
    return asm + compile_commande(ast.children[body_idx], ctx) + compile_expression(ast.children[ret_idx], ctx) + "    mov rsp, rbp\n    pop rbp\n    ret\n\n"

def compile_programme(ast):
    global structures, structures_tailles, array_lengths, liste_fonctions, fonction_types
    liste_fonctions.clear()
    fonction_types.clear()
    
    for c in ast.children:
        if c.data == "struct_def":
            s_name = c.children[-1].value
            structures[s_name], current_offset = {}, 0
            for field in c.children[:-1]:
                f_type = "int" if field.children[0].data == "type_int" else field.children[0].children[0].value
                f_name = field.children[1].value
                count = 1
                if field.data == "field_decl_array": count = int(field.children[2].children[0].value)
                unit_size = 8 if f_type == "int" else structures_tailles[f_type]
                total_field_size = unit_size * count
                structures[s_name][f_name] = {"offset": current_offset, "type": f_type, "count": count, "size": total_field_size}
                current_offset -= total_field_size
            structures_tailles[s_name] = abs(current_offset)
        elif c.data == "fonction":
            f_name = c.children[1].value
            f_type = "int" if c.children[0].data == "type_int" else c.children[0].children[0].value
            liste_fonctions.add(f_name)
            fonction_types[f_name] = f_type

    asm = "section .data\nformat: db \"%d\", 10, 0\nn: dq 0\n\nsection .text\nglobal main\nextern printf\nextern atoi\n\n"
    for c in ast.children:
        if c.data == "fonction": asm += compile_fonction(c)
    for c in ast.children:
        if c.data == "main":
            ctx = Context()
            asm += "main:\n    push rbp\n    mov rbp, rsp\n    sub rsp, 512\n"
            asm += "    push rsi\n    mov rdi, [rsp]\n    mov rdi, [rdi + 8]\n    call atoi\n    mov [n], rax\n    pop rsi\n\n"
            asm += compile_commande(c.children[1], ctx) + compile_expression(c.children[2], ctx) + "    mov rsp, rbp\n    pop rbp\n    ret\n"
    return asm

if __name__ == "__main__":
    if os.path.exists("final.c"):
        with open("final.c", "r") as f:
            code_c = f.read()
        try:
            tree = grammaire.parse(code_c)
            print(PrettyPrinterC().format(tree))
            with open("Result.asm", "w") as f:
                f.write(compile_programme(tree))
        except Exception as e:
            print(e)