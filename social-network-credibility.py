import matplotlib.pyplot as plt
import networkx as nx


import random
import math


g = nx.null_graph()
n = 0
friendship_amount = 0
source = 0
target = 0
msp = 0.5


def get_graph_info():
    """Get general input about the graph from the user"""
    global n, friendship_amount, msp
    n = int(input("Insert the requested amount of users: "))
    friendship_amount = int(input("Insert the requested amount of friendships: "))
    msp = float(input("Insert the requested MSP: "))


def get_source_target():
    """Get input from user regarding source and target nodes"""
    global source, target
    source = int(input("Insert the requested source node: "))
    target = int(input("Insert the requested target node: "))    


def main():
    """ 
    Our main, the flow is as followed:
     1. Get user input regarding graph size and MSP
     2. Generate a random undirected graph according to input parameters
        which represents our social media. The node and edge grades will be
        derived partly from its structure and partly randomly generated.
        The social network is then drawn for the user to choose source and
        target nodes.
     3. Using the inputted source we then morph our graph to a directed
        acyclic graph, with the flow of information going outwards from 
        the source.
     4. The algorithm is run on the resulting graph, returning whether
        target is an acquaintance of source and if it exists, a path whose
        TSP is >= MSP and its TSP. We have implemented the algorithm twice,
        once as described on the article and once using an optimization.
     5. We draw the new graph with its found path colored in blue.
    """
    get_graph_info()
    build_undirected_graph()
    # print_graph_with_labels()
    print_graph_with_nums()
    get_source_target()
    build_directed_graph()
    result, path, tsp = is_acquaintance()
    print("TSP received is (regular algo): " + str(tsp))
    print("Is acquaintance (regular algo): " + str(result))
    result, path, tsp = is_acquaintance_optimization()
    print("TSP received is (optimized algo): " + str(tsp))
    print("Is acquaintance (optimized algo): " + str(result))
    print_details()
    print_graph_with_labels(path=path)
    # print_graph_with_nums(path=path)


def print_details():
    for node in g.nodes():
        print("Node number: " + str(node) +"\tc: " + str(g.nodes[node]['c']))
    for (u, v) in g.edges():
        print("Edge between " + str(u) + " and " + str(v) + "\tp: " + str(g.edges[u, v]['p']))


def print_graph_with_nums(path=[]):
    """Prints the graph with the nodes number"""
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, nodelist=[n for n in g.nodes() if not n in path], node_color='r')
    nx.draw_networkx_nodes(g, pos, nodelist=path, node_color='b')
    nx.draw_networkx_edges(g, pos)
    labels = {}
    for node in g.nodes():
        labels[node] = str(node)
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=8)    
    plt.show()


def print_graph_with_labels(path=[]):
    """Print the graph with weights printed on the nodes and edges"""
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, nodelist=[n for n in g.nodes() if not n in path], node_color='r')
    nx.draw_networkx_nodes(g, pos, nodelist=path, node_color='b')
    nx.draw_networkx_edges(g, pos)
    labels = {}
    for node in g.nodes():
        labels[node] = "{:.2f}".format(g.nodes[node]['c'])
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=8)
    labels = {}
    for (u, v) in g.edges():
        labels[u, v] = "{:.2f}".format(g.edges[u, v]['p'])
    nx.draw_networkx_edge_labels(g, pos, edge_labels=labels, font_size=7)    
    plt.show()


def is_acquaintance():
    """The regular implementation as described in the article"""
    if (not target in g.nodes()):
        return (False, [], 0)
    all_paths = nx.all_simple_paths(g, source, target)
    for path in all_paths:
        tsp = compute_tsp(path)
        if tsp >= msp:
            return (True, path, tsp)
    return (False, [], 0)


def is_acquaintance_optimization():
    """
    An optimization for the algorithm:
    Instead of iterating through every path from source to target,
    we set for each edge e=(u, v) a weight attribute - w'(e) = ln(1/(e[p]*v[c])).
    We then find the shortest path from source to target. Networkx doesn't have
    a built in heaviest path method, so it is a workaround for finding the
    heaviest path when using w(e) = ln(e[p]*v[c]) as a weight function.
    The heaviest path using w as a weight function has the maximal
    TSP value out of all paths as well. We compute its TSP and check whether
    it is above MSP.
    """
    if (not target in g.nodes()):
        return (False, [], 0)
    for (u,v) in g.edges():
        g.edges[u, v]['weight'] = math.log(1 / (g.edges[u, v]['p'] * g.nodes[v]['c']))
    heaviest_path = nx.shortest_path(g, source=source, target=target, weight='weight', method='bellman-ford')
    tsp = compute_tsp(heaviest_path)
    if tsp >= msp:
        return (True, heaviest_path, tsp)
    else:
        return (False, [], tsp)


def compute_tsp(path):
    """Given a path, computes its TSP as described in the algorithm."""
    path_edges = zip(path, path[1:])
    tsp = 1
    for (u, v) in path_edges:
        tsp = tsp * g.nodes[v]['c'] * g.edges[u, v]['p']
    return tsp


