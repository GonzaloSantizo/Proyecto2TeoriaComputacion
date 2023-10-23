import re
import itertools as it
from graphviz import Digraph
import time

# CNF
def nullableSymble(gram_argument):
    nullable = set()
    change = True

    while change:
        change = False
        for production in gram_argument:
            head, body = production.split(' → ')
            bodys = body.split(' | ')
            for body in bodys:
                body = body.split(' ')
                if 'ε' in body or all(simbolo in nullable for simbolo in body):
                    if head not in nullable:
                        nullable.add(head)
                        change = True

    return nullable

# This function eliminates epsilon productions from the grammar.
def eliminate_prod_epsilon(gram_argument):
    nullable = nullableSymble(gram_argument)
        
    nuevaGram = []

    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')

        new_bodies = set(bodys)
        
        for body in bodys:
            body = body.split(' ')
            
            nullable_body = []
            for i in range(len(body)):
                if body[i] in nullable:
                    nullable_body.append({"symbol":body[i],"position":i})

            for i in range(1,len(nullable_body)+1):
                combinations = it.combinations(nullable_body, r=i)

                for combination in combinations:
                    nuevobody = body.copy()
                    for item in combination:
                        i = item["position"]
                        nuevobody[i]=" "
                    
                    while " " in nuevobody:
                        nuevobody.remove(" ")
                        
                    if len(nuevobody)>0:
                        new_bodies.add(' '.join(nuevobody))
                    
                        
                    
        if 'ε' in new_bodies:
            new_bodies.remove('ε')
        
        if len(new_bodies)>0:
            nuevaGram.append(head + ' → ' + ' | '.join(new_bodies))
        
    return nuevaGram

# Checks if a production is valid based on a given pattern.
def prod_valid(pattern, production):
    return bool(re.match(pattern, production))

# Extracts non-terminals from the grammar.
def non_terminal_symbol(gram_argument):
    non_terminal = set()

    for production in gram_argument:
        non_terminal.add(production.split(' → ')[0])
    
    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        
        for body in bodys:
            body = body.split(' ')
            for simbolo in body:
                if simbolo.isupper():
                    non_terminal.add(simbolo)
        
    return non_terminal

# Extracts terminals from the grammar.
def terminal_symbol(gram_argument):
    non_terminal = non_terminal_symbol(gram_argument)
    terminales = set()

    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        
        for body in bodys:
            body = body.split(' ')
            for simbolo in body:
                if simbolo not in non_terminal:
                    terminales.add(simbolo)
        
    return terminales

# Finds unary productions in the grammar.
def Unary_operator(gram_argument, non_terminal):
    prods_unarias = set()
    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        
        for body in bodys:
            if body in non_terminal:
                prods_unarias.add((head, body))
    
    return prods_unarias

# Finds non-unary productions in the grammar.
def non_unary_operator(gram_argument, non_terminal):
    non_unary_prods = set()
    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        
        for body in bodys:
            if body not in non_terminal:
                non_unary_prods.add((head, body))
    
    return non_unary_prods

# Eliminates unary productions from the grammar.
def eliminate_unary(gram_argument):
    nuevaGram = []
    non_terminal = non_terminal_symbol(gram_argument)
    prods_unarias = Unary_operator(gram_argument, non_terminal)
    non_unary_prods = non_unary_operator(gram_argument, non_terminal) 

    parejas_unarias = set()
    for simbolo in non_terminal:
        parejas_unarias.add((simbolo, simbolo))
    
    change = True
    
    parejas_nueva_gram = set()
    
    while change:
        change = False
        for pareja in parejas_unarias.copy():
            for prod in prods_unarias:
                if pareja[1] == prod[0] and (pareja[0], prod[1]) not in parejas_unarias:
                    parejas_unarias.add((pareja[0], prod[1]))
                    change = True
                    
    for pareja in parejas_unarias:
        for prod in non_unary_prods:
            if pareja[1] == prod[0]:
                parejas_nueva_gram.add((pareja[0], prod[1]))
    
    for simbolo in non_terminal:
        new_bodies = set()
        
        for pareja in parejas_nueva_gram:
            if simbolo == pareja[0]:
                new_bodies.add(pareja[1])
        
        if len(new_bodies) > 0:
            nuevaGram.append(simbolo + ' → ' + ' | '.join(new_bodies))
            
    return nuevaGram

