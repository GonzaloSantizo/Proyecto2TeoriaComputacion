# Import necessary libraries
import re
import itertools
from pprint import pprint
import copy
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

# AUXILIARY FUNCTIONS SECTION

# Function to read a grammar file
def read_file(file_name: str) -> (list[str] | None):
    # Try to open and read the file
    try:
        file = open(file_name, 'r', encoding='utf-8')
        data = file.read()
        file.close()
        return data.split('\n')
    except:
        print("Error reading the file")
        return None

# Function to evaluate a regular expression in a string
def evaluate_expression(regex: str, expression: str) -> bool:
    if re.match(regex, expression):
        return True
    else:
        return False

# Function to identify terminal and non-terminal symbols in the grammar
def identify_terms(grammar: dict) -> (set, set):
    non_terminals: set = set(grammar.keys())
    terminals: set = set()

    for productions in grammar.values():
        for production in productions:
            for term in production.split(" "):
                if term not in non_terminals:
                    terminals.add(term)

    return non_terminals, terminals

# Function to build the power set of a set
def build_power_set(s: set) -> list[str]:
    power_set = []
    for i in range(len(s) + 1):
        power_set.extend(itertools.combinations(s, i))
    return power_set

# Function to check if a symbol is terminal
def is_terminal(term: str) -> bool:
    if re.fullmatch("([a-z]|[0-9]|\s)*", term):
        return True
    else:
        return False 

# SIMPLIFICATION SECTION OF GRAMMARS FOR CHOMSKY NORMAL FORM

# Function to remove epsilon productions
def remove_epsilon_productions(grammar: dict) -> dict:
    nullable = set()

    for i in grammar:
        if 'ε' in grammar[i]:
            nullable.add(i)

    changed = True
    while changed:
        changed = False
        temp_set = set()
        for i in grammar:
            for j in nullable:
                if (j in grammar[i]) and (i not in nullable):
                    temp_set.add(i)
                    changed = True
        
        nullable = nullable.union(temp_set)
    
    # Remove epsilon production
    for i in grammar:
        if 'ε' in grammar[i]:
            grammar[i].remove('ε')

    power_set = build_power_set(nullable)

    new_grammar = {}

    for i in grammar:
        new_grammar[i] = []
        for j in grammar[i]:
            new_grammar[i].append(j)

        for j in grammar[i]:
            for k in power_set:
                new_production = j
                for l in k:
                    new_production = new_production.replace(l, '')
                if new_production != '' and (new_production not in new_grammar[i]):
                    new_grammar[i].append(new_production)

    
    grammar = new_grammar
    new_grammar = copy.deepcopy(grammar)

    for i in grammar:
        for j in grammar[i]:
            if j == ' ':
                new_grammar[i].remove(j)
            elif is_terminal(j):
                temp = j
                temp = temp.replace(' ', '')
                new_grammar[i].append(temp)
                new_grammar[i].remove(j)

    return new_grammar

# Function to remove unit productions
def remove_unit_productions(grammar: dict) -> dict: 
    new_grammar = {}
    for i in grammar:
        new_grammar[i] = []
        for j in grammar[i]:
            new_grammar[i].append(j)

    changed = True
    while changed:
        changed = False
        for i in new_grammar:
            for j in new_grammar[i]:
                if len(j) == 1 and j.isupper():
                    for k in new_grammar[j]:
                        if k not in new_grammar[i]:
                            new_grammar[i].append(k)
                    new_grammar[i].remove(j)
                    changed = True

    return new_grammar 

# Function to remove non-derivable symbols
def remove_non_derivable_symbols(grammar: dict) -> dict:
    non_terminals, terminals = identify_terms(grammar)
    derivable = set()

    for i in grammar:
        for j in grammar[i]:
            if j in terminals:
                derivable.add(i)

    changed = True
    while changed:
        changed = False
        for i in grammar:
            for j in grammar[i]:
                for k in j.split(" "):
                    if k in derivable and i not in derivable:
                        derivable.add(i)
                        changed = True

    new_grammar = {}

    for i in derivable:
        new_grammar[i] = []
        for j in grammar[i]:
            new_grammar[i].append(j)
    
    return new_grammar

# Function to remove unreachable productions
def remove_unreachable_productions(grammar: dict) -> dict:
    reachable = set("S")
    new_grammar = {}

    non_terminals: set = set(grammar.keys())
    terminals: set = set()

    for productions in grammar.values():
        for production in productions:
            for term in production.split(" "):
                if term not in non_terminals:
                    terminals.add(term)

    changed = True
    while changed:
        changed = False
        temp_set = set()
        for i in reachable:
            for j in grammar[i]:
                jsplit = j.split(" ")
                for k in jsplit:
                    if k in non_terminals and k not in reachable:
                        temp_set.add(k)
                        changed = True

        reachable = reachable.union(temp_set)
    
    for i in reachable:
        new_grammar[i] = []
        for j in grammar[i]:
            new_grammar[i].append(j)
    for i in grammar:
        for j in grammar[i]:
            for k in j.split(" "):
                if k not in non_terminals and k not in terminals:
                    new_grammar[i].remove(j)
                    break

    return new_grammar

