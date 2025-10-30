import sys
import heapq
from typing import Tuple, List, Dict, FrozenSet

# Кэш для хешей состояний
_state_cache = {}

class AmphipodState:
    __slots__ = ('rooms', 'hallway', 'energy', 'room_depth', 'hash_val')
    
    def __init__(self, rooms, hallway, energy, room_depth):
        self.rooms = rooms  # tuple of tuples, каждый room - tuple символов
        self.hallway = hallway  # tuple из 11 элементов (None или символ)
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

def parse_input(lines: List[str]) -> AmphipodState:
    """Парсит входные данные и создает начальное состояние"""
    room_depth = len(lines) - 3
    
    # Инициализируем комнаты
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
    
    # Преобразуем в кортежи
    rooms_tuple = tuple(tuple(room) for room in rooms)
    hallway_tuple = tuple(hallway)
    
    return AmphipodState(rooms_tuple, hallway_tuple, 0, room_depth)

def get_move_cost(amphipod: str) -> int:
    """Возвращает стоимость перемещения для типа амфипода"""
    return {'A': 1, 'B': 10, 'C': 100, 'D': 1000}[amphipod]

def get_target_room(amphipod: str) -> int:
    """Возвращает целевую комнату для амфипода"""
    return {'A': 0, 'B': 1, 'C': 2, 'D': 3}[amphipod]

def is_room_complete(room: Tuple[str, ...], room_index: int, room_depth: int) -> bool:
    """Проверяет, заполнена ли комната правильными амфиподами"""
    if len(room) != room_depth:
        return False
    target_char = 'ABCD'[room_index]
    return all(c == target_char for c in room)

def is_path_clear(hallway: Tuple, start: int, end: int) -> bool:
    """Проверяет, свободен ли путь в коридоре"""
    step = 1 if end > start else -1
    for pos in range(start + step, end + step, step):
        if hallway[pos] is not None:
            return False
    return True

def can_move_to_room(room: Tuple[str, ...], room_index: int, amphipod: str, room_depth: int) -> bool:
    """Проверяет, может ли амфипод переместиться в комнату"""
    # Комната должна быть целевой для этого амфипода
    if room_index != get_target_room(amphipod):
        return False
    
    # В комнате должны быть только правильные амфиподы
    for c in room:
        if c != amphipod:
            return False
    
    # В комнате должно быть место
    return len(room) < room_depth

def get_room_position(room_index: int) -> int:
    """Возвращает позицию комнаты в коридоре"""
    return [2, 4, 6, 8][room_index]

def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте с оптимизациями
    """
    initial_state = parse_input(lines)
    
    # Приоритетная очередь для алгоритма Дейкстры
    heap = []
    heapq.heappush(heap, (initial_state.energy, initial_state))
    
    # Словарь для хранения минимальной энергии для каждого состояния
    min_energy = {initial_state: 0}
    
    room_positions = [2, 4, 6, 8]
    forbidden_stops = set(room_positions)
    
    best_energy = float('inf')
    
    while heap:
        current_energy, current_state = heapq.heappop(heap)
        
        # Если нашли решение хуже лучшего, пропускаем
        if current_energy >= best_energy:
            continue
        
        # Если мы уже нашли лучший путь к этому состоянию, пропускаем
        if current_energy > min_energy.get(current_state, float('inf')):
            continue
        
        # Проверяем, является ли состояние целевым
        is_goal = True
        for i in range(4):
            if not is_room_complete(current_state.rooms[i], i, current_state.room_depth):
                is_goal = False
                break
        
        if is_goal:
            best_energy = min(best_energy, current_energy)
            continue
        
        # Оптимизация: сначала пытаемся переместить амфиподы прямо в их комнаты
        moved_directly = False
        
        # 1. Попытка переместить амфиподы из коридора прямо в их комнаты
        for hallway_pos in range(11):
            amphipod = current_state.hallway[hallway_pos]
            if amphipod is None:
                continue
            
            target_room = get_target_room(amphipod)
            room_pos = room_positions[target_room]
            
            # Проверяем возможность перемещения в комнату
            if (can_move_to_room(current_state.rooms[target_room], target_room, amphipod, current_state.room_depth) and
                is_path_clear(current_state.hallway, hallway_pos, room_pos)):
                
                # Вычисляем стоимость
                steps = abs(hallway_pos - room_pos)
                steps += (current_state.room_depth - len(current_state.rooms[target_room]))
                energy_cost = steps * get_move_cost(amphipod)
                
                # Создаем новое состояние
                new_rooms = list(current_state.rooms)
                new_room = list(new_rooms[target_room])
                new_room.append(amphipod)
                new_rooms[target_room] = tuple(new_room)
                
                new_hallway = list(current_state.hallway)
                new_hallway[hallway_pos] = None
                
                new_state = AmphipodState(
                    tuple(new_rooms), 
                    tuple(new_hallway), 
                    current_state.energy + energy_cost,
                    current_state.room_depth
                )
                
                if new_state.energy < min_energy.get(new_state, float('inf')):
                    min_energy[new_state] = new_state.energy
                    heapq.heappush(heap, (new_state.energy, new_state))
                
                moved_directly = True
        
        if moved_directly:
            continue
        
        # 2. Перемещение амфиподов из комнат в коридор
        for room_idx in range(4):
            room = current_state.rooms[room_idx]
            if not room:
                continue
            
            # Если комната уже завершена, не перемещаем из нее
            if is_room_complete(room, room_idx, current_state.room_depth):
                continue
            
            # Проверяем, есть ли неправильные амфиподы в комнате
            has_wrong_amphipod = False
            for amphipod in room:
                if get_target_room(amphipod) != room_idx:
                    has_wrong_amphipod = True
                    break
            
            # Если в комнате только правильные амфиподы, не перемещаем из нее
            if not has_wrong_amphipod:
                continue
            
            # Берем верхний амфипод из комнаты
            amphipod = room[-1]
            room_pos = room_positions[room_idx]
            
            # Глубина амфипода в комнате
            depth_in_room = current_state.room_depth - len(room) + 1
            
            # Пытаемся переместить в различные позиции коридора
            for target_pos in range(11):
                if target_pos in forbidden_stops:
                    continue
                
                if is_path_clear(current_state.hallway, room_pos, target_pos):
                    steps = depth_in_room + abs(room_pos - target_pos)
                    energy_cost = steps * get_move_cost(amphipod)
                    
                    # Создаем новое состояние
                    new_rooms = list(current_state.rooms)
                    new_room = list(room[:-1])  # Убираем верхний амфипод
                    new_rooms[room_idx] = tuple(new_room)
                    
                    new_hallway = list(current_state.hallway)
                    new_hallway[target_pos] = amphipod
                    
                    new_state = AmphipodState(
                        tuple(new_rooms), 
                        tuple(new_hallway), 
                        current_state.energy + energy_cost,
                        current_state.room_depth
                    )
                    
                    if new_state.energy < min_energy.get(new_state, float('inf')):
                        min_energy[new_state] = new_state.energy
                        heapq.heappush(heap, (new_state.energy, new_state))
    
    return best_energy if best_energy != float('inf') else -1

def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)

if __name__ == "__main__":
    main()