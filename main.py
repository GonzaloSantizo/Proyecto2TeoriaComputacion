
from proyecto2 import *
from cyk import *

# Execution
pattern = r"([A-Z]+)\s*→\s*(\w|\s)+"
gram_argument = []
denegade = False
initialSymbol = ""

with open("gramatica.txt", 'r') as file:
    print("\n--------------------------------------------------------------")
    print("ORIGINAL GRAMMAR: ")
    lineas = file.readlines()
    for i, linea in enumerate(lineas):
        linea = linea.strip()
        linea = linea.replace("â†’", "→")
        linea = linea.replace("Îµ", "ε")
            
        respuesta = prod_valid(pattern, linea)
            
        if respuesta:
            gram_argument.append(linea)
            if i == 0:
                initialSymbol = linea.split(' → ')[0]
            print(linea)
        else:
            print("\nERROR! Line: " + linea + " in gram_argument.txt is incorrect.")
            denegade = True
            break
        
if denegade is False:
    nuevagram_argument = eliminate_prod_epsilon(gram_argument)
    print("\n--------------------------------------------------------------")
    print("GRAMMAR WITHOUT ε PRODUCTIONS: ")
    for item in nuevagram_argument:
        print(item)
    
    nuevagram_argument = eliminate_unary(nuevagram_argument)
    print("\n--------------------------------------------------------------")
    print("GRAMMAR WITHOUT UNIT PRODUCTIONS: ")
    for item in nuevagram_argument:
        print(item)

    nuevagram_argument = eliminarSimbolosInutiles(nuevagram_argument, initialSymbol)
    print("\n--------------------------------------------------------------")
    print("GRAMMAR WITHOUT UNUSED SYMBOLS: ")
    for item in nuevagram_argument:
        print(item)
    
    nuevagram_argument = cnf(nuevagram_argument)
    print("\n--------------------------------------------------------------")
    print("GRAMMAR IN CNF: ")
    for item in nuevagram_argument:
        print(item)
        
    grammar = convert_to_grammar(nuevagram_argument)
    
    # Input of the string
    W = input("\nEnter the string 𝑤. Separate non-terminals with whitespace.\n>> ")
    start_time = time.time()
    parse_tree = cyk(grammar, W.split(), initialSymbol)
    if parse_tree:
        print("\nThe expression 𝑤 DOES belong to the language described by the grammar.")
        visualize_tree(parse_tree)
    else:
        print("The expression 𝑤 DOES NOT belong to the language described by the grammar.")
    end_time = time.time()
    duration = end_time - start_time
    print(f"The algorithm took {duration:.4f} seconds to perform the validation.")
