import sys
from collections import deque, defaultdict
import heapq

def solve(edges: list[tuple[str, str]]) -> list[str]:
    
    graph = defaultdict(list)
    gateways = set()
    nodes = set()
    
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
        nodes.add(u)
        nodes.add(v)
        if u.isupper():
            gateways.add(u)
        if v.isupper():
            gateways.add(v)
    
    virus_pos = 'a'
    result = []
    
    def get_gate_edges():
        gate_edges = []
        for gate in sorted(gateways):
            for neighbor in sorted(graph[gate]):
                if neighbor.islower():  # только к обычным узлам
                    gate_edges.append(f"{gate}-{neighbor}")
        return gate_edges
    
    def bfs_distances(start):
        """Вычисляет расстояния от стартовой позиции до всех узлов"""
        dist = {start: 0}
        queue = deque([start])
        
        while queue:
            current = queue.popleft()
            for neighbor in graph[current]:
                if neighbor not in dist:
                    dist[neighbor] = dist[current] + 1
                    queue.append(neighbor)
        return dist
    
    def find_target_gateway(virus_position):
        """Находит целевой шлюз для вируса"""
        dist = bfs_distances(virus_position)
        
        min_dist = float('inf')
        candidate_gates = []
        
        for gate in gateways:
            if gate in dist:
                if dist[gate] < min_dist:
                    min_dist = dist[gate]
                    candidate_gates = [gate]
                elif dist[gate] == min_dist:
                    candidate_gates.append(gate)
        
        return min(candidate_gates) if candidate_gates else None
    
    def find_next_move(virus_position, target_gate):
        """Находит следующий ход вируса"""
        dist = bfs_distances(target_gate)
        
        candidates = []
        for neighbor in sorted(graph[virus_position]):
            if neighbor in dist:
                candidates.append((dist[neighbor], neighbor))
        
        if not candidates:
            return None
        
        min_dist = min(candidates)[0]
        best_candidates = [neighbor for dist, neighbor in candidates if dist == min_dist]
        
        return min(best_candidates)
    
    def is_virus_at_gateway(virus_position):
        """Проверяет, находится ли вирус рядом со шлюзом"""
        for neighbor in graph[virus_position]:
            if neighbor in gateways:
                return True
        return False
    
    def get_critical_gate_edge(virus_position, target_gate):
        """Находит критический коридор для отключения"""
        for neighbor in sorted(graph[virus_position]):
            if neighbor in gateways:
                return f"{neighbor}-{virus_position}"
        
        dist_from_virus = bfs_distances(virus_position)
        reachable_gates = [gate for gate in gateways if gate in dist_from_virus]
        
        if not reachable_gates:
            return None
        
        available_edges = get_gate_edges()
        return available_edges[0] if available_edges else None
    
    while True:
        if is_virus_at_gateway(virus_pos):
            for neighbor in sorted(graph[virus_pos]):
                if neighbor in gateways:
                    critical_edge = f"{neighbor}-{virus_pos}"
                    if critical_edge not in result:
                        result.append(critical_edge)
                        graph[neighbor].remove(virus_pos)
                        graph[virus_pos].remove(neighbor)
                        break
           
            dist = bfs_distances(virus_pos)
            reachable = any(gate in dist for gate in gateways)
            if not reachable:
                break
            continue
        
        target_gate = find_target_gateway(virus_pos)
        if not target_gate:
            break 
        
        critical_edge = get_critical_gate_edge(virus_pos, target_gate)
        if critical_edge:
            result.append(critical_edge)
            gate, node = critical_edge.split('-')
            graph[gate].remove(node)
            graph[node].remove(gate)
        else:
            available_edges = get_gate_edges()
            if available_edges:
                critical_edge = available_edges[0]
                result.append(critical_edge)
                gate, node = critical_edge.split('-')
                graph[gate].remove(node)
                graph[node].remove(gate)
            else:
                break  
        
        next_pos = find_next_move(virus_pos, target_gate)
        if next_pos:
            virus_pos = next_pos
        else:
            break  
    
    return result

def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)

if __name__ == "__main__":
    main()