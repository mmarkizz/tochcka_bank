import sys
import heapq
from typing import Tuple, List

class State:
    __slots__ = ('rooms', 'hallway', 'energy', 'room_depth', 'hash_val')
    
    def __init__(self, rooms, hallway, energy, room_depth):
        self.rooms = rooms  # tuple of tuples
        self.hallway = hallway  # tuple of 11 elements
        self.energy = energy
        self.room_depth = room_depth
        self.hash_val = None
    
    def __hash__(self):
        if self.hash_val is None:
            self.hash_val = hash((self.rooms, self.hallway))
        return self.hash_val
    
    def __eq__(self, other):
        return self.rooms == other.rooms and self.hallway == other.hallway
    
    def __lt__(self, other):
        return self.energy < other.energy

def parse_input(lines: List[str]) -> State:
    room_depth = len(lines) - 3
    rooms = [[] for _ in range(4)]
    hallway = [None] * 11
    
    room_positions = [2, 4, 6, 8]
    
    for depth in range(room_depth):
        line_idx = 2 + depth
        if line_idx < len(lines):
            line = lines[line_idx]
            for room_idx, corridor_pos in enumerate(room_positions):
                char_pos = corridor_pos + 1
                if char_pos < len(line) and line[char_pos] in 'ABCD':
                    rooms[room_idx].append(line[char_pos])
    
    # Реверсируем комнаты чтобы глубина 0 была ближе к коридору
    for i in range(4):
        rooms[i] = list(reversed(rooms[i]))
    
    rooms_tuple = tuple(tuple(room) for room in rooms)
    hallway_tuple = tuple(hallway)
    
    return State(rooms_tuple, hallway_tuple, 0, room_depth)

def get_cost(amphipod: str) -> int:
    return {'A': 1, 'B': 10, 'C': 100, 'D': 1000}[amphipod]

def get_target_room(amphipod: str) -> int:
    return {'A': 0, 'B': 1, 'C': 2, 'D': 3}[amphipod]

def is_room_available(room: Tuple, room_idx: int, room_depth: int) -> bool:
    """Комната доступна если она пустая или содержит только правильных амфиподов"""
    if not room:
        return True
    
    target_char = 'ABCD'[room_idx]
    return all(c == target_char for c in room)

def get_room_position(room_idx: int) -> int:
    return [2, 4, 6, 8][room_idx]

def is_path_clear(hallway: Tuple, start: int, end: int) -> bool:
    if start == end:
        return True
    
    step = 1 if end > start else -1
    current = start + step
    while current != end + step:
        if hallway[current] is not None:
            return False
        current += step
    return True

def get_available_hallway_positions(hallway: Tuple, start_pos: int) -> List[int]:
    """Возвращает доступные позиции в коридоре из заданной позиции"""
    available = []
    
    # Двигаемся влево
    pos = start_pos - 1
    while pos >= 0:
        if hallway[pos] is not None:
            break
        if pos not in [2, 4, 6, 8]:  # Запрещенные позиции остановки
            available.append(pos)
        pos -= 1
    
    # Двигаемся вправо
    pos = start_pos + 1
    while pos < 11:
        if hallway[pos] is not None:
            break
        if pos not in [2, 4, 6, 8]:  # Запрещенные позиции остановки
            available.append(pos)
        pos += 1
    
    return available

def solve(lines: list[str]) -> int:
    initial_state = parse_input(lines)
    heap = []
    heapq.heappush(heap, (initial_state.energy, initial_state))
    visited = {initial_state: initial_state.energy}
    
    room_positions = [2, 4, 6, 8]
    
    while heap:
        current_energy, state = heapq.heappop(heap)
        
        # Проверяем цель
        goal_reached = True
        for i in range(4):
            target_char = 'ABCD'[i]
            if len(state.rooms[i]) != state.room_depth or not all(c == target_char for c in state.rooms[i]):
                goal_reached = False
                break
        
        if goal_reached:
            return state.energy
        
        if current_energy > visited.get(state, float('inf')):
            continue
        
        # 1. Перемещение из коридора в комнаты
        for hallway_pos in range(11):
            amphipod = state.hallway[hallway_pos]
            if amphipod is None:
                continue
            
            target_room = get_target_room(amphipod)
            room_pos = room_positions[target_room]
            
            # Проверяем возможность перемещения в комнату
            if (is_room_available(state.rooms[target_room], target_room, state.room_depth) and
                is_path_clear(state.hallway, hallway_pos, room_pos)):
                
                # Количество шагов
                hallway_steps = abs(hallway_pos - room_pos)
                room_steps = state.room_depth - len(state.rooms[target_room])
                total_steps = hallway_steps + room_steps
                
                energy_cost = total_steps * get_cost(amphipod)
                
                # Создаем новое состояние
                new_rooms = list(state.rooms)
                new_room = list(new_rooms[target_room])
                new_room.append(amphipod)
                new_rooms[target_room] = tuple(new_room)
                
                new_hallway = list(state.hallway)
                new_hallway[hallway_pos] = None
                
                new_state = State(
                    tuple(new_rooms),
                    tuple(new_hallway),
                    state.energy + energy_cost,
                    state.room_depth
                )
                
                if new_state.energy < visited.get(new_state, float('inf')):
                    visited[new_state] = new_state.energy
                    heapq.heappush(heap, (new_state.energy, new_state))
        
        # 2. Перемещение из комнат в коридор
        for room_idx in range(4):
            room = state.rooms[room_idx]
            if not room:
                continue
            
            # Проверяем, нужно ли перемещать амфиподы из этой комнаты
            target_char = 'ABCD'[room_idx]
            room_correct = True
            for amphipod in room:
                if amphipod != target_char:
                    room_correct = False
                    break
            
            # Если все амфиподы в комнате правильные, не перемещаем
            if room_correct:
                continue
            
            # Берем верхний амфипод
            amphipod = room[-1]
            room_pos = room_positions[room_idx]
            
            # Количество шагов чтобы выйти из комнаты
            room_exit_steps = state.room_depth - len(room) + 1
            
            # Находим доступные позиции в коридоре
            available_positions = get_available_hallway_positions(state.hallway, room_pos)
            
            for target_pos in available_positions:
                hallway_steps = abs(room_pos - target_pos)
                total_steps = room_exit_steps + hallway_steps
                energy_cost = total_steps * get_cost(amphipod)
                
                # Создаем новое состояние
                new_rooms = list(state.rooms)
                new_room = list(room[:-1])  # Убираем верхний амфипод
                new_rooms[room_idx] = tuple(new_room)
                
                new_hallway = list(state.hallway)
                new_hallway[target_pos] = amphipod
                
                new_state = State(
                    tuple(new_rooms),
                    tuple(new_hallway),
                    state.energy + energy_cost,
                    state.room_depth
                )
                
                if new_state.energy < visited.get(new_state, float('inf')):
                    visited[new_state] = new_state.energy
                    heapq.heappush(heap, (new_state.energy, new_state))
    
    return -1

def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))
    
    result = solve(lines)
    print(result)

if __name__ == "__main__":
    main()