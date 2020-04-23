from copy import deepcopy


def find_circular_movements(ms):
    circular_movements = []
    moves = [m for m in ms]
    while moves:
        node_a = moves[0]
        # look at the target of the first move
        moves = [m for m in moves if m != node_a]
        if node_a.target.piece:
            node_b = node_a.target.piece.order
            moves = [m for m in moves if m != node_b]
            # This would be a head to head.
            if node_b.is_move and node_b.target != node_a.source:
                # go
                next_node = node_b.target.piece.order
                found_original_node = False
                nodes = [node_a, node_b]
                while not found_original_node:
                    nodes.append(next_node)
                    moves = [m for m in moves if m != next_node]
                    if next_node.is_move:
                        if next_node.target == node_a.source:
                            found_original_node = True
                            circular_movements.append(nodes)
                        else:
                            next_node = next_node.target.piece.order
    return circular_movements


