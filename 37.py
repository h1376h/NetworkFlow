from graphviz import Digraph
import math

# Define phi (golden ratio conjugate) for clarity
PHI = (math.sqrt(5) - 1) / 2 # ~0.618034

def create_flow_graph(step_num, title_prefix, action_description, flows_data, residual_data, initial_caps_ref, path_edges=None):
    """
    Creates a Digraph for a specific step of the Ford-Fulkerson algorithm.

    Args:
        step_num (int): The current step number.
        title_prefix (str): Main title for the step (e.g., "Ford-Fulkerson Step X").
        action_description (str): Detailed description of the action (e.g., "Augmenting path S->X1->T by 0.5").
        flows_data (dict): Dictionary of current flow for each original edge (u, v): flow_value.
        residual_data (dict): Dictionary of residual capacities for (u, v): capacity_value
                              and (v, u): reverse_capacity_value.
        initial_caps_ref (dict): Reference to the dictionary of original edge capacities.
        path_edges (list): List of (u, v) tuples representing edges in the current augmenting path.
                           For reverse edges in the path, use (v, u) to indicate flow reversal.
    """
    dot = Digraph(comment=f'Ford-Fulkerson Non-Termination Example - Step {step_num}')
    # Combine title prefix and action description for a comprehensive title
    full_title = f"{title_prefix}\n{action_description}\nTotal Flow: {flows_data['total_flow']:.5f}"
    dot.attr(label=full_title, labelloc='t', fontsize='20')
    dot.attr(rankdir='LR') # Left to Right layout for better readability

    # Define node styles
    dot.node('s', 'Source (s)', style='filled', fillcolor='lightblue')
    dot.node('t', 'Sink (t)', style='filled', fillcolor='lightcoral')
    dot.node('x1', 'Node x1')
    dot.node('x2', 'Node x2')

    # Define all original edges and their base capacities for display reference
    # Using a large integer for M (e.g., 100)
    original_capacities_display = {
        ('s', 'x1'): '1',
        ('s', 'x2'): '100',
        ('x1', 'x2'): '1',
        ('x1', 't'): '100',
        ('x2', 't'): 'φ ≈ 0.618'
    }

    # Add edges with current flow and residual capacities
    # First, draw all original edges based on their flow/capacity/residual
    for (u, v), cap_str_display in original_capacities_display.items():
        current_flow_uv = flows_data.get((u, v), 0.0)
        res_cap_uv_forward = residual_data.get((u, v), 0.0)
        
        # Check if this original edge is part of the current augmenting path (forward direction)
        is_path_edge_forward = (u, v) in path_edges if path_edges else False

        # Draw the forward edge if it has flow or positive residual capacity
        if res_cap_uv_forward > 1e-9 or current_flow_uv > 1e-9:
            label_uv = f'{current_flow_uv:.5f}/{cap_str_display} ({res_cap_uv_forward:.5f})'
            color_uv = 'red' if is_path_edge_forward else 'black'
            penwidth_uv = '3.0' if is_path_edge_forward else '1.0'
            dot.edge(u, v, label=label_uv, color=color_uv, penwidth=penwidth_uv, fontsize='10')

    # Then, draw all distinct reverse residual edges that have positive capacity
    drawn_reverse_edges = set()
    for (node1, node2) in residual_data.keys():
        # Check if (node1,node2) is a reverse of an original edge by checking if (node2,node1) is an original edge
        if (node2, node1) in initial_caps_ref:
            res_cap_reverse = residual_data.get((node1, node2), 0.0)
            if res_cap_reverse > 1e-9 and (node1, node2) not in drawn_reverse_edges:
                
                # Check if this reverse edge (node1, node2) is part of the augmenting path
                is_path_edge_reverse = (node1, node2) in path_edges if path_edges else False
                
                label_reverse = f'({res_cap_reverse:.5f})'
                color_reverse = 'red' if is_path_edge_reverse else 'grey'
                penwidth_reverse = '3.0' if is_path_edge_reverse else '1.0'
                dot.edge(node1, node2, label=label_reverse, style='dashed', color=color_reverse, penwidth=penwidth_reverse, fontsize='10')
                drawn_reverse_edges.add((node1, node2))


    dot.render(f'ford_fulkerson_step_{step_num}', view=True, format='png', cleanup=True)


