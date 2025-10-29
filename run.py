import sys
import heapq
from typing import Tuple, List, Dict

class Amphipod:
    def __init__(self, type_char: str, room: int, depth: int):
        self.type_char = type_char
        self.room = room
        self.depth = depth
        self.cost = self.get_cost()
        self.target_room = self.get_target_room()
    
    def get_cost(self) -> int:
        costs = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
        return costs[self.type_char]
    
    def get_target_room(self) -> int:
        targets = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        return targets[self.type_char]
    
    def __repr__(self):
        return f"{self.type_char}(r{self.room}d{self.depth})"

class State:
    def __init__(self, amphipods: List[Amphipod], room_depth: int, energy: int = 0):
        self.amphipods = amphipods
        self.room_depth = room_depth
        self.energy = energy
        self.room_positions = [2, 4, 6, 8]  # Позиции комнат в коридоре
    
    def __hash__(self):
        # Хеш на основе позиций всех объектов
        positions = []
        for amphipod in sorted(self.amphipods, key=lambda x: (x.type_char, x.room, x.depth)):
            positions.append((amphipod.type_char, amphipod.room, amphipod.depth))
        return hash(tuple(positions))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __lt__(self, other):
        return self.energy < other.energy
    
    def is_goal(self) -> bool:
        # Проверяем, все ли объекты в своих целевых комнатах
        for amphipod in self.amphipods:
            if amphipod.room != amphipod.target_room:
                return False
        return True
    
    def get_room_occupancy(self, room: int) -> List[Amphipod]:
        # Возвращает объекты в указанной комнате
        return [a for a in self.amphipods if a.room == room]
    
    def get_corridor_occupancy(self) -> Dict[int, Amphipod]:
        # Возвращает объекты в коридоре (room = -1)
        corridor_amphipods = {}
        for amphipod in self.amphipods:
            if amphipod.room == -1:
                corridor_amphipods[amphipod.depth] = amphipod
        return corridor_amphipods
    
    def can_move_to_room(self, amphipod: Amphipod, target_room: int) -> Tuple[bool, int]:
        # Проверяет, может ли объект переместиться в целевую комнату
        if target_room != amphipod.target_room:
            return False, 0
        
        room_occupants = self.get_room_occupancy(target_room)
        
        # Проверяем, что в комнате нет чужих объектов
        for occupant in room_occupants:
            if occupant.type_char != amphipod.type_char:
                return False, 0
        
        # Находим максимальную доступную глубину
        max_depth = self.room_depth - 1
        for depth in range(self.room_depth):
            occupied = any(o.depth == depth for o in room_occupants)
            if not occupied:
                max_depth = depth
                break
        
        return True, max_depth
    
    def is_path_clear(self, start_pos: int, end_pos: int, exclude_amphipod: Amphipod = None) -> bool:
        # Проверяет, свободен ли путь в коридоре
        corridor = self.get_corridor_occupancy()
        
        step = 1 if end_pos > start_pos else -1
        for pos in range(start_pos + step, end_pos + step, step):
            if pos in corridor and (exclude_amphipod is None or corridor[pos] != exclude_amphipod):
                return False
        return True

def parse_input(lines: List[str]) -> State:
    """Парсит входные данные и создает начальное состояние"""
    room_depth = len(lines) - 3
    
    amphipods = []
    
    # Парсим комнаты
    for room_idx, corridor_pos in enumerate([2, 4, 6, 8]):
        for depth in range(room_depth):
            line_idx = 2 + depth
            if line_idx < len(lines):
                char = lines[line_idx][corridor_pos + 1]  # +1 из-за формата строки
                if char in 'ABCD':
                    amphipods.append(Amphipod(char, room_idx, depth))
    
    return State(amphipods, room_depth)

def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    initial_state = parse_input(lines)
    
    # Приоритетная очередь для алгоритма Дейкстры
    heap = []
    heapq.heappush(heap, (initial_state.energy, initial_state))
    
    # Словарь для хранения минимальной энергии для каждого состояния
    min_energy = {initial_state: 0}
    
    room_positions = [2, 4, 6, 8]
    forbidden_positions = set(room_positions)  # Запрещенные позиции остановки
    
    while heap:
        current_energy, current_state = heapq.heappop(heap)
        
        # Если достигли цели, возвращаем энергию
        if current_state.is_goal():
            return current_energy
        
        # Если мы уже нашли лучший путь к этому состоянию, пропускаем
        if current_energy > min_energy.get(current_state, float('inf')):
            continue
        
        # Генерируем все возможные ходы
        for i, amphipod in enumerate(current_state.amphipods):
            # Если объект в коридоре
            if amphipod.room == -1:
                # Пытаемся переместить в целевую комнату
                target_room = amphipod.target_room
                can_move, target_depth = current_state.can_move_to_room(amphipod, target_room)
                
                if can_move:
                    # Проверяем путь до комнаты
                    start_pos = amphipod.depth
                    end_pos = room_positions[target_room]
                    
                    if current_state.is_path_clear(start_pos, end_pos, amphipod):
                        # Вычисляем стоимость перемещения
                        steps = abs(start_pos - end_pos)  # Движение по коридору
                        steps += (target_depth + 1)  # Вход в комнату
                        
                        energy_cost = steps * amphipod.cost
                        
                        # Создаем новое состояние
                        new_amphipods = current_state.amphipods.copy()
                        new_amphipods[i] = Amphipod(amphipod.type_char, target_room, target_depth)
                        new_state = State(new_amphipods, current_state.room_depth, 
                                        current_state.energy + energy_cost)
                        
                        # Добавляем в очередь, если нашли лучший путь
                        if new_state.energy < min_energy.get(new_state, float('inf')):
                            min_energy[new_state] = new_state.energy
                            heapq.heappush(heap, (new_state.energy, new_state))
            
            # Если объект в комнате
            else:
                # Проверяем, может ли объект выйти из комнаты
                room_occupants = current_state.get_room_occupancy(amphipod.room)
                
                # Проверяем, не заблокирован ли объект
                is_blocked = False
                for depth in range(amphipod.depth):
                    if any(o.depth == depth for o in room_occupants):
                        is_blocked = True
                        break
                
                if is_blocked:
                    continue
                
                # Объект может выйти из комнаты
                room_pos = room_positions[amphipod.room]
                
                # Генерируем все возможные позиции в коридоре
                for target_pos in range(11):
                    # Пропускаем запрещенные позиции
                    if target_pos in forbidden_positions:
                        continue
                    
                    # Проверяем путь
                    if current_state.is_path_clear(room_pos, target_pos):
                        # Вычисляем стоимость выхода в коридор
                        steps = (amphipod.depth + 1)  # Выход из комнаты
                        steps += abs(room_pos - target_pos)  # Движение по коридору
                        
                        energy_cost = steps * amphipod.cost
                        
                        # Создаем новое состояние
                        new_amphipods = current_state.amphipods.copy()
                        new_amphipods[i] = Amphipod(amphipod.type_char, -1, target_pos)
                        new_state = State(new_amphipods, current_state.room_depth, 
                                        current_state.energy + energy_cost)
                        
                        # Добавляем в очередь, если нашли лучший путь
                        if new_state.energy < min_energy.get(new_state, float('inf')):
                            min_energy[new_state] = new_state.energy
                            heapq.heappush(heap, (new_state.energy, new_state))
    
    return -1  # Если решение не найдено

def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)

if __name__ == "__main__":
    main()