def turn_to_directed_acyclic_graph():
    """
    g is a bi-directional (not undirected) graph at the time of calling
    we remove all circles (Since we look for the highest product of [0, 1]
    elements, circles can only lower it) and keep only the flow going outwards
    from the source. Another optimization is keeping only nodes reachable
    from the source.
    """
    dag = g.copy()
    dag.remove_edges_from(filter(lambda x: (x[0]-source) % n >= (x[1] - source) % n, g.edges()))
    descent = {source} | nx.descendants(dag, source)
    dag = dag.subgraph(descent)
    return dag


def set_scores():
    """
    A method that iterates through all nodes and edges, either generating or
    deriving all attributes and computing its score. The exact way it does
    so is described in the report.
    """
    handle_ffr_nodes()
    handle_ra_nodes()
    for node in g.nodes():
        g.nodes[node]['tf'] = g.degree(node)
        g.nodes[node]['ffr'] = float(g.nodes[node]['followers']) / float(g.nodes[node]['followees'])
        g.nodes[node]['aua'] = random.randint(0, 365*12)
        g.nodes[node]['c'] = compute_node_grade(node)

    for (u, v) in g.edges():
        g.edges[u, v]['mf'] = len(list(filter(lambda x: x in nx.neighbors(g, v), nx.neighbors(g, u))))
        g.edges[u, v]['fd'] = random.randint(0, min(g.nodes[u]['aua'], g.nodes[v]['aua']))
        g.edges[u, v]['oir'] = random.random()*3
        g.edges[u, v]['ra'] = compute_resemblence(u, v)
        g.edges[u, v]['p'] = compute_edge_grade(u, v)


def compute_node_grade(node):
    """set_scores helper function for computing the node score"""
    tf = g.nodes[node]['tf']
    c_tf = float(tf) / float(friendship_amount / n) if tf < friendship_amount / n else 1
    aua = g.nodes[node]['aua']
    c_aua = float(aua) / float(365) if aua < 365 else 1
    ffr = g.nodes[node]['ffr']
    c_ffr = ffr if ffr < 1 else 1
    c = float(c_tf + c_aua + c_ffr) / float(3)
    return c


def compute_edge_grade(u, v):
    """set_scores helper function for computing the edge score"""
    max_tf = max(g.nodes[u]['tf'], g.nodes[v]['tf'])
    mf = g.edges[u, v]['mf']
    p_mf = mf / (max_tf * 0.1) if mf < max_tf * 0.1 else 1
    fd = g.edges[u, v]['fd']
    p_fd = float(fd) / float(365) if fd < 365 else 1
    oir = g.edges[u, v]['oir']
    p_oir = oir if oir < 1 else 1
    p_ra = g.edges[u, v]['ra']
    p = float(p_mf + p_fd + p_oir + p_ra) / float(4)
    return p


def compute_resemblence(u, v):
    """A set_scores helper function for computing RA"""
    count_ta = 0
    count_tra = 0
    resemblence_attr = ['hometown',
                        'curr_country',
                        'curr_city',
                        'home_country',
                        'gender',
                        'language',
                        'religion']

    for attr in resemblence_attr:
        if g.nodes[u][attr] != None:
            count_ta = count_ta+1
            if g.nodes[u][attr] == g.nodes[v][attr]:
                count_tra = count_tra + 1
    if count_ta == 0:
        return 0
    return float(count_tra) / float(count_ta)


def handle_ffr_nodes():
    """a set_scores helper function for computing ffr"""
    choose_from = range(n)

    for node in g.nodes():
        g.nodes[node]['followers'] = 0

    for node in g.nodes():
        how_much = random.randint(1, n-1)
        followees = random.sample(choose_from, how_much)
        g.nodes[node]['followees'] = how_much
        for followed in followees:
             g.nodes[followed]['followers'] = g.nodes[followed]['followers'] + 1


def handle_ra_nodes():
    for node in g.nodes():
        g.nodes[node]['hometown'] = random_none_or_int(1, 200)
        g.nodes[node]['curr_country'] = random_none_or_int(1, 15)
        g.nodes[node]['curr_city'] = random_none_or_int(1, 200)
        g.nodes[node]['home_country'] = random_none_or_int(1, 15)
        g.nodes[node]['gender'] = random_none_or_int(1, 2)
        g.nodes[node]['language'] = random_none_or_int(1, 50)
        g.nodes[node]['religion'] = random_none_or_int(1, 7)


def random_none_or_int(a, b, none_rate=0.5):
    if random.random() <= none_rate:
        return None
    else:
        return random.randint(a,b)


def build_undirected_graph():
    """
    generate a random undirected graph representing the OSN using
    parameters from user input. The method then calls set_scores which
    determines the score for each node and edge
    """
    global g
    g = nx.gnm_random_graph(n, friendship_amount)
    set_scores()


def build_directed_graph():
    """turns the undirected g to a graph representing flow information"""
    global g
    g = g.to_directed()
    g = turn_to_directed_acyclic_graph()


if __name__ == "__main__":
    main()