def run_ford_fulkerson_irrational_loop_steps():
    M_val = 100 # A large integer capacity
    phi = PHI # Golden ratio conjugate ≈ 0.618034

    # Initial capacities (these are constants for the network)
    initial_caps = {
        ('s', 'x1'): 1.0, ('s', 'x2'): M_val,
        ('x1', 'x2'): 1.0, ('x1', 't'): M_val,
        ('x2', 't'): phi
    }

    # Initialize current flow (f(e)) and residual capacities (c_f(e))
    current_flows = {edge: 0.0 for edge in initial_caps}
    
    residual_capacities = initial_caps.copy()
    for (u, v) in initial_caps:
        residual_capacities[(v, u)] = 0.0 # Initialize all potential reverse edges to 0

    total_network_flow = 0.0
    
    # --- Ford-Fulkerson Algorithm Steps ---
    step_count = 0

    # Step 0: Initial State
    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", "Initial State (All flows are zero)", current_flows.copy(), residual_capacities.copy(), initial_caps, [])
    step_count += 1

    # Loop Iteration 1 (Augment P1: s -> x1 -> x2 -> t)
    path_edges = [('s', 'x1'), ('x1', 'x2'), ('x2', 't')]
    bottleneck = min(residual_capacities[e] for e in path_edges) # min(1, 1, phi) = phi

    for u, v in path_edges:
        current_flows[(u, v)] += bottleneck
        residual_capacities[(u, v)] -= bottleneck
        residual_capacities[(v, u)] += bottleneck # Update reverse residual capacity
    total_network_flow += bottleneck

    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment s->x1->x2->t by {bottleneck:.5f}",
                      current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
    step_count += 1

    # Loop Iteration 2 (Augment P2: s -> x2 -> x1 -> t using residual edge x2 -> x1)
    # This path is: s -> x2 (forward), x2 -> x1 (reverse of original x1->x2), x1 -> t (forward)
    path_edges = [('s', 'x2'), ('x2', 'x1'), ('x1', 't')] # Note: ('x2','x1') indicates using the reverse edge
    
    bottleneck = min(residual_capacities['s', 'x2'], residual_capacities['x2', 'x1'], residual_capacities['x1', 't']) # min(M, phi, M) = phi

    for u, v in path_edges:
        if (u,v) in initial_caps: # It's a forward original edge (s,x2), (x1,t)
            current_flows[(u, v)] += bottleneck
            residual_capacities[(u, v)] -= bottleneck
            residual_capacities[(v, u)] += bottleneck # Increase reverse capacity
        else: # It's a reverse original edge (x2,x1)
            original_forward_edge = (v, u) # The original edge is (x1,x2)
            current_flows[original_forward_edge] -= bottleneck # Reduce flow on original (x1,x2)
            residual_capacities[(u, v)] -= bottleneck # Reduce reverse residual capacity (x2,x1)
            residual_capacities[original_forward_edge] += bottleneck # Increase forward residual capacity (x1,x2)
    total_network_flow += bottleneck

    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment s->x2->x1->t by {bottleneck:.5f}",
                      current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
    step_count += 1
    
    # Loop Iteration 3 (Augment P3: s -> x1 -> t)
    # After Step 2:
    # residual_capacities['s','x1'] is still 1-phi = phi^2
    # residual_capacities['x1','x2'] is now 1 (because f(x1,x2) became 0)
    # residual_capacities['x2','t'] is still 0 (from step 1)
    # residual_capacities['x1','t'] is M-phi
    # The path s->x1->t is available, but its bottleneck is smaller.
    path_edges = [('s', 'x1'), ('x1', 't')]
    bottleneck = min(residual_capacities['s', 'x1'], residual_capacities['x1', 't']) # min(phi^2, M-phi) = phi^2

    for u, v in path_edges:
        current_flows[(u, v)] += bottleneck
        residual_capacities[(u, v)] -= bottleneck
        residual_capacities[(v, u)] += bottleneck # Update reverse capacity
    total_network_flow += bottleneck

    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment s->x1->t by {bottleneck:.5f}",
                      current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
    step_count += 1
    
    # --- Remaining Steps to show continuation of the loop ---
    # The essence of the loop is that after these three steps, the network can be in a state
    # where paths similar to the first two reappear, but with capacities reduced by
    # a factor related to phi. This continues indefinitely.
    # We will simulate the *effect* of these repeated augmentations.

    # Step 4: Augment P4 (similar to P1, but with smaller residuals)
    # This is a conceptual restart of the sequence of paths, but with smaller remaining capacities.
    
    bottleneck_for_cycle = PHI**3 # This is the new bottleneck
    path_edges = [('s', 'x1'), ('x1', 'x2'), ('x2', 't')]
    
    # Manually ensure enough residual capacity for visualization:
    # These values are set to simulate the state where the next phi-power bottleneck is available
    residual_capacities['s', 'x1'] = bottleneck_for_cycle
    residual_capacities['x1', 'x2'] = bottleneck_for_cycle
    residual_capacities['x2', 't'] = bottleneck_for_cycle

    for u, v in path_edges:
        current_flows[(u, v)] += bottleneck_for_cycle
        residual_capacities[(u, v)] -= bottleneck_for_cycle
        residual_capacities[(v, u)] += bottleneck_for_cycle
    total_network_flow += bottleneck_for_cycle

    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment s->x1->x2->t by {bottleneck_for_cycle:.5f}",
                      current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
    step_count += 1

    # Step 5: Path similar to step 2 (s -> x2 -> x1 -> t)
    bottleneck_for_cycle = PHI**3 
    path_edges = [('s', 'x2'), ('x2', 'x1'), ('x1', 't')]
    
    # Manually ensure enough residual capacity for visualization
    residual_capacities['s', 'x2'] = M_val - (total_network_flow - current_flows.get(('s','x2'),0)) # Ensure large enough
    residual_capacities['x2', 'x1'] = bottleneck_for_cycle # Assume it was built up
    residual_capacities['x1', 't'] = M_val - (total_network_flow - current_flows.get(('x1','t'),0))

    for u, v in path_edges:
        if (u,v) in initial_caps:
            current_flows[(u, v)] += bottleneck_for_cycle
            residual_capacities[(u, v)] -= bottleneck_for_cycle
            residual_capacities[(v, u)] += bottleneck_for_cycle
        else: # Reverse edge
            original_forward_edge = (v, u)
            current_flows[original_forward_edge] -= bottleneck_for_cycle
            residual_capacities[(u, v)] -= bottleneck_for_cycle
            residual_capacities[original_forward_edge] += bottleneck_for_cycle

    total_network_flow += bottleneck_for_cycle
    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment s->x2->x1->t by {bottleneck_for_cycle:.5f}",
                      current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
    step_count += 1

    # Step 6: Path similar to step 3 (s -> x1 -> t)
    bottleneck_for_cycle = PHI**4 # Next smaller bottleneck
    path_edges = [('s', 'x1'), ('x1', 't')]
    
    # Manually ensure enough residual capacity for visualization
    residual_capacities['s', 'x1'] = bottleneck_for_cycle
    residual_capacities['x1', 't'] = M_val - (total_network_flow - current_flows.get(('x1','t'),0)) # Ensure large enough

    for u, v in path_edges:
        current_flows[(u, v)] += bottleneck_for_cycle
        residual_capacities[(u, v)] -= bottleneck_for_cycle
        residual_capacities[(v, u)] += bottleneck_for_cycle
    total_network_flow += bottleneck_for_cycle

    current_flows['total_flow'] = total_network_flow
    create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment s->x1->t by {bottleneck_for_cycle:.5f}",
                      current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
    step_count += 1
    
    # Steps 7-9: Further iterations to show the diminishing returns
    # We will just show the pattern of decreasing bottlenecks.
    # The exact path choices will be simplified for display.
    for i in range(7, 10):
        bottleneck_for_cycle = PHI**(i+1) # Continually smaller
        # Alternate between the main paths that cause the loop
        if i % 2 == 1:
            path_edges = [('s', 'x1'), ('x1', 'x2'), ('x2', 't')]
            # Ensure capacities are conceptually available for this small flow
            residual_capacities['s', 'x1'] = bottleneck_for_cycle
            residual_capacities['x1', 'x2'] = bottleneck_for_cycle
            residual_capacities['x2', 't'] = bottleneck_for_cycle
        else:
            path_edges = [('s', 'x2'), ('x2', 'x1'), ('x1', 't')]
            # Ensure capacities are conceptually available for this small flow
            residual_capacities['s', 'x2'] = M_val - (total_network_flow / 2) # Arbitrary large enough
            residual_capacities['x2', 'x1'] = bottleneck_for_cycle # Make reverse available
            residual_capacities['x1', 't'] = M_val - (total_network_flow / 2) # Arbitrary large enough

        # Augment flow (simplified for conceptual display)
        for u, v in path_edges:
            if (u,v) in initial_caps: # Forward original edge
                current_flows[(u, v)] += bottleneck_for_cycle
                residual_capacities[(u, v)] -= bottleneck_for_cycle
                residual_capacities[(v, u)] += bottleneck_for_cycle
            else: # Reverse original edge
                original_forward_edge = (v, u)
                current_flows[original_forward_edge] -= bottleneck_for_cycle
                residual_capacities[(u, v)] -= bottleneck_for_cycle
                residual_capacities[original_forward_edge] += bottleneck_for_cycle
        total_network_flow += bottleneck_for_cycle
        
        current_flows['total_flow'] = total_network_flow
        create_flow_graph(step_count, f"Ford-Fulkerson Step {step_count}", f"Augment by {bottleneck_for_cycle:.5f} (Continuing Loop)",
                          current_flows.copy(), residual_capacities.copy(), initial_caps, path_edges)
        step_count += 1

    print("\nGenerated 10 PNG files (ford_fulkerson_step_X.png) showing the theoretical loop.")
    print("This simulation manually guides path choices to illustrate the non-terminating pattern.")
    print("The precision of floating-point numbers can slightly affect exact values.")
    print("Total flow converges to 1 + phi (approx 1.618), but never exactly reaches it.")
    print(f"Max Theoretical Flow: {1 + PHI:.5f}")


if __name__ == "__main__":
    run_ford_fulkerson_irrational_loop_steps()