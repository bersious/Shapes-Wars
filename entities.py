# =============================================================================
# entities.py — Định nghĩa thực thể: Quân Bạch Quốc (kẻ xâm lược) & Vũ khí Hắc Quốc (phòng thủ)
# =============================================================================
#
# THIẾT KẾ TỔNG QUAN — HẮC QUỐC THỦ THÀNH
# ========================================
# Game có 10 Level, 7 loại Tháp (unlock dần), 6 loại Quái (mạnh dần).
#
# BẢNG THÁP (7 loại):
# ┌─────────────┬────────┬──────┬───────┬─────┬──────────────────────────────┐
# │ Tên         │ Unlock │ Dame │ Tầm   │ Tốc │ Đặc biệt                     │
# ├─────────────┼────────┼──────┼───────┼─────┼──────────────────────────────┤
# │ Ballista    │ Lv 1   │  40  │  3.0  │ 1.2 │ Bắn đơn mục tiêu, tầm xa     │
# │ Phalanx     │ Lv 2   │  25  │  2.5  │ 2.0 │ Bắn xuyên theo hàng ngang    │
# │ Ignis       │ Lv 3   │  20  │  2.0  │ 3.5 │ Burn 3s + AoE nhỏ bán kính 1 │
# │ Kronos      │ Lv 5   │   0  │  2.5  │ 1.0 │ Làm chậm 50% (Titan miễn)    │
# │ Ares        │ Lv 6   │ 120  │  3.5  │ 0.6 │ Dame cao nhất, bắn đơn       │
# │ Hephaestus  │ Lv 8   │  80  │  3.0  │ 0.8 │ Nổ AoE bán kính 1.5 ô        │
# │ Thanatos    │ Lv 10  │ 500  │  0.0  │  —  │ Mìn gài 1 lần, nổ AoE 3x3   │
# └─────────────┴────────┴──────┴───────┴─────┴──────────────────────────────┘
#
# BẢNG QUÁI (6 loại):
# ┌──────────┬────────┬─────┬────────┬──────────────────────────────────────┐
# │ Tên      │ Wave   │ HP  │ Speed  │ Đặc biệt                             │
# ├──────────┼────────┼─────┼────────┼──────────────────────────────────────┤
# │ Lurker   │ 1–3    │  60 │  1.0   │ Không có                             │
# │ Drifter  │ 2–5    │ 120 │  1.8   │ Di chuyển nhanh                      │
# │ Brute    │ 4–6    │ 280 │  0.6   │ Máu dày, chậm                        │
# │ Phantom  │ 6–8    │ 200 │  2.5   │ Né đạn 20%, Kronos chỉ chậm 50%      │
# │ Ravager  │ 7–9    │ 450 │  0.8   │ Tấn công Tháp kề cạnh               │
# │ Titan    │ 9–10   │ 900 │  0.5   │ Tấn công Tháp + miễn nhiễm Kronos   │
# └──────────┴────────┴─────┴────────┴──────────────────────────────────────┘
#
# LỘ TRÌNH 10 LEVEL:
# Lv1:  Ballista                    | Quái: Lurker
# Lv2:  + Phalanx (unlock)          | Quái: Lurker, Drifter
# Lv3:  + Ignis (unlock)            | Quái: Drifter, Brute
# Lv4:  Nâng cấp Tháp lên Lv2 (+30%)| Quái: Brute (số lượng nhiều)
# Lv5:  + Kronos (unlock)           | Quái: Phantom
# Lv6:  + Ares (unlock)             | Quái: Phantom, Ravager
# Lv7:  Nâng cấp Tháp lên Lv3 (+30%)| Quái: Ravager, Brute
# Lv8:  + Hephaestus (unlock)       | Quái: Ravager, Titan (1 con)
# Lv9:  —                           | Quái: Titan + Phantom kết hợp
# Lv10: + Thanatos (unlock)         | Quái: Tất cả + Titan số lượng lớn
# =============================================================================


# ─────────────────────────────────────────────────────────────────────────────
# BASE CLASSES
# ─────────────────────────────────────────────────────────────────────────────