# Function to convert a grammar to Chomsky Normal Form
def convert_to_chomsky(grammar: dict) -> dict:
    # Simplify the grammar
    grammar = remove_epsilon_productions(grammar)
    grammar = remove_unit_productions(grammar)
    grammar = remove_non_derivable_symbols(grammar)
    grammar = remove_unreachable_productions(grammar)
    # Convert to Chomsky Normal Form
    changed = True
    nt = 0
    while changed:
        changed = False
        new_grammar = copy.deepcopy(grammar)
        for i in grammar:
            for j in grammar[i]:
                jsplit = j.split(" ")
                if len(jsplit) > 2:
                    splitted_and_separated = jsplit[1:]
                    joined = " ".join(splitted_and_separated)

                    if [joined] in list(new_grammar.values()):
                        for k in new_grammar:
                            if new_grammar[k] == [joined]:
                                new_grammar[i].append(jsplit[0] + " " + f"{k}")
                                new_grammar[i].remove(j)
                    else:
                        new_grammar[f"NT{nt}"] = [joined]
                        new_grammar[i].append(jsplit[0] + " " + f"NT{nt}")
                        new_grammar[i].remove(j)
                        nt += 1
                        changed = True
        grammar = new_grammar

    new_grammar = {}
    for i in grammar:
        new_grammar[i] = []
        for j in grammar[i]:
            new_grammar[i].append(j.split(" "))

    grammar = new_grammar

    return grammar

# CYK ALGORITHM IMPLEMENTATION SECTION

# Function to perform CYK syntactic analysis
def cyk_parse(grammar: dict, word: str) -> (bool,list|None):
    n = len(word)
    # Initialize the table
    T = [[set([]) for j in range(n)] for i in range(n)]
 
    # Fill the table
    for j in range(0, n):
        # Iterate over the grammar rules
        for lhs, rule in grammar.items():
            for rhs in rule:
                # If a terminal is found
                if len(rhs) == 1 and rhs[0] == word[j]:
                    T[j][j].add(lhs)
 
        for i in range(j, -1, -1):   
            # Iterate over the range i to j + 1   
            for k in range(i, j):     
                # Iterate over the grammar rules
                for lhs, rule in grammar.items():
                    for rhs in rule:
                        # If a terminal is found
                        if (len(rhs) == 2) and (rhs[0] in T[i][k]) and (rhs[1] in T[k+1][j]):
                            T[i][j].add(lhs)
    if len(T[0][n-1]) != 0:
        return True, T
    else:
        return False, None

# PARSE TREE VISUALIZATION SECTION

# Function to generate and visualize the parse tree
def generate_and_visualize_tree(grammar: dict, table: list, sentence: list) -> None:
    class Node:
        def __init__(self, symbol):
            self.symbol = symbol
            self.children = []

        def add_child(self, child):
            self.children.append(child)

        def get_children(self):
            return self.children
        
    def generate_tree(table, grammar, i, j, symbol):
        if i == j:
            for rule, productions in grammar.items():
                for production in productions:
                    if len(production) == 1 and symbol in production:
                        return Node(symbol)
        
        for k in range(i, j):
            for rule, productions in grammar.items():
                for production in productions:
                    if symbol == rule and len(production) == 2:
                        left, right = production
                        if left in table[i][k] and right in table[k+1][j]:
                            node = Node(symbol)
                            node.add_child(generate_tree(table, grammar, i, k, left))
                            node.add_child(generate_tree(table, grammar, k+1, j, right))
                            return node

        node = Node(symbol)

        if len(node.get_children()) == 0:
            outputs = grammar[symbol]
            terminals = []

            for term in outputs:
                if len(term) == 1:
                    terminals.append(term[0])

            for word in sentence:
                if word in terminals:
                    node.add_child(Node(word))
                    sentence.remove(word)
                    break

        return node
    
    def visualize(tree):
        G = nx.DiGraph()
        labels = {}

        def add_node_edges(tree, G, parent=None, counter=0):
            node = f"{tree.symbol}{counter}"
            G.add_node(node)
            labels[node] = tree.symbol
            if parent is not None:
                G.add_edge(parent, node)
            counter += 1
            for child in tree.children:
                counter = add_node_edges(child, G, node, counter)
            return counter

        add_node_edges(tree, G)
        pos = nx.graph
        pos = graphviz_layout(G, "dot")
        plt.figure(figsize=(10, 6))
        nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color="skyblue", font_size=15)
        plt.title("Parse Tree")
        plt.show()
    
    parse_tree = generate_tree(table, grammar, 0, len(table) - 1, 'S')
    visualize(parse_tree)

# MAIN

if __name__ == '__main__':
    regex = "[A-z]+->(([A-Za-z0-9]|\s)*(\|)*)+|ε"
    data = read_file(f'./1.txt')
    for expression in data:
        if expression != '':
            if not evaluate_expression(regex=regex, expression=expression):
                print(f'Production {expression} does not comply, so the grammar is not accepted')
                exit(0)

    grammar: dict = {}

    for expression in data:
        expression_split1 = expression.split('->')
        expression_split2 = expression_split1[1].split('|')
        if expression_split1[0] not in grammar:
            grammar[expression_split1[0]] = expression_split2
        else:
            grammar[expression_split1[0]].extend(expression_split2)

    grammar: dict = convert_to_chomsky(grammar) 

    sentence: list = input("Enter the sentence you want to verify: ").split()
    accept, table = cyk_parse(grammar, sentence)

    if accept:
        print("The sentence IS accepted")
        generate_and_visualize_tree(grammar, table, sentence)
    else:
        print("The sentence IS NOT accepted")
