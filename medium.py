Edges = [
  [1, 2, 25],
  [1, 3, 30],
  [1, 4, 20],
  [3, 4, 30],
  [2, 5, 25],
  [3, 5, 35],
  [4, 6, 30],
  [5, 7, 40],
  [4, 8, 40],
  [6, 8, 35],
  [6, 9, 30],
  [7, 10, 20],
  [8, 10, 20],
  [9, 10, 20]
]

# each edge is represented as [to, from, capacity]

def construct_level_graph(source, sink, edges):
    visited = [source]
    nodes_in_curr_level = [source]
    nodes_in_next_level = []

    # set all edge is_part_of_level_graph values to False
    # to ensure that a new level graph is created everytime the 
    # function is called
    for edge in edges: 
        edge[4] = False 

    while True:  
        # add an edge to the level graph if:
          # remaining capacity is greater than 0
          # "to" value is in the list of nodes in the current level
          # "from" value has not been visited yet (on a new level)
        for edge in edges:
            if edge[0] in nodes_in_curr_level and edge[1] not in visited and edge[3] - edge[2] > 0:
                nodes_in_next_level.append(edge[1])
                edge[4] = True
                visited.append(edge[1])

        # if there are no new edges in the next level,
        # then the depth of the search can no longer expand,
        # so we terminate
        if not nodes_in_next_level:
            break
                 
        nodes_in_curr_level = nodes_in_next_level
        nodes_in_next_level = []

    if sink in visited:
        return edges 
    return False

def dfs(source, sink, edges):
    global levels
    visited = [source]
    path = [source]
    path_indices = []

    # run the search while it is currently checking a path or 
    # until the sink is reached
    while path and path[-1] != sink:
        for idx, edge in enumerate(edges):
            if edge[0] == path[-1] and edge[1] not in visited and edge[3] - edge[2] > 0 and edge[4]:
                visited.append(edge[1])
                path.append(edge[1])
                path_indices.append(idx)
                break

        else:
            path.pop() # backtracking / will keep on popping until there are no more paths
            try:
                path_indices.pop()
            except:
                pass
    # best to return the indices of the edges in the path, 
    # so we can better change the residual values as well later on
    return path_indices 

def dinitz(source, sink, edges):
    # first, add the is_part_of_level_graph value to all edges (which is False)
    # while were at it, lets also add the flow values for each, which is 0
    for idx in range(len(edges)):
        edges[idx] = [edges[idx][0], edges[idx][1], 0, edges[idx][2], False]

    # save current lenght of the edges list for later
    n = len(edges)

    # create the residual edges, 
    residuals = []
    for edge in edges:
        residuals.append([edge[1], edge[0], 0, 0, False])
    edges = edges + residuals

    # output value
    out = 0
    
    # construct the level graph (step 1)
    level_graph = construct_level_graph(source, sink, edges)

    while level_graph:
        # get path using dfs, then compute for flow value in that path
        path = dfs(source, sink, level_graph)

        cfp = float('inf')
        for e in path:
            cfp = min(cfp, edges[e][3]-edges[e][2])
        out += cfp
        
        # update edges (both forward and backward edges)
        for e in path:
            edges[e][2] += cfp
            if e < n: # forward edge
                edges[e+n][2] -= cfp
            else: # residual/backward edge
                edges[e-n][2] -= cfp
                
        level_graph = construct_level_graph(source, sink, level_graph)
        path = dfs(source, sink, edges)
    return out

print(dinitz(1,10,Edges))
# outputs 60