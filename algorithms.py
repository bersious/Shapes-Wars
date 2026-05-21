from data_structures import Queue


def bfs_find_path(grid, start, target):
    """
    Thuật toán BFS (Breadth-First Search) tìm đường đi ngắn nhất
    trên bản đồ dạng lưới 2D từ điểm xuất phát đến căn cứ.

    Tham số:
        grid (list[list[int]]): Ma trận 2D đại diện cho bản đồ.
                                0 = ô đường đi được.
                                1 = ô bị chặn (Tháp / vật cản).
        start (tuple[int, int]): Tọa độ (row, col) điểm xuất phát (Spawn Point).
        target (tuple[int, int]): Tọa độ (row, col) điểm đích (Căn cứ - Base).

    Trả về:
        list[tuple[int, int]]: Danh sách các tọa độ tạo thành đường đi ngắn nhất
                               từ start đến target (không bao gồm ô start).
                               Trả về [] nếu không tìm được đường.

    Độ phức tạp:
        - Time Complexity: O(V + E) với V là tổng số ô trên lưới (rows * cols)
                          và E là số cạnh nối giữa các ô kề nhau.
        - Space Complexity: O(V) để lưu Queue và mảng visited.
    """
    rows = len(grid)
    cols = len(grid[0])

    # Chỉ ô == 0 (Trống) hoặc == -1 (SPAWN/BASE) là đi được.
    if grid[start[0]][start[1]] not in (0, -1) or grid[target[0]][target[1]] not in (0, -1):
        return []

    frontier = Queue()
    frontier.enqueue(start)
    came_from = {start: None}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while not frontier.is_empty():
        current = frontier.dequeue()

        if current == target:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dr, dc in directions:
            neighbor = (current[0] + dr, current[1] + dc)
            nr, nc = neighbor
            if (0 <= nr < rows and
                    0 <= nc < cols and
                    grid[nr][nc] in (0, -1) and
                    neighbor not in came_from):
                frontier.enqueue(neighbor)
                came_from[neighbor] = current

    return []


def recalculate_paths(grid, monsters):
    """
    Tính lại đường đi cho tất cả quái vật đang sống trên bản đồ.
    Gọi hàm này mỗi khi người chơi đặt thêm một Tháp mới.

    Tham số:
        grid (list[list[int]]): Ma trận lưới 2D hiện tại.
        monsters (LinkedList): Danh sách liên kết chứa các đối tượng Monster.

    Độ phức tạp:
        - Time Complexity: O(M * (V + E)) với M là số quái vật đang sống.
        - Space Complexity: O(V) cho mỗi lần gọi BFS.
    """
    for monster in monsters:
        # Level 0 monsters must keep their tower-chase path — never override
        if getattr(monster, 'level_0_target_tower', None) is not None:
            continue
        new_path = bfs_find_path(grid, monster.grid_pos, monster.target_pos)
        monster.path = new_path
        monster.path_index = 0
