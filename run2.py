import sys
from collections import deque, defaultdict

def solve(edges: list[tuple[str, str]]) -> list[str]:
    # Build graph
    graph = defaultdict(list)
    gateways = set()
    
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
        if u.isupper():
            gateways.add(u)
        if v.isupper():
            gateways.add(v)
    
    virus_pos = 'a'
    result = []
    
    def bfs(start):
        """BFS from start node, return distances and paths"""
        dist = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in sorted(graph[current]):  # sorted for determinism
                if neighbor not in dist:
                    dist[neighbor] = dist[current] + 1
                    queue.append(neighbor)
        return dist
    
    def find_target_gateway(position):
        """Find the gateway that virus will target"""
        dist = bfs(position)
        
        # Find reachable gateways
        reachable_gates = [g for g in gateways if g in dist]
        if not reachable_gates:
            return None
            
        # Find minimum distance
        min_dist = min(dist[g] for g in reachable_gates)
        
        # Get gates with minimum distance, choose lexicographically smallest
        candidate_gates = [g for g in reachable_gates if dist[g] == min_dist]
        return min(candidate_gates)
    
    def find_next_move(position, target_gate):
        """Find virus's next move toward target gateway"""
        # Do BFS from target gateway to find optimal path
        dist = bfs(target_gate)
        
        # Check neighbors of current position
        neighbors = sorted(graph[position])
        
        # Find neighbor with smallest distance to target gateway
        best_neighbor = None
        min_dist = float('inf')
        
        for neighbor in neighbors:
            if neighbor in dist and dist[neighbor] < min_dist:
                min_dist = dist[neighbor]
                best_neighbor = neighbor
            elif neighbor in dist and dist[neighbor] == min_dist and neighbor < best_neighbor:
                best_neighbor = neighbor
                
        return best_neighbor
    
    def get_gate_edges():
        """Get all gate-node edges in lexicographic order"""
        edges_list = []
        for gate in sorted(gateways):
            for node in sorted(graph[gate]):
                if node.islower():  # only regular nodes
                    edges_list.append(f"{gate}-{node}")
        return edges_list
    
    # Main game loop
    while True:
        # Check if virus is directly connected to a gateway
        immediate_threat = None
        for neighbor in sorted(graph[virus_pos]):
            if neighbor in gateways:
                immediate_threat = f"{neighbor}-{virus_pos}"
                break
        
        if immediate_threat:
            # Cut the immediate threat
            result.append(immediate_threat)
            gate, node = immediate_threat.split('-')
            graph[gate].remove(node)
            graph[node].remove(gate)
            continue
        
        # Find target gateway for virus
        target_gate = find_target_gateway(virus_pos)
        if not target_gate:
            break  # No reachable gateways
            
        # Find virus's next move
        next_pos = find_next_move(virus_pos, target_gate)
        if not next_pos:
            break
            
        # The key insight: We need to sever edges that are on ALL optimal paths
        # to the target gateway, or if there are multiple, choose lexicographically
        
        # Get all gate edges in order
        gate_edges = get_gate_edges()
        if not gate_edges:
            break
            
        # Strategy: Sever edges connected to the target gateway first
        target_gate_edges = [edge for edge in gate_edges if edge.startswith(target_gate + '-')]
        
        if target_gate_edges:
            # Sever lexicographically smallest edge connected to target gateway
            edge_to_cut = min(target_gate_edges)
        else:
            # Sever any available gate edge
            edge_to_cut = gate_edges[0]
            
        result.append(edge_to_cut)
        gate, node = edge_to_cut.split('-')
        graph[gate].remove(node)
        graph[node].remove(gate)
        
        # Virus moves
        virus_pos = next_pos
    
    return result

def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            parts = line.split('-')
            if len(parts) == 2:
                edges.append((parts[0], parts[1]))

    result = solve(edges)
    for edge in result:
        print(edge)

if __name__ == "__main__":
    main()