# Finds symbols that can generate terminals.
def simbolosGeneran(gram_argument):
    simbolos_generan = terminal_symbol(gram_argument)
    
    change = True

    while change:
        change = False
        for production in gram_argument:
            head, body = production.split(' → ')
            bodys = body.split(' | ')
            for body in bodys:
                body = body.split(' ')
                if all(simbolo in simbolos_generan for simbolo in body):
                    if head not in simbolos_generan:
                        simbolos_generan.add(head)
                        change = True
                        
    return simbolos_generan

# Eliminates symbols that do not generate terminals from the grammar.
def eliminate_non_generator(gram_argument):
    simbolos_generan = simbolosGeneran(gram_argument)
    nuevaGram = []
    
    for production in gram_argument:
        if production.split(' → ')[0] in simbolos_generan:
            nuevaGram.append(production)
        
    for production in nuevaGram.copy():
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        new_bodies = set(bodys)
        
        for body in bodys:
            body = body.split(' ')
            if any(simbolo not in simbolos_generan for simbolo in body):
                new_bodies.remove(' '.join(body))
        
        nuevaGram.remove(production)
        if len(new_bodies) > 0:
            nuevaGram.append(head + ' → ' + ' | '.join(new_bodies))
    
    return nuevaGram

# Finds symbols that are reachable from the start symbol.
def reachable_symbols(gram_argument, simboloInicial):
    simbolos_alcanzables = set(simboloInicial)
    change = True

    while change:
        change = False
        for production in gram_argument:
            head, body = production.split(' → ')
            bodys = body.split(' | ')
            
            if head in simbolos_alcanzables:
                for body in bodys:
                    body = body.split(' ')
                    for simbolo in body:
                        if simbolo not in simbolos_alcanzables:
                            simbolos_alcanzables.add(simbolo)
                            change = True
                        
    return simbolos_alcanzables

# Eliminates symbols that are not reachable from the start symbol.
def eliminarSimbolosNoAlcanzables(gram_argument, simboloInicial):
    simbolos_alcanzables = reachable_symbols(gram_argument, simboloInicial)
    nuevaGram = []
                    
    for production in gram_argument:
        if production.split(' → ')[0] in simbolos_alcanzables:
            nuevaGram.append(production)
    
    for production in nuevaGram.copy():
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        new_bodies = set(bodys)
        
        for body in bodys:
            body = body.split(' ')
            if any(simbolo not in simbolos_alcanzables for simbolo in body):
                new_bodies.remove(' '.join(body))
        
        nuevaGram.remove(production)
        if len(new_bodies) > 0:
            nuevaGram.append(head + ' → ' + ' | '.join(new_bodies))

    return nuevaGram

# Eliminates symbols that are not useful in the grammar.
def eliminarSimbolosInutiles(gram_argument, simboloInicial):
    nuevaGram = eliminate_non_generator(gram_argument)
    nuevaGram = eliminarSimbolosNoAlcanzables(nuevaGram, simboloInicial)
    
    return nuevaGram

# Generates a new symbol based on the state.
def generarSimbolo(state):
    return state[0:2] + chr(ord(state[2]) + 1)

