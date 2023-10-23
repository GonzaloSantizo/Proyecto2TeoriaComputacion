
# CYK algorithm, returns the parse tree.
def cyk(grammar, W, simboloInicial):

    n = len(W)
    P = {}
    
    # Initialize P with non-terminals that produce terminals.
    # Implementation of the base condition of dynamic programming.
    # Direct derivations are identified.
    for i in range(n):
        P[(i, i + 1)] = []
        for A, productions in grammar.items():
            for prod in productions:
                if len(prod) == 1 and prod[0] == W[i]:
                    P[(i, i + 1)].append(Node(A, [Node(prod[0])]))
    
    # Dynamic programming: fill matrix P iteratively.
    # For each substring of the word, find all possible derivations.
    for span in range(2, n + 1):
        for start in range(n - span + 1):
            end = start + span
            P[(start, end)] = []
            # Consider all possible bipartitions of the substring.
            for split in range(start + 1, end):
                # Check if each production rule can be applied.
                for A, productions in grammar.items():
                    for prod in productions:
                        if len(prod) == 2:
                            B, C = prod
                            # Check the already stored solutions for substrings [start, split] and [split, end].
                            # If matches are found, build a derivation and add it to our P matrix.
                            for b_node in P[(start, split)]:
                                if b_node.symbol == B:
                                    for c_node in P[(split, end)]:
                                        if c_node.symbol == C:
                                            P[(start, end)].append(Node(A, [b_node, c_node]))
    
    # Return the parse tree if one exists for the entire word.
    for node in P[(0, n)]:
        if node.symbol == simboloInicial:
            return node
    return None
