import graphviz

def create_initial_flow_network():
    """Create the initial flow network from the first slide."""
    g = graphviz.Digraph('G', filename='flow_network_initial.png', format='png')
    g.attr(rankdir='LR')
    g.attr('node', shape='circle')
    
    # Add nodes
    g.node('s')
    g.node('t')
    
    # Add intermediate nodes
    g.node('n1', label='')
    g.node('n2', label='')
    g.node('n3', label='')
    g.node('n4', label='')
    
    # Add edges with flow/capacity labels
    g.edge('s', 'n1', label='0/10')
    g.edge('s', 'n2', label='0/10')
    g.edge('n1', 'n3', label='0/4')
    g.edge('n1', 'n2', label='0/2')
    g.edge('n1', 'n4', label='0/8')
    g.edge('n2', 'n4', label='0/9')
    g.edge('n3', 'n4', label='0/6')
    g.edge('n3', 't', label='0/10')
    g.edge('n4', 't', label='0/10')
    
    # Add flow value label
    g.node('flow_value', shape='none', label='0', pos='0,2!')
    g.node('flow_label', shape='none', label='flow', pos='1.5,2.5!')
    g.node('capacity_label', shape='none', label='capacity', pos='2.5,2.5!')
    g.node('value_label', shape='none', label='value of flow', pos='0,2.5!')
    
    g.render(cleanup=True)
    return g

def create_greedy_failure_example():
    """Create the example showing why greedy algorithm fails."""
    g = graphviz.Digraph('G', filename='flow_network_failure_example.png', format='png')
    g.attr(rankdir='LR')
    g.attr('node', shape='circle')
    
    # Add nodes
    g.node('s')
    g.node('v')
    g.node('w')
    g.node('t')
    
    # Add edges with capacity labels
    g.edge('s', 'v', label='2')
    g.edge('s', 'w', label='2')
    g.edge('v', 't', label='2')
    g.edge('v', 'w', label='1')
    g.edge('w', 't', label='2')
    
    g.render(cleanup=True)
    return g

def create_residual_network_example():
    """Create the residual network example."""
    # Original network
    g1 = graphviz.Digraph('G', filename='original_flow_network.png', format='png')
    g1.attr(rankdir='LR')
    g1.attr('node', shape='circle')
    
    g1.node('u')
    g1.node('v')
    
    g1.edge('u', 'v', label='6/17')
    
    # Add labels
    g1.node('original_label', shape='none', label='original flow network G', pos='0,2!')
    g1.node('flow_label', shape='none', label='flow', pos='0.5,1.5!')
    g1.node('capacity_label', shape='none', label='capacity', pos='0.5,2.0!')
    
    g1.render(cleanup=True)
    
    # Residual network
    g2 = graphviz.Digraph('Gf', filename='residual_network_example.png', format='png')
    g2.attr(rankdir='LR')
    g2.attr('node', shape='circle')
    
    g2.node('u')
    g2.node('v')
    
    g2.edge('u', 'v', label='11')
    g2.edge('v', 'u', label='6')
    
    # Add labels
    g2.node('residual_label', shape='none', label='residual network Gf', pos='0,2!')
    g2.node('residual_capacity_label', shape='none', label='residual\ncapacity', pos='0.5,1.5!')
    g2.node('reverse_edge_label', shape='none', label='reverse edge', pos='0.5,1.0!')
    
    g2.render(cleanup=True)
    return g1, g2

def create_network_flow_quiz():
    """Create the network flow quiz diagram."""
    g = graphviz.Digraph('G', filename='network_flow_quiz.png', format='png')
    g.attr('node', shape='circle')
    
    # Add nodes
    g.node('A')
    g.node('B')
    g.node('C')
    g.node('D')
    g.node('E')
    g.node('F')
    g.node('G')
    g.node('H')
    
    # Add edges with capacity labels
    g.edge('B', 'A', label='9')
    g.edge('C', 'B', label='8')
    g.edge('A', 'E', label='5')
    g.edge('A', 'F', label='7')
    g.edge('B', 'F', label='8')
    g.edge('C', 'D', label='6')
    g.edge('C', 'G', label='4')
    g.edge('D', 'H', label='8')
    g.edge('D', 'G', label='6')
    g.edge('F', 'E', label='5')
    g.edge('F', 'G', label='2')
    g.edge('G', 'H', label='3')
    g.edge('G', 'C', label='5')
    g.edge('H', 'D', label='5')
    
    # Add annotations
    g.node('source_label', shape='none', label='source', pos='0,2.5!')
    g.node('target_label', shape='none', label='target', pos='4.0,2.5!')
    g.node('residual_capacity_label', shape='none', label='residual capacity', pos='2.0,2.5!')
    
    g.render(cleanup=True)
    return g

def create_flow_cut_relationship():
    """Create the flow and cut relationship diagram."""
    g = graphviz.Digraph('G', filename='flow_cut_relationship.png', format='png')
    g.attr(rankdir='LR')
    
    # Add nodes with gray fill
    g.node('s', shape='circle')
    g.node('t', shape='circle', style='filled', fillcolor='lightgray')
    g.node('n1', shape='circle', style='filled', fillcolor='lightgray')
    g.node('n2', shape='circle', style='filled', fillcolor='lightgray')
    g.node('n3', shape='circle', style='filled', fillcolor='lightgray')
    g.node('n4', shape='circle', style='filled', fillcolor='lightgray')
    g.node('n5', shape='circle', style='filled', fillcolor='lightgray')
    g.node('n6', shape='circle', style='filled', fillcolor='lightgray')
    
    # Add regular edges
    g.edge('s', 'n1', label='10/10')
    g.edge('s', 'n4', label='5/5')
    g.edge('s', 'n6', label='10/15')
    g.edge('n1', 'n2', label='5/9')
    g.edge('n1', 'n3', label='5/15')
    g.edge('n2', 'n3', label='0/15')
    g.edge('n3', 'n5', label='5/8')
    g.edge('n4', 'n3', label='0/4')
    g.edge('n4', 'n5', label='0/4')
    g.edge('n5', 'n2', label='0/6')
    g.edge('n6', 'n5', label='10/16')
    
    # Add cut edges (thicker)
    g.edge('n2', 't', label='5/10', penwidth='3.0')
    g.edge('n5', 't', label='10/10', penwidth='3.0')
    
    # Add annotations
    g.node('flow_value_label', shape='none', label='value of flow = 25', pos='0,2.5!')
    g.node('net_flow_label', shape='none', label='net flow across cut = 5 + 10 + 10 = 25', pos='0,2.0!')
    
    g.render(cleanup=True)
    return g

if __name__ == "__main__":
    create_initial_flow_network()
    create_greedy_failure_example()
    create_residual_network_example()
    create_network_flow_quiz()
    create_flow_cut_relationship()
    
    print("All graph images have been generated successfully!")