class Monster:
    """
    Lớp cơ sở cho tất cả quái vật trong game.

    Thuộc tính:
        name (str): Tên loại quái.
        hp (int): Máu hiện tại.
        max_hp (int): Máu tối đa.
        speed (float): Tốc độ di chuyển (ô/giây).
        reward (int): Vàng thưởng khi bị tiêu diệt.
        damage_to_base (int): Sát thương gây ra cho căn cứ khi chạm đích.
        grid_pos (tuple): Tọa độ hiện tại trên lưới (row, col).
        target_pos (tuple): Tọa độ căn cứ (row, col).
        path (list): Danh sách tọa độ đường đi do BFS cung cấp.
        path_index (int): Vị trí hiện tại trong đường đi.
        pixel_pos (list): Tọa độ pixel thực tế để vẽ mượt trên màn hình.
        alive (bool): Trạng thái sống/chết.
        slow_multiplier (float): Hệ số giảm tốc (1.0 = bình thường).
        slow_timer (float): Thời gian còn lại của hiệu ứng chậm (giây).
        color (tuple): Màu RGB để vẽ trên Pygame.
        can_attack_tower (bool): Có thể tấn công Tháp không.
        immune_to_slow (bool): Miễn nhiễm hiệu ứng chậm của Kronos.

    Độ phức tạp khởi tạo:
        - Time: O(1) | Space: O(1)
    """

    def __init__(self, grid_pos, target_pos):
        self.name = "Monster"
        self.hp = 100
        self.max_hp = 100
        self.speed = 1.0
        self.reward = 10
        self.damage_to_base = 1
        self.grid_pos = grid_pos
        self.target_pos = target_pos
        self.path = []
        self.path_index = 0
        self.pixel_pos = [0.0, 0.0]
        self.alive = True
        self.slow_multiplier = 1.0
        self.slow_timer = 0.0
        self.color = (100, 200, 100)
        self.can_attack_tower = False
        self.immune_to_slow = False
        # Scatter properties
        self.is_scattering = True
        self.scatter_target = None

    def take_damage(self, amount):
        """
        Nhận sát thương. Quái chết nếu HP <= 0.

        Tham số:
            amount (int/float): Lượng sát thương nhận vào.

        Trả về:
            bool: True nếu quái vừa chết sau đòn này.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def apply_slow(self, multiplier, duration):
        """
        Áp dụng hiệu ứng làm chậm từ Tháp Kronos.

        Tham số:
            multiplier (float): Hệ số tốc độ sau khi chậm (0.5 = giảm 50%).
            duration (float): Thời gian hiệu ứng tồn tại (giây).

        Ghi chú:
            - Titan: immune_to_slow = True → bỏ qua hoàn toàn.
            - Phantom: slow_half = True → multiplier bị giảm còn 50% hiệu lực.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        if self.immune_to_slow:
            return
        effective_multiplier = multiplier
        if hasattr(self, 'slow_half') and self.slow_half:
            effective_multiplier = 1.0 - (1.0 - multiplier) * 0.5
        self.slow_multiplier = effective_multiplier
        self.slow_timer = duration

    def update(self, dt, cell_size):
        """
        Cập nhật vị trí pixel của quái vật theo đường đi BFS mỗi frame.

        Tham số:
            dt (float): Delta time — thời gian kể từ frame trước (giây).
            cell_size (int): Kích thước mỗi ô lưới (pixel).

        Trả về:
            bool: True nếu quái đã đến đích (căn cứ).

        Độ phức tạp: Time O(1) | Space O(1)
        """
        # Cập nhật timer hiệu ứng chậm
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_multiplier = 1.0

        if not self.path or self.path_index >= len(self.path):
            if getattr(self, 'is_scattering', False):
                self.is_scattering = False
                # Khi kết thúc đoạn tản mác, tìm đường từ vị trí tản mác về Căn cứ
                from algorithms import bfs_find_path
                # Lưu ý: grid phải được truyền vào, nhưng hàm update không có grid.
                # Chúng ta sẽ xử lý tìm đường mới ở main.py khi is_scattering chuyển sang False,
                # HOẶC truyền grid vào hàm update. Tốt nhất là thêm self.grid vào Monster khi spawn.
                if hasattr(self, 'grid_ref') and self.grid_ref:
                    self.path = bfs_find_path(self.grid_ref, self.grid_pos, self.target_pos)
                    self.path_index = 0
                    if not self.path:
                        return False # Kẹt
                    return False
            else:
                return True  # Đã đến đích

        target_cell = self.path[self.path_index]
        target_x = target_cell[1] * cell_size + cell_size // 2
        target_y = target_cell[0] * cell_size + cell_size // 2

        actual_speed = self.speed * self.slow_multiplier * cell_size
        dx = target_x - self.pixel_pos[0]
        dy = target_y - self.pixel_pos[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist <= actual_speed * dt:
            self.pixel_pos[0] = target_x
            self.pixel_pos[1] = target_y
            self.grid_pos = target_cell
            self.path_index += 1
        else:
            self.pixel_pos[0] += (dx / dist) * actual_speed * dt
            self.pixel_pos[1] += (dy / dist) * actual_speed * dt

        return self.path_index >= len(self.path) and not getattr(self, 'is_scattering', False)


# ─────────────────────────────────────────────────────────────────────────────
# 6 LOẠI QUÂN BẠCH QUỐC (Kẻ Xâm Lược)
# ─────────────────────────────────────────────────────────────────────────────

class Lurker(Monster):
    """
    Trinh Sát Trắng — tân binh Bạch Quốc, giáp nhẹ hợp kim trắng.
    Xuất hiện: Wave 1–3 | HP: 80 | Speed: 1.2 | Reward: 5 vàng
    Màu: Trắng bạc.
    """
    def __init__(self, grid_pos, target_pos):
        super().__init__(grid_pos, target_pos)
        self.name = "Lurker"
        self.hp = self.max_hp = 80
        self.speed = 1.2
        self.reward = 5
        self.damage_to_base = 1
        self.color = (80, 200, 80)


class Drifter(Monster):
    """
    Kỵ Binh Lướt — đơn vị cơ giới Bạch Quốc, ván trượt phản trọng lực.
    Xuất hiện: Wave 2–5 | HP: 160 | Speed: 2.0 | Reward: 10 vàng
    Màu: Xám bạc sáng.
    """
    def __init__(self, grid_pos, target_pos):
        super().__init__(grid_pos, target_pos)
        self.name = "Drifter"
        self.hp = self.max_hp = 160
        self.speed = 2.0
        self.reward = 10
        self.damage_to_base = 1
        self.color = (180, 220, 60)


class Brute(Monster):
    """
    Thiết Giáp Trắng — binh sĩ giáp kim cương nhân tạo, bị tẩy não.
    Xuất hiện: Wave 4–6 | HP: 400 | Speed: 0.7 | Reward: 20 vàng
    Màu: Trắng thép.
    """
    def __init__(self, grid_pos, target_pos):
        super().__init__(grid_pos, target_pos)
        self.name = "Brute"
        self.hp = self.max_hp = 400
        self.speed = 0.7
        self.reward = 20
        self.damage_to_base = 2
        self.color = (230, 100, 40)


class Phantom(Monster):
    """
    Đặc Công Bóng Ma — đội đặc nhiệm tàng hình Bạch Quốc, chip quang học.
    Xuất hiện: Wave 6–8 | HP: 250 | Speed: 2.6 | Reward: 25 vàng

    Cơ chế né đạn: 20% (chip tàng hình quang học).
    Cơ chế kháng chậm: slow_half = True → chỉ bị chậm 50% hiệu lực.

    Màu: Trắng trong suốt.
    """
    def __init__(self, grid_pos, target_pos):
        super().__init__(grid_pos, target_pos)
        self.name = "Phantom"
        self.hp = self.max_hp = 250
        self.speed = 2.6
        self.reward = 25
        self.damage_to_base = 2
        self.color = (180, 100, 230)
        self.slow_half = True
        self.dodge_chance = 0.20


class Ravager(Monster):
    """
    Phá Thành Giả — binh chủng công thành Bạch Quốc, búa plasma phá tháp.
    Xuất hiện: Wave 7–9 | HP: 600 | Speed: 0.9 | Reward: 40 vàng

    Cơ chế: can_attack_tower = True, 15 HP/lần, 1.0 lần/giây.

    Màu: Trắng vàng kim.
    """
    def __init__(self, grid_pos, target_pos):
        super().__init__(grid_pos, target_pos)
        self.name = "Ravager"
        self.hp = self.max_hp = 600
        self.speed = 0.9
        self.reward = 40
        self.damage_to_base = 3
        self.color = (200, 30, 30)
        self.can_attack_tower = True
        self.attack_damage = 15
        self.attack_speed = 1.0
        self.attack_timer = 0.0


class Titan(Monster):
    """
    Cỗ Máy Diệt Chủng — vũ khí tối thượng do vua NamDinh đặt hàng chế tạo.
    Xuất hiện: Wave 9–10 | HP: 1500 | Speed: 0.6 | Reward: 100 vàng

    Cơ chế: immune_to_slow, can_attack_tower, 40 HP/lần.

    Màu: Trắng rực rỡ + viền vàng.
    """
    def __init__(self, grid_pos, target_pos):
        super().__init__(grid_pos, target_pos)
        self.name = "Titan"
        self.hp = self.max_hp = 1500
        self.speed = 0.6
        self.reward = 100
        self.damage_to_base = 5
        self.color = (140, 0, 0)
        self.immune_to_slow = True
        self.can_attack_tower = True
        self.attack_damage = 40
        self.attack_speed = 0.8
        self.attack_timer = 0.0
        self.size_multiplier = 1.5  # To hơn 1.5x so với quái thường


# ─────────────────────────────────────────────────────────────────────────────
# BASE CLASS TOWER — Vũ khí phòng thủ Hắc Quốc
# ─────────────────────────────────────────────────────────────────────────────

class Tower:
    """
    Lớp cơ sở cho tất cả Tháp phòng thủ.

    Thuộc tính:
        name (str): Tên tháp.
        grid_pos (tuple): Vị trí trên lưới (row, col).
        damage (int): Sát thương mỗi phát bắn.
        range (float): Tầm bắn (đơn vị: số ô).
        fire_rate (float): Số lần bắn mỗi giây.
        cost (int): Chi phí đặt tháp (vàng).
        hp (int): Máu hiện tại của tháp.
        max_hp (int): Máu tối đa.
        fire_timer (float): Đếm thời gian giữa các lần bắn.
        level (int): Cấp độ hiện tại (1, 2 hoặc 3).
        unlock_level (int): Level game cần để mở khóa tháp này.
        color (tuple): Màu RGB vẽ trên Pygame.

    Độ phức tạp: Time O(1) | Space O(1)
    """

    def __init__(self, grid_pos):
        self.name = "Tower"
        self.grid_pos = grid_pos
        self.damage = 10
        self.range = 2.0
        self.fire_rate = 1.0
        self.cost = 50
        self.hp = 100
        self.max_hp = 100
        self.fire_timer = 0.0
        self.level = 1
        self.unlock_level = 1
        self.color = (50, 50, 200)

    def can_fire(self, dt):
        """
        Cập nhật timer bắn. Trả về True nếu đã sẵn sàng bắn lần tiếp theo.

        Tham số:
            dt (float): Delta time (giây).

        Trả về:
            bool: True nếu tháp được phép bắn trong frame này.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        self.fire_timer += dt
        if self.fire_timer >= 1.0 / self.fire_rate:
            self.fire_timer = 0.0
            return True
        return False

    def in_range(self, monster_grid_pos):
        """
        Kiểm tra một quái vật có nằm trong tầm bắn không.

        Tham số:
            monster_grid_pos (tuple): Tọa độ lưới (row, col) của quái vật.

        Trả về:
            bool: True nếu khoảng cách Euclidean <= tầm bắn.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        dr = self.grid_pos[0] - monster_grid_pos[0]
        dc = self.grid_pos[1] - monster_grid_pos[1]
        return (dr ** 2 + dc ** 2) ** 0.5 <= self.range

    def take_damage(self, amount):
        """
        Tháp nhận sát thương từ Ravager/Titan.

        Tham số:
            amount (int): Lượng sát thương.

        Trả về:
            bool: True nếu tháp vừa bị phá hủy.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True
        return False

    def upgrade(self):
        """
        Nâng cấp tháp lên cấp tiếp theo (tối đa cấp 3).
        Mỗi lần nâng: dame +30%, HP +20%.

        Trả về:
            bool: True nếu nâng cấp thành công, False nếu đã cấp 3.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        if self.level >= 3:
            return False
        self.level += 1
        self.damage = int(self.damage * 1.3)
        self.max_hp = int(self.max_hp * 1.2)
        self.hp = self.max_hp
        return True


# ─────────────────────────────────────────────────────────────────────────────
# 7 LOẠI VŨ KHÍ HẮC QUỐC
# ─────────────────────────────────────────────────────────────────────────────

class Ballista(Tower):
    """
    Nỏ Hắc Thạch — vũ khí cổ xưa nhất, đá obsidian xuyên giáp.
    Unlock: Level 1 | Cost: 60 | Dame: 40 | Range: 3.0 | FireRate: 1.2/s
    HP: 120 | Màu: Tím đen obsidian.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Ballista"
        self.damage = 40
        self.range = 3.0
        self.fire_rate = 1.2
        self.cost = 60
        self.hp = self.max_hp = 120
        self.unlock_level = 1
        self.color = (50, 100, 220)


class Phalanx(Tower):
    """
    Tường Gai Bóng Đêm — gai tẩm nọc rắn đen, bí kíp bộ lạc phía Đông.
    Unlock: Level 2 | Cost: 90 | Dame: 25/con | Range: 2.5 | FireRate: 2.0/s
    HP: 100 | Màu: Xanh đen.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Phalanx"
        self.damage = 25
        self.range = 2.5
        self.fire_rate = 2.0
        self.cost = 90
        self.hp = self.max_hp = 100
        self.unlock_level = 2
        self.color = (80, 180, 220)
        self.pierce = True  # Đạn xuyên qua nhiều con


class Ignis(Tower):
    """
    Lửa Hồn Tổ Tiên — ngọn lửa thiêng từ dầu hắc ín, lửa tím đen AoE.
    Unlock: Level 3 | Cost: 120 | Dame: 20 (+15 burn/s x3s) | Range: 2.0
    HP: 90 | Màu: Tím lửa.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Ignis"
        self.damage = 20
        self.range = 2.0
        self.fire_rate = 3.5
        self.cost = 120
        self.hp = self.max_hp = 90
        self.unlock_level = 3
        self.color = (230, 90, 20)
        self.burn_damage = 15
        self.burn_duration = 3.0
        self.aoe_radius = 1.0


class Kronos(Tower):
    """
    Trụ Trì Hoãn — phát minh của thầy phù thủy già nhất tộc Đen.
    Unlock: Level 5 | Cost: 150 | Dame: 0 | Range: 2.5 | FireRate: 1.0/s
    HP: 80 | Màu: Tím sẫm. Làm chậm 50%, 2 giây.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Kronos"
        self.damage = 0
        self.range = 2.5
        self.fire_rate = 1.0
        self.cost = 150
        self.hp = self.max_hp = 80
        self.unlock_level = 5
        self.color = (130, 80, 200)
        self.slow_multiplier = 0.5
        self.slow_duration = 2.0


class Ares(Tower):
    """
    Đại Bác Sấm Đen — đúc bằng thiên thạch, tiếng sấm chấn động.
    Unlock: Level 6 | Cost: 210 | Dame: 120 | Range: 3.5 | FireRate: 0.6/s
    HP: 150 | Màu: Đỏ sẫm đen.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Ares"
        self.damage = 120
        self.range = 3.5
        self.fire_rate = 0.6
        self.cost = 210
        self.hp = self.max_hp = 150
        self.unlock_level = 6
        self.color = (180, 20, 20)


class Hephaestus(Tower):
    """
    Cối Đá Phún Thạch — máy phóng dung nham núi lửa, nổ AoE.
    Unlock: Level 8 | Cost: 260 | Dame: 80 (AoE) | Range: 3.0 | FireRate: 0.8/s
    HP: 130 | Màu: Cam đen.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Hephaestus"
        self.damage = 80
        self.range = 3.0
        self.fire_rate = 0.8
        self.cost = 260
        self.hp = self.max_hp = 130
        self.unlock_level = 8
        self.color = (210, 120, 10)
        self.aoe_radius = 1.5


class Thanatos(Tower):
    """
    Bẫy Hố Tử Thần — bẫy cổ xưa nhất, phù phép bởi bảy thầy phù thủy.
    Unlock: Level 10 | Cost: 350 | Dame: 500 (AoE 3x3) | Range: 0
    HP: 50 | Màu: Đen tuyền tím. Dùng 1 lần, nổ khi địch dẫm lên.
    """
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.name = "Thanatos"
        self.damage = 500
        self.range = 0.0
        self.fire_rate = 0.0
        self.cost = 350
        self.hp = self.max_hp = 50
        self.unlock_level = 10
        self.color = (60, 60, 60)
        self.aoe_radius = 1.5  # bán kính nổ = 1.5 ô ~ vùng 3x3
        self.is_triggered = False
        self.single_use = True


# ─────────────────────────────────────────────────────────────────────────────
# BASE — Thành trì Hắc Quốc
# ─────────────────────────────────────────────────────────────────────────────

class Base:
    """
    Căn cứ của người chơi. Game kết thúc (thua) khi HP = 0.

    Thuộc tính:
        grid_pos (tuple): Vị trí trên lưới.
        hp (int): Máu căn cứ hiện tại.
        max_hp (int): Máu tối đa.
        color (tuple): Màu xanh dương đậm để phân biệt.

    Độ phức tạp: Time O(1) | Space O(1)
    """

    def __init__(self, grid_pos, max_hp=20):
        self.grid_pos = grid_pos
        self.hp = max_hp
        self.max_hp = max_hp
        self.color = (30, 80, 200)

    def take_damage(self, amount):
        """
        Căn cứ nhận sát thương khi quái đến đích.

        Tham số:
            amount (int): Lượng máu bị trừ.

        Trả về:
            bool: True nếu căn cứ vừa bị phá hủy (HP <= 0).

        Độ phức tạp: Time O(1) | Space O(1)
        """
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY — Tra cứu nhanh theo tên (dùng trong main.py)
# ─────────────────────────────────────────────────────────────────────────────

MONSTER_REGISTRY = {
    "Lurker":   Lurker,
    "Drifter":  Drifter,
    "Brute":    Brute,
    "Phantom":  Phantom,
    "Ravager":  Ravager,
    "Titan":    Titan,
}

TOWER_REGISTRY = {
    "Ballista":    Ballista,
    "Phalanx":     Phalanx,
    "Ignis":       Ignis,
    "Kronos":      Kronos,
    "Ares":        Ares,
    "Hephaestus":  Hephaestus,
    "Thanatos":    Thanatos,
}

# Danh sách tháp được mở khóa theo từng level game
TOWERS_BY_LEVEL = {
    1:  ["Ballista"],
    2:  ["Ballista", "Phalanx"],
    3:  ["Ballista", "Phalanx", "Ignis"],
    4:  ["Ballista", "Phalanx", "Ignis"],
    5:  ["Ballista", "Phalanx", "Ignis", "Kronos"],
    6:  ["Ballista", "Phalanx", "Ignis", "Kronos", "Ares"],
    7:  ["Ballista", "Phalanx", "Ignis", "Kronos", "Ares"],
    8:  ["Ballista", "Phalanx", "Ignis", "Kronos", "Ares", "Hephaestus"],
    9:  ["Ballista", "Phalanx", "Ignis", "Kronos", "Ares", "Hephaestus"],
    10: ["Ballista", "Phalanx", "Ignis", "Kronos", "Ares", "Hephaestus", "Thanatos"],
}
