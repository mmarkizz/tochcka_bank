import sys
from collections import deque, defaultdict

def solve(edges: list[tuple[str, str]]) -> list[str]:
    graph = defaultdict(list)
    gateways = set()
    
    # Строим граф
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
        dist = {start: 0}
        prev = {start: None}
        queue = deque([start])
        
        while queue:
            current = queue.popleft()
            for neighbor in sorted(graph[current]):  # сортируем для детерминизма
                if neighbor not in dist:
                    dist[neighbor] = dist[current] + 1
                    prev[neighbor] = current
                    queue.append(neighbor)
        return dist, prev
    
    def get_target_gateway(pos):
        dist, _ = bfs(pos)
        candidate_gates = []
        min_dist = float('inf')
        
        for gate in gateways:
            if gate in dist:
                if dist[gate] < min_dist:
                    min_dist = dist[gate]
                    candidate_gates = [gate]
                elif dist[gate] == min_dist:
                    candidate_gates.append(gate)
        
        return min(candidate_gates) if candidate_gates else None
    
    def get_next_move(pos, target_gate):
        _, prev = bfs(target_gate)
        current = pos
        while prev[current] != target_gate:
            current = prev[current]
        return current
    
    # Основной цикл
    while True:
        # Проверяем непосредственную угрозу
        immediate_threat = None
        for neighbor in sorted(graph[virus_pos]):
            if neighbor in gateways:
                immediate_threat = f"{neighbor}-{virus_pos}"
                break
        
        if immediate_threat:
            result.append(immediate_threat)
            gate, node = immediate_threat.split('-')
            graph[gate].remove(node)
            graph[node].remove(gate)
            continue
        
        # Находим целевой шлюз
        target_gate = get_target_gateway(virus_pos)
        if not target_gate:
            break
        
        # Находим следующий ход вируса
        next_pos = get_next_move(virus_pos, target_gate)
        
        # Находим критический коридор на пути к шлюзу
        # Ищем связь между следующим положением вируса и шлюзом
        critical_edge = None
        if next_pos in graph[target_gate]:
            critical_edge = f"{target_gate}-{next_pos}"
        else:
            # Ищем любой доступный коридор шлюз-узел
            available = []
            for gate in sorted(gateways):
                for node in sorted(graph[gate]):
                    if node.islower():
                        available.append(f"{gate}-{node}")
            if available:
                critical_edge = available[0]
        
        if critical_edge:
            result.append(critical_edge)
            gate, node = critical_edge.split('-')
            graph[gate].remove(node)
            graph[node].remove(gate)
        
        # Вирус перемещается
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