# Transforms the grammar to Chomsky Normal Form (CNF) - Part A.
def cnfA(gram_argument):
    state_counter = 'X_0'
    terminales = terminal_symbol(gram_argument)
    nuevaGram = []
    nuevasProd = set()
    
    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        
        for body in bodys:
            if body not in terminales:
                body = body.split(' ')
                
                for simbolo in body:
                    if simbolo in terminales and simbolo not in [item[1] for item in nuevasProd]:
                        state_counter = generarSimbolo(state_counter)
                        nuevasProd.add((state_counter, simbolo))

    for item in nuevasProd:
        nuevaGram.append(item[0] + ' → ' + item[1])

    for production in gram_argument:
        head, body = production.split(' → ')
        bodys = body.split(' | ')
        
        new_bodies = set()
        
        for body in bodys:
            if body not in terminales:
                body = body.split(' ')
                
                for simbolo in body:
                    for item in nuevasProd:
                        if simbolo == item[1]:
                            i = body.index(simbolo)
                            body[i] = item[0]
            
                body = ' '.join(body)
            
            new_bodies.add(body)
            
        if len(new_bodies) > 0:
            nuevaGram.append(head + ' → ' + ' | '.join(new_bodies))

    return nuevaGram

# Transforms the grammar to Chomsky Normal Form (CNF) - Part B.
def cnfB(gram_argument):
    state_counter = 'C_0'
    terminales = terminal_symbol(gram_argument)
    change = True
    
    while change:
        nuevaGram = []
        nuevasProd = set()
        change = False
        for production in gram_argument:
            head, body = production.split(' → ')
            bodys = body.split(' | ')
        
            for body in bodys:
                if body not in terminales:
                    body = body.split(' ')
                    if len(body) >= 3 and (body[len(body) - 2], body[len(body) - 1]) not in [item[1] for item in nuevasProd]:
                        state_counter = generarSimbolo(state_counter)
                        nuevasProd.add((state_counter, (body[len(body) - 2], body[len(body) - 1])))
                        change = True
                        
        for item in nuevasProd:
            nuevaGram.append(item[0] + ' → ' + item[1][0] + ' ' + item[1][1])
        
        for production in gram_argument:
            head, body = production.split(' → ')
            bodys = body.split(' | ')
        
            new_bodies = set()
        
            for body in bodys:
                if body not in terminales:
                    body = body.split(' ')
                
                    if len(body) >= 3:
                        for item in nuevasProd:
                            if (body[len(body) - 2], body[len(body) - 1]) == item[1]:
                                body[len(body) - 2] = item[0]
                                body[len(body) - 1] = " "
                
                    while " " in body:
                            body.remove(" ")
                    body = ' '.join(body)
            
                new_bodies.add(body)
            
            if len(new_bodies) > 0:
                nuevaGram.append(head + ' → ' + ' | '.join(new_bodies)
    )
    return nuevaGram

# Transforms the grammar to Chomsky Normal Form (CNF).
def cnf(gram_argument):
    nuevaGram = cnfA(gram_argument)
    nuevaGram = cnfB(nuevaGram)
    
    return nuevaGram

# Node class for building parse trees.
class Node:
    def __init__(self, symbol, children=[]):
        self.symbol = symbol
        self.children = children

    def __repr__(self):
        return self.symbol

# Visualizes the parse tree using Graphviz.
def visualize_tree(node):
    dot = Digraph(comment='Parse Tree')
    build_graph(dot, node)
    dot.view(filename='Parse Tree', cleanup=True)

# Builds the graph with recursion.
def build_graph(dot, node, parent_name=None):
    name = node.symbol + str(id(node))
    dot.node(name, node.symbol)
    if parent_name:
        dot.edge(parent_name, name)
    for child in node.children:
        build_graph(dot, child, name)

# Prints the tree with recursion.
def print_tree(node, indent=0):
    print(' ' * indent + node.symbol)
    for child in node.children:
        print_tree(child, indent + 2)

# Converts the grammar array to a dictionary.
def convert_to_grammar(rules_list):
    grammar = {}
    for rule in rules_list:
        left, right = rule.split("→")
        left = left.strip()
        productions = [prod.strip().split() for prod in right.split("|")]
        if left not in grammar:
            grammar[left] = []
        grammar[left].extend(productions)
    return grammar
