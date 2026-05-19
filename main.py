import pygame
import sys
import math
import random
import os
import json
import asyncio
from data_structures import LinkedList, Queue, PriorityQueue
from algorithms import bfs_find_path, recalculate_paths

SAVE_FILE = "save_data.json"
def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('unlocked_level', 1), data.get('has_selected_faction', False), data.get('has_seen_intro', False), data.get('has_beaten_game', False)
        except:
            pass
    return 1, False, False, False

def save_progress(unlocked_level, has_selected_faction, has_seen_intro, has_beaten_game=False):
    with open(SAVE_FILE, 'w') as f:
        json.dump({
            'unlocked_level': unlocked_level, 
            'has_selected_faction': has_selected_faction,
            'has_seen_intro': has_seen_intro,
            'has_beaten_game': has_beaten_game
        }, f)

# Đường dẫn tới ảnh nền do người dùng cung cấp
BG_IMAGE_PATH = "assets/backgrounds/background.png.png"

try:
    from entities import (
        Lurker, Drifter, Brute, Phantom, Ravager, Titan,
        Ballista, Phalanx, Ignis, Kronos, Ares, Hephaestus, Thanatos,
        Base, TOWERS_BY_LEVEL, TOWER_REGISTRY, MONSTER_REGISTRY
    )
except ImportError:
    print("Vui lòng đảm bảo các file entities.py, algorithms.py, data_structures.py nằm cùng thư mục.")
    sys.exit()

GRID_ROWS = 14
GRID_COLS = 20
CELL_SIZE = 48
SIDEBAR_WIDTH = 300
SCREEN_W = GRID_COLS * CELL_SIZE + SIDEBAR_WIDTH
SCREEN_H = GRID_ROWS * CELL_SIZE
FPS = 60

SPAWN_POS = (1, 0)
BASE_POS = (GRID_ROWS - 2, GRID_COLS - 1)

C_BG = (15, 18, 25)
C_GRID_LINE = (35, 40, 55)
C_SIDEBAR = (20, 22, 30)
C_TEXT = (220, 230, 240)
C_TEXT_DIM = (120, 130, 150)
C_GOLD = (255, 190, 50)
C_MENU_BG = (10, 12, 18)
C_MENU_BOX = (22, 25, 35)
C_BASE = (80, 20, 120)
C_SPAWN = (220, 220, 240)
STARTING_GOLD = 180
WAVE_CLEAR_BONUS = 50

INTRO_STORY_TEXTS = [
    "Từ thuở khai thiên lập địa, thế giới của những Hình Khối vốn là một bức tranh tuyệt mĩ, được dệt nên bởi sự cân bằng hoang sơ của vạn vật. Nơi đó không có chiến tranh, không có ranh giới, mà chỉ có những quy luật tự nhiên khắc nghiệt nhưng công bằng chi phối mọi sự sống.\n\nTrải qua hàng ngàn năm tiến hóa dưới sự dịch chuyển của các tầng kiến tạo, thế giới dần chia cắt thành hai cực đối lập hoàn toàn. Sự phân chia này khởi nguồn cho hai nền văn minh vĩ đại rẽ theo hai hướng đi khác biệt vĩnh viễn.",
    "Ở phương Bắc, Bạch Quốc vươn mình trỗi dậy dưới ánh sáng rực rỡ của khoa học và công nghệ. Họ tự nhận mình là giống loài thượng đẳng, được sinh ra để thống trị. Những cung điện dát vàng mọc lên từ băng tuyết, những cỗ máy cơ khí tối tân gầm rú trên bầu trời.\n\nNgười Bạch Quốc sở hữu bộ óc thiên tài và vẻ ngoài lạnh lùng, hoàn mĩ. Tuy nhiên, đằng sau sự hào nhoáng đó là một xã hội vô cảm, máy móc, nơi mọi thứ đều được tính toán bằng lợi ích và sức mạnh.",
    "Trái ngược hoàn toàn, phương Nam xa xôi lại là thánh địa của người tộc Đen - Hắc Quốc. Đúng vậy, họ không có những bộ óc thiên tài để chế tạo vũ khí laser hay tàu vũ trụ. Vẻ bề ngoài của họ có phần hung tợn, thô ráp và tính khí đôi lúc bốc đồng.\n\nNhưng đằng sau diện mạo hoang dã ấy, người Hắc Quốc lại mang trong mình trái tim nồng ấm. Họ sống với nhau bằng thứ tình nghĩa sắt son và tinh thần đoàn kết vững chãi như bàn thạch. Với họ, một người ngã xuống, vạn người đứng lên.",
    "Thế nhưng, sự cân bằng đã vỡ vụn khi vị vua thứ 18 của Bạch Quốc lên ngôi — NamDinh. Không ai ngờ rằng, ngọn lửa của cuộc chiến tranh tàn khốc nhất lịch sử lại chẳng bắt nguồn từ một âm mưu chính trị đại sự nào, mà chỉ từ một vết sẹo tâm lý thuở thiếu thời.\n\nChỉ vì một lần bị một kẻ lang thang tộc Đen móc mất chiếc ví khi còn nhỏ, NamDinh đã nuôi dưỡng một lòng căm ghét cực đoan, biến sự thù hận cá nhân thành nỗi kỳ thị chủng tộc sâu sắc.",
    "Khi nắm đại quyền trong tay, NamDinh dõng dạc tuyên bố trước toàn vương quốc: Người tộc Đen là những kẻ hạ đẳng, là vết nhơ của thế giới cần phải bị loại bỏ tận gốc. Tiếng còi báo động xé toạc bầu trời phương Bắc.\n\nĐại quân Bạch Quốc với những binh đoàn cơ giới bọc thép tàn nhẫn, mang theo vũ khí hủy diệt tối tân nhất, rầm rộ tràn xuống phương Nam như một cơn hồng thủy trắng xóa muốn nghiền nát mọi thứ.",
    "Giữa lúc đất nước lâm nguy, tai họa lại ập đến khi vị vua thứ 35 của tộc Đen đột ngột băng hà vì bạo bệnh. Cả Hắc Quốc chìm trong tang thương. Vận mệnh của hàng vạn sinh linh lúc này được đặt cả lên vai người con gái duy nhất của ngài — Thanh Hoa.\n\nBước lên ngôi vị Nữ hoàng thứ 36, Thanh Hoa không chỉ sở hữu vẻ đẹp nghiêng nước nghiêng thành, mà còn là một bậc kỳ tài hiếm có trong lịch sử vương quốc.",
    "Nàng thông minh, sắc sảo và mang một trái tim quả cảm không biết cúi đầu. Đối mặt với hỏa lực áp đảo, những cỗ máy khổng lồ không biết đau đớn của kẻ thù, Nữ hoàng Thanh Hoa biết rằng nàng không thể dùng sức mạnh cơ bắp thuần túy.\n\nNàng phải dùng đến những chiến thuật phòng ngự đỉnh cao, kết hợp với các loại bẫy và tháp canh ma thuật cổ xưa để bảo vệ những người dân tình nghĩa của mình.",
    "Tiếng tù và chiến trận từ sừng thú đã vang vọng khắp mọi bờ cõi phương Nam. Bầu trời nhuốm màu máu, mặt đất rung chuyển dưới gót chân quân thù. Không còn đường lùi nữa!\n\nHỡi Nữ hoàng, hãy bày binh bố trận, vạch sẵn nghiêm phòng. Cuộc kháng chiến sinh tồn vĩ đại nhất lịch sử của Hắc Quốc... chính thức bắt đầu."
]

CAMPAIGN_STORY = {
    1: "Tiếng tù và chiến trận vang lên từ biên giới phía Bắc! Đại quân Bạch Quốc đã vượt qua dãy Bạch Sơn. Đội Trinh Sát Trắng đang dò đường tiến vào lãnh thổ. Nữ hoàng Thanh Hoa ra lệnh kích hoạt tuyến phòng thủ đầu tiên — những Nỏ Hắc Thạch cổ xưa đã ngủ yên trăm năm nay lại được đánh thức. Cuộc chiến sinh tồn của Hắc Quốc bắt đầu!",
    2: "Tin xấu: Bạch Quốc triển khai Kỵ Binh Lướt — đơn vị cơ giới với tốc độ kinh hoàng. Chúng vượt qua tầm bắn trước khi Nỏ kịp ngắm! Nữ hoàng Thanh Hoa ra lệnh cho bộ lạc phía Đông dựng lên Tường Gai Bóng Đêm — hàng rào gai độc xuyên đội hình kẻ thù.",
    3: "Mặt đất rung chuyển dưới bước chân của Thiết Giáp Trắng! Lớp giáp kim cương nhân tạo của chúng miễn nhiễm gần như mọi loại đạn. Nữ hoàng triệu tập hội đồng trưởng lão, và Trưởng lão Thắp Lửa đã đáp lại bằng ngọn Lửa Hồn Tổ Tiên — ngọn lửa tím đen thiêu rụi mọi thứ.",
    4: "Bạch Quốc tung đợt tổng tấn công với số lượng chưa từng có! Lurker, Drifter, Brute — ồ ạt tràn vào như sóng thần. Tin vui: thợ rèn Hắc Quốc tìm ra cách Nâng cấp Tháp (Chuột Phải) bằng phù văn cổ đại. Hãy tối ưu hóa phòng tuyến, thưa Nữ hoàng!",
    5: "Đặc Công Bóng Ma — sát thủ tàng hình với chip quang học. Đạn trượt, mắt thường không thể thấy. Giữa lúc tuyệt vọng, thầy phù thủy già nhất tộc Đen hoàn thành phát minh cả đời: Trụ Trì Hoãn — sóng năng lượng tối bóp méo không-thời gian, khiến kẻ thù chậm lại.",
    6: "Phá Thành Giả xuất hiện! Chúng không đi qua tháp — chúng ĐÁNH SẬP tháp! Búa plasma nghiền nát phòng tuyến. Nữ hoàng Thanh Hoa ra lệnh kéo khẩu Đại Bác Sấm Đen — vũ khí thiên thạch — vào chiến trường. Mỗi phát bắn, một tiếng sấm, một kẻ thù ngã gục.",
    7: "Ravager và Brute phối hợp tạo sóng công thành khổng lồ. Giáp dày phía trước, búa phá phía sau. Thợ rèn Hắc Quốc bẻ khóa bí mật Nâng cấp Cấp 3 — phù văn tối thượng từ cuốn sách cổ Vua cha để lại. Đây là cuộc chiến sinh tồn!",
    8: "CẢNH BÁO TỐI THƯỢNG! Cỗ Máy Diệt Chủng — vũ khí tận diệt do đích thân vua NamDinh ra lệnh chế tạo — đang tiến về thành. Nữ hoàng nhớ lời cha: 'Khi kẻ thù đưa núi đến, con hãy ném lại cho chúng cả ngọn núi lửa.' Cối Đá Phún Thạch được đưa ra chiến trường!",
    9: "Titan phá vỡ vòng ngoài. Đặc Công Bóng Ma lợi dụng hỗn loạn xâm nhập. Hắc Quốc bên bờ sụp đổ. Nữ hoàng Thanh Hoa đứng trên tường thành thì thầm: 'Cha ơi, con sẽ không để vương quốc này sụp đổ. Một người ngã xuống, vạn người đứng lên.' Hãy cầm cự bằng MỌI GIÁ!",
    10: "Trận chiến cuối cùng! NamDinh tung toàn lực — Titan dẫn đầu, Brute, Phantom, Ravager theo sau. Nhưng Nữ hoàng có câu trả lời cuối cùng: Bẫy Hố Tử Thần — bẫy cổ xưa nhất, phù phép bởi bảy thầy phù thủy. 'Đây là đất của chúng ta. Và chúng ta sẽ bảo vệ nó.' Vinh quang thuộc về Hắc Quốc!"
}

WAVES_BY_LEVEL = {
    1: ["Lurker"] * 25,
    2: (["Lurker", "Lurker", "Drifter"] * 5) + ["Drifter"] * 5 + ["Lurker"] * 5,
    3: (["Drifter", "Brute"] * 8) + ["Drifter"] * 4,
    4: (["Lurker", "Drifter", "Brute"] * 12) + ["Brute"] * 3 + ["Lurker"] * 3,
    5: (["Brute", "Phantom"] * 12),
    6: (["Phantom", "Phantom", "Ravager"] * 7) + ["Ravager"],
    7: (["Brute", "Phantom", "Ravager"] * 10) + ["Brute"] * 5 + ["Ravager"] * 2,
    8: (["Phantom", "Ravager"] * 12) + ["Titan"] + ["Ravager"] * 3,
    9: ["Titan"] + (["Phantom", "Phantom", "Ravager"] * 10) + ["Titan"] + ["Ravager"] * 2,
    10: ["Titan", "Titan"] + (["Brute", "Phantom", "Ravager"] * 20) + ["Titan", "Titan"],
}

OBSTACLES_BY_LEVEL = {
    1: [(4, 10), (5, 10), (8, 10), (9, 10)], # Easy wall
    2: [(0, 8), (1, 8), (2, 8), (3, 8), (10, 12), (11, 12), (12, 12), (13, 12)], # Offset walls
    3: [(2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 15), (9, 15), (10, 15), (11, 15), (12, 15), (13, 15)], # Big stagger
    4: [(4, 8), (4, 9), (4, 10), (5, 8), (5, 9), (5, 10), (6, 8), (6, 9), (6, 10), (7, 8), (7, 9), (7, 10), (8, 8), (8, 9), (8, 10)], # Huge block
    5: [(0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (9, 10), (10, 10), (11, 10), (12, 10), (13, 10), (4, 9), (9, 9)], # Tight choke
    6: [(4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (4, 14), (5, 14), (6, 14), (7, 14), (8, 14), (9, 14), (6, 9), (7, 9)], # Split and center block
    7: [(2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (6, 12), (7, 12), (8, 12), (9, 12), (10, 12), (11, 12), (12, 12), (2, 8), (3, 8), (11, 8), (12, 8)], # Zig zag extra
    8: [(2, 3), (3, 3), (4, 3), (5, 3), (2, 7), (3, 7), (4, 7), (5, 7), (8, 11), (9, 11), (10, 11), (11, 11), (8, 15), (9, 15), (10, 15), (11, 15)], # Dense blocks
    9: [(2, 4), (2, 5), (2, 6), (11, 5), (11, 6), (11, 7), (6, 10), (7, 10), (2, 14), (2, 15), (11, 14), (11, 15), (6, 16), (7, 16)], # Heavy scattered rocks
    10: [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (11, 18), (11, 17), (11, 16), (11, 15), (11, 14), (11, 13), (11, 12), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (4, 17), (5, 17), (6, 17), (7, 17), (8, 17)] # Labyrinth extra
}

FINAL_STORY_TEXTS = [
    "Sau nhiều lần tấn công thất bại dồn dập, vua NamDinh đã phải gánh chịu làn sóng phản đối vô cùng mạnh mẽ từ chính người dân Bạch Quốc. Cuộc chiến vô nghĩa kéo dài chỉ mang lại nỗi đau thương cùng cực cho cả hai bên.",
    "Lúc này, quân Kháng chiến Bạch Quốc trỗi dậy mạnh mẽ. Họ đã bắt giữ vua NamDinh và trao trả ông cho phía Hắc Quốc xử tử. Đây là bước đi quyết định nhằm cầu hòa và chấm dứt chiến tranh giữa hai quốc gia.",
    "Lúc này, quân Kháng chiến Bạch Quốc trỗi dậy mạnh mẽ. Họ đã bắt giữ vua NamDinh và trao trả ông cho phía Hắc Quốc xử tử. Đây là bước đi quyết định nhằm cầu hòa và chấm dứt chiến tranh giữa hai quốc gia.",
    "Người đứng đầu quân Kháng chiến là tướng Perseus chính thức lên ngôi vua mới của Bạch Quốc. Ông tích cực viện trợ những công nghệ ánh sáng tiên tiến nhất để hỗ trợ phía Hắc Quốc khôi phục và xây dựng lại vương quốc phồn vinh.",
    "Từ đây, khói lửa chiến tranh hoàn toàn lùi xa. Hai vương quốc chính thức đạt được sự toàn vẹn và thịnh trị lâu dài, khi cả ánh sáng và bóng tối từ nay đã có thể học cách thấu hiểu, tôn trọng và chung sống hòa bình bên nhau."
]

GAMEOVER_QUOTES = [
    "Nữ hoàng Thanh Hoa tôn kính đã sa lưới quân thù, Hắc Quốc nay chìm vào bóng tối vĩnh hằng...",
    "Thiết đao lạnh lẽo gác lên cổ Nữ hoàng, tiếng kèn khải hoàn của Bạch Quốc vang lên rền vang.",
    "Bạch Quốc đã san bằng mọi phòng tuyến, triều đại Hắc Quốc chính thức sụp đổ từ đây.",
    "Nữ hoàng Thanh Hoa ngẩng cao đầu trước giờ phán xét, linh hồn nàng sẽ mãi bảo vệ đất đai này!"
]

VICTORY_QUOTES = [
    "Phòng tuyến Hắc Quốc vững chãi như bàn thạch! Quân xâm lược Bạch Quốc buộc phải tháo chạy!",
    "Kháng chiến thành công mỹ mãn! Ánh sáng kiêu ngạo của Bạch Quốc đã phải lu mờ trước bóng tối!",
    "Máu và cát dội lên khúc khải hoàn! Người tộc Đen đã bảo vệ thành công chủ quyền thiêng liêng!",
    "Từng bước đẩy lùi gông cùm! Ngày tự do và bình đẳng đang đến rất gần với chúng ta!"
]

ENCYCLOPEDIA_DATA = {
    "Lurker": {"name": "Lurker (Trinh Sát Trắng)", "stats": "HP: 80 | Speed: 1.2 | DMG: 1 | Reward: 5", "lore": "Lính trinh sát cấp thấp của Bạch Quốc, trang bị giáp nhẹ hợp kim trắng. Tân binh bị đẩy ra tiền tuyến làm bia thí quân. Yếu ớt nhưng kéo đến với số lượng áp đảo."},
    "Drifter": {"name": "Drifter (Kỵ Binh Lướt)", "stats": "HP: 160 | Speed: 2.0 | DMG: 1 | Reward: 10", "lore": "Đơn vị cơ giới hóa của Bạch Quốc, di chuyển trên ván trượt phản trọng lực. Tự xưng là 'gió trắng' — đến và đi trước khi ai kịp phản ứng."},
    "Brute": {"name": "Brute (Thiết Giáp Trắng)", "stats": "HP: 400 | Speed: 0.7 | DMG: 2 | Reward: 20", "lore": "Binh sĩ thiết giáp nặng mang giáp kim cương nhân tạo. Chậm chạp nhưng gần như bất khả xuyên phá. Đã bị tẩy não bởi tuyên truyền chủng tộc thượng đẳng."},
    "Phantom": {"name": "Phantom (Đặc Công Bóng Ma)", "stats": "HP: 250 | Speed: 2.6 | DMG: 2 | Reward: 25", "lore": "[ĐẶC TÍNH] Né đạn 20%, kháng chậm 50%. Đội đặc nhiệm ưu tú nhất Bạch Quốc, cấy chip tàng hình quang học. Con dao sắc nhất của vua NamDinh."},
    "Ravager": {"name": "Ravager (Phá Thành Giả)", "stats": "HP: 600 | Speed: 0.9 | DMG: 3 | Reward: 40", "lore": "[ĐẶC TÍNH] Tấn công Tháp kề cạnh (15 HP/s). Binh chủng công thành mang búa plasma. Cuồng tín coi việc phá thành tộc Đen là 'sứ mệnh thanh lọc'."},
    "Titan": {"name": "Titan (Cỗ Máy Diệt Chủng)", "stats": "HP: 1500 | Speed: 0.6 | DMG: 5 | Reward: 100", "lore": "[ĐẶC TÍNH] Đánh tháp 40 HP/s, miễn nhiễm làm chậm. Vũ khí tối thượng do đích thân vua NamDinh đặt hàng chế tạo. Biểu tượng cho đỉnh cao tàn bạo công nghệ."},
    "Ballista": {"name": "Ballista (Nỏ Hắc Thạch)", "stats": "Cost: 60 | DMG: 40 | Range: 3.0 | Rate: 1.2/s", "lore": "Vũ khí cổ xưa nhất của tộc Đen, chế từ đá obsidian. Mũi tên đen xuyên giáp đáng kinh ngạc. Biểu tượng sự kiên cường — đơn giản, bền bỉ, không bao giờ gãy."},
    "Phalanx": {"name": "Phalanx (Tường Gai Bóng Đêm)", "stats": "Cost: 90 | DMG: 25 | Range: 2.5 | Rate: 2.0/s", "lore": "Hàng rào gai tẩm nọc rắn đen — bí kíp gia truyền bộ lạc phía Đông Hắc Quốc. Gai đen bắn ra xuyên qua hàng ngũ, trúng nhiều mục tiêu. Thô sơ nhưng cực kỳ hiệu quả."},
    "Ignis": {"name": "Ignis (Lửa Hồn Tổ Tiên)", "stats": "Cost: 120 | DMG: 20+15/s Burn | Range: 2.0", "lore": "Ngọn lửa thiêng từ dầu hắc ín — 'vàng đen' của tộc Đen. Bùng lên thành lửa tím đen không thể dập tắt. Mỗi ngọn lửa là lời cầu nguyện đến linh hồn tổ tiên."},
    "Kronos": {"name": "Kronos (Trụ Trì Hoãn)", "stats": "Cost: 150 | Làm chậm 50% | Range: 2.5", "lore": "Phát minh của thầy phù thủy già nhất tộc Đen. Trụ đá đen phát sóng năng lượng tối, bóp méo không-thời gian. Bằng chứng trí tuệ tộc Đen không thua kém ai."},
    "Ares": {"name": "Ares (Đại Bác Sấm Đen)", "stats": "Cost: 210 | DMG: 120 | Range: 3.5 | Rate: 0.6/s", "lore": "Đại bác đúc bằng thiên thạch rơi xuống Hắc Quốc trăm năm trước. Mỗi phát bắn tạo tiếng sấm chấn động chiến trường. Mỗi viên đạn phải chạm khắc phù văn trước khi bắn."},
    "Hephaestus": {"name": "Hephaestus (Cối Đá Phún Thạch)", "stats": "Cost: 260 | DMG: 80 (AoE 3x3) | Range: 3.0", "lore": "Máy phóng đá núi lửa — tận dụng dung nham từ ngọn núi lửa thánh ở rìa Hắc Quốc. Đá nóng chảy nổ tung trên diện rộng. Vũ khí quyết định cho trận chiến bầy đàn."},
    "Thanatos": {"name": "Thanatos (Bẫy Hố Tử Thần)", "stats": "Cost: 350 | DMG: 500 | 1 lần dùng", "lore": "Bẫy cổ xưa nhất tộc Đen — hố sâu che đậy bằng lá khô, phù phép bởi bảy thầy phù thủy. Khi dẫm lên, mặt đất sụp xuống nuốt chửng vùng 3x3. Một lần — đủ thay đổi cục diện."}
}



OUTRO_TEXT = """
BÁO CÁO TỔNG KẾT ĐỒ ÁN MÔN HỌC
CẤU TRÚC DỮ LIỆU VÀ GIẢI THUẬT
Lớp: IT003.Q21.TTNT
========================================================================

--- TÊN ĐỀ TÀI CHÍNH THỨC ---
Xây dựng Game Thủ Thành (Tower Defense) ứng dụng các 
Thuật toán Tìm đường và Cấu trúc dữ liệu nâng cao.


--- NHÀ PHÁT TRIỂN DUY NHẤT (SOLE DEVELOPER) ---
Họ và tên: Nguyễn Thành Thiện Nhân
Mã số sinh viên: 25521290
Biệt danh / Gaming Nickname: bersious.
Email liên hệ: 25521290@gm.uit.edu.vn


--- PHÁT TRIỂN Ý TƯỞNG & KỊCH BẢN ---
Biên kịch & Thiết kế Logic: bersious.
Dự án được hoàn thiện dựa trên ý tưởng cốt lõi của tác giả
cùng với những lời nhận xét, góp ý vô cùng giá trị 
đến từ những người bạn thân thiết.


--- THIẾT KẾ ĐỒ HỌA TRỰC QUAN (UI/UX ART) ---
Kỹ sư thiết kế Prompt (Prompt Engineer): bersious.
Toàn bộ hệ thống tài nguyên hình ảnh, nhân vật, 
quái vật và tháp phòng thủ trong trò chơi 
đều được tạo lập độc quyền bởi Gemini AI 
thông qua các câu lệnh mô tả chi tiết của tác giả.


--- NỀN TẢNG CÔNG NGHỆ & NGÔN NGỮ ---
Ngôn ngữ lập trình cốt lõi: Python 3
Thư viện quản lý đồ họa và tương tác: Pygame
Hệ thống quản lý mã nguồn và phiên bản: Git & GitHub


--- CÁC CẤU TRÚC DỮ LIỆU TỰ TRIỂN KHAI (FROM SCRATCH) ---
Để đáp ứng chuẩn kiến thức môn học, 100% các cấu trúc dữ liệu
sau đây đã được tác giả tự lập trình thủ công hoàn toàn
mà không sử dụng bất kỳ thư viện hỗ trợ sẵn nào của Python:

1. Linked List (Danh sách liên kết):
   - Trực tiếp quản lý và tối ưu hóa bộ nhớ cho danh sách 
     quái vật (Enemies) xuất hiện liên tục trên bản đồ lưới.
   - Thao tác Thêm/Xóa phần tử đạt độ phức tạp tối ưu O(1).

2. Queue (Hàng đợi chuẩn FIFO):
   - Điều phối và quản lý hệ thống sinh quái vật theo từng đợt 
     (Wave System) một cách tuần tự và chính xác.

3. Priority Queue (Hàng đợi ưu tiên):
   - Cài đặt AI thông minh cho các tháp phòng thủ (Towers).
   - Giúp tháp tự động tính toán, phân loại và truy xuất nhanh nhất 
     Mục tiêu tối thượng (Quái gần căn cứ nhất hoặc máu thấp nhất).


--- THUẬT TOÁN AI CỐT LÕI (PATHFINDING AI) ---
Thuật toán Breadth-First Search (BFS):
- Áp dụng trên môi trường ma trận lưới 2D không trọng số.
- Đảm bảo tìm ra tuyến đường ngắn nhất từ điểm xuất phát đến căn cứ.
- Tự động gọi lại và tính toán lại lộ trình theo thời gian thực (Real-time)
  ngay khi người chơi đặt tháp mới để tạo chướng ngại vật né tránh.
- Độ phức tạp thời gian đạt chuẩn: O(V + E)


--- HỆ THỐNG CỐ VẤN AI & THAM KHẢO (AI CO-PILOT) ---
Quá trình tối ưu hóa mã nguồn và xử lý các lỗi thuật toán phức tạp
có sự đồng hành, hỗ trợ tra cứu từ Hệ thống Antigravity 
thông qua các mô hình ngôn ngữ lớn tiên tiến nhất:
- Gemini 3.1
- Claude Opus 4.7
- Claude Sonnet 4.6


--- ÂM NHẠC XUYÊN SUỐT TRÒ CHƠI (OFFICIAL SOUNDTRACK) ---
Bài hát chủ đề: Ước Anh Tan Nát Con Tim
Thể hiện bởi nghệ sĩ: Phùng Khánh Linh
Nguồn phát trực tuyến: YouTube Official Visualizer
Đường dẫn âm nhạc: https://www.youtube.com/watch?v=xg0hNDgqurM
(Giai điệu mang đến một không gian kịch tính, đầy cảm xúc
hòa quyện vào những trận chiến thủ thành căng thẳng)
*dạo này bản quyền gắt, mong mik ko bị đánh bản quyền


========================================================================
MỨC ĐỘ HOÀN THÀNH DỰ ÁN: 100%
*Hoàn thành trong một đêm: 18-19/05/2026
CẢM ƠN BẠN ĐÃ TRẢI NGHIỆM TRÒ CHƠI CỦA BERSIOUS.!
GAME OVER - VICTORY IS YOURS!
========================================================================
Cảm ơn bạn iu dấu đã chơi hết con game vô nghĩa này.
"""


def draw_polygon(surface, color, cx, cy, radius, sides, angle_offset=0, width=0):
    points = []
    for i in range(sides):
        angle = angle_offset + i * (2 * math.pi / sides)
        points.append((cx + radius*math.cos(angle), cy + radius*math.sin(angle)))
    if len(points) >= 3:
        pygame.draw.polygon(surface, color, points, width)


def draw_glow(surface, cx, cy, radius, color):
    glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        alpha = int((1 - r/radius) * 150)
        pygame.draw.circle(glow, (*color[:3], alpha), (radius, radius), r)
    surface.blit(glow, (cx - radius, cy - radius), special_flags=pygame.BLEND_RGB_ADD)

def draw_entity_shape(surface, name, cx, cy, angle=0):
    # === THÁP HẮC QUỐC (tông tối: tím, đen, obsidian) ===
    if name == "Ballista":
        draw_polygon(surface, (100,60,140), cx, cy, 17, 8, angle, width=2)
        draw_polygon(surface, (40,10,60), cx, cy, 15, 8, angle)
    elif name == "Phalanx":
        pygame.draw.rect(surface, (80,60,120), (cx-10,cy-15,20,30), width=2)
        pygame.draw.rect(surface, (30,20,50), (cx-9,cy-14,18,28))
    elif name == "Ignis":
        draw_polygon(surface, (120,40,140), cx, cy+4, 17, 3, angle-math.pi/2, width=2)
        draw_polygon(surface, (140,50,180), cx, cy+4, 15, 3, angle-math.pi/2)
    elif name == "Kronos":
        draw_polygon(surface, (80,40,120), cx, cy-8, 14, 3, angle+math.pi/2, width=2)
        draw_polygon(surface, (80,40,120), cx, cy+8, 14, 3, angle-math.pi/2, width=2)
        draw_polygon(surface, (60,0,100), cx, cy-8, 12, 3, angle+math.pi/2)
        draw_polygon(surface, (60,0,100), cx, cy+8, 12, 3, angle-math.pi/2)
    elif name == "Ares":
        draw_polygon(surface, (100,20,30), cx, cy, 19, 4, angle, width=2)
        draw_polygon(surface, (60,5,15), cx, cy, 17, 4, angle)
    elif name == "Hephaestus":
        pygame.draw.rect(surface, (120,50,10), (cx-15,cy-10,30,20), width=2)
        pygame.draw.rect(surface, (80,30,5), (cx-14,cy-9,28,18))
    elif name == "Thanatos":
        pygame.draw.circle(surface, (80,0,120), (cx,cy), 20, width=2)
        pygame.draw.circle(surface, (20,0,30), (cx,cy), 18)
        pygame.draw.circle(surface, (120,0,180), (cx,cy), 6)
    # === QUÂN BẠCH QUỐC (các tông màu sáng rực rỡ, dễ phân biệt) ===
    elif name == "Lurker":
        # Màu xanh lá sáng
        draw_polygon(surface, (80, 220, 80), cx, cy, 14, 3, angle, width=2)
        draw_polygon(surface, (150, 255, 150), cx, cy, 12, 3, angle)
    elif name == "Drifter":
        # Màu vàng chanh
        draw_polygon(surface, (200, 200, 50), cx, cy, 16, 4, angle, width=2)
        draw_polygon(surface, (255, 255, 120), cx, cy, 14, 4, angle)
    elif name == "Brute":
        # Màu xanh dương sáng
        pygame.draw.rect(surface, (50, 150, 240), (cx-15,cy-15,30,30), width=2)
        pygame.draw.rect(surface, (130, 200, 255), (cx-14,cy-14,28,28))
    elif name == "Phantom":
        # Màu hồng tím neon
        pygame.draw.circle(surface, (200, 80, 220), (cx,cy), 10, width=2)
        pygame.draw.circle(surface, (255, 160, 255), (cx,cy), 8)
    elif name == "Ravager":
        # Màu cam sáng
        draw_polygon(surface, (220, 100, 30), cx, cy, 18, 5, angle, width=2)
        draw_polygon(surface, (255, 170, 80), cx, cy, 16, 5, angle)
    elif name == "Titan":
        # Màu đỏ thẫm viền vàng kim
        draw_polygon(surface, (255, 215, 0), cx, cy, 26, 6, angle, width=2)
        draw_polygon(surface, (230, 40, 40), cx, cy, 24, 6, angle)


def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines, current_line = [], []
    for word in words:
        current_line.append(word)
        fw, _ = font.size(' '.join(current_line))
        if fw > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines


class FloatingText:
    def __init__(self, x, y, text, color, duration=1.0):
        self.x, self.y = float(x), float(y)
        self.text, self.color = text, color
        self.life, self.max_life = duration, duration

    def update(self, dt):
        self.life -= dt
        self.y -= 20 * dt

    def draw(self, surface, font):
        alpha = max(0, int((self.life / self.max_life) * 255))
        if alpha <= 0:
            return
        surf = font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        surface.blit(surf, (int(self.x), int(self.y)))


class Bullet:
    def __init__(self, start_pos, target, tw_type):
        self.x, self.y = float(start_pos[0]), float(start_pos[1])
        self.target = target
        self.tw_type = tw_type
        speeds = {"Ballista": 800, "Ignis": 500, "Ares": 2500, "Hephaestus": 400}
        self.speed = float(speeds.get(tw_type, 700))
        self.reached = False

    def update(self, dt):
        if not self.target or not getattr(self.target, 'alive', False):
            self.reached = True
            return
        tx, ty = self.target.pixel_pos
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist <= self.speed * dt:
            self.reached = True
        else:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def draw(self, screen):
        ix, iy = int(self.x), int(self.y)
        colors = {"Ballista": (100, 60, 140), "Ignis": (140, 50, 180),
                  "Ares": (100, 20, 30), "Hephaestus": (120, 50, 10)}
        c = colors.get(self.tw_type, (80, 0, 120))
        r = 8 if self.tw_type == "Hephaestus" else 5
        pygame.draw.circle(screen, c, (ix, iy), r)
        if self.tw_type in ("Ignis", "Ares"):
            draw_glow(screen, ix, iy, r * 3, c)


class GameEngine:
    def toggle_fullscreen(self):
        self.is_fullscreen = not getattr(self, 'is_fullscreen', False)
        if self.is_fullscreen:
            try:
                self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF)
            except:
                try:
                    self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
                except:
                    self.is_fullscreen = False
        else:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF)

    def play_click(self):
        if getattr(self, 'click_sfx', None) and not self.is_muted:
            self.click_sfx.play()

    def preprocess_sound_icons(self):
        self.mute_icon = None
        self.unmute_icon = None
        try:
            if os.path.exists("assets/ui/mute.png") and os.path.exists("assets/ui/unmute.png"):
                mute_src = pygame.image.load("assets/ui/mute.png").convert_alpha()
                unmute_src = pygame.image.load("assets/ui/unmute.png").convert_alpha()
                
                # Process mute icon (black on white -> white on transparent)
                mw, mh = mute_src.get_size()
                m_surf = pygame.Surface((mw, mh), pygame.SRCALPHA)
                for x in range(mw):
                    for y in range(mh):
                        r, g, b, a = mute_src.get_at((x, y))
                        brightness = (r + g + b) // 3
                        if brightness < 220:
                            alpha = 255 - brightness
                            m_surf.set_at((x, y), (240, 240, 240, alpha))
                self.mute_icon = pygame.transform.smoothscale(m_surf, (32, 32))
                
                # Process unmute icon
                uw, uh = unmute_src.get_size()
                u_surf = pygame.Surface((uw, uh), pygame.SRCALPHA)
                for x in range(uw):
                    for y in range(uh):
                        r, g, b, a = unmute_src.get_at((x, y))
                        brightness = (r + g + b) // 3
                        if brightness < 220:
                            alpha = 255 - brightness
                            u_surf.set_at((x, y), (240, 240, 240, alpha))
                self.unmute_icon = pygame.transform.smoothscale(u_surf, (32, 32))
        except Exception as e:
            print(f"Lỗi xử lý icon âm thanh: {e}")


    def draw_entity_icon(self, name, cx, cy):
        draw_entity_shape(self.screen, name, cx, cy, 0)

    def get_poster(self, name):
        if not hasattr(self, 'posters'):
            self.posters = {}
        if name not in self.posters:
            loaded = False
            p_names = [f"{name}_poster", name, name.lower(), f"{name.lower()}_poster"]
            if name == "Lurker": p_names += ["luker", "luker_poster", "Luker", "Luker_poster"]
            if name == "Thanatos": p_names += ["thatanos", "thatanos_poster", "Thatanos", "Thatanos_poster"]
            for p_name in p_names:
                for ext in ["png", "jpg", "jpeg", "PNG", "JPG"]:
                    path = f"assets/characters/{p_name}.{ext}"
                    if os.path.exists(path):
                        try:
                            img = pygame.image.load(path).convert_alpha()
                            self.posters[name] = pygame.transform.scale(img, (300, 300))
                            loaded = True
                            break
                        except: pass
                if loaded: break
            if not loaded:
                import glob
                search_patterns = [f"assets/characters/*{name}*.*", f"assets/characters/*{name.lower()}*.*"]
                if name == "Lurker": search_patterns += ["assets/characters/*luker*.*", "assets/characters/*Luker*.*"]
                if name == "Thanatos": search_patterns += ["assets/characters/*thatanos*.*", "assets/characters/*Thatanos*.*"]
                for pat in search_patterns:
                    for f in glob.glob(pat):
                        try:
                            img = pygame.image.load(f).convert_alpha()
                            self.posters[name] = pygame.transform.scale(img, (300, 300))
                            loaded = True
                            break
                        except: pass
                    if loaded: break
            if not loaded:
                self.posters[name] = None
        return self.posters[name]

    def start_menu_music(self):
        try:
            pygame.mixer.music.load("assets/audio/bgm.mp3")
            pygame.mixer.music.play(-1, fade_ms=1500)
            pygame.mixer.music.set_volume(0 if getattr(self, 'is_muted', False) else 0.5)
        except:
            pass

    def start_ending_music(self):
        try:
            pygame.mixer.music.load("assets/audio/song2.mp3")
            pygame.mixer.music.play(-1, fade_ms=1500)
            pygame.mixer.music.set_volume(0 if getattr(self, 'is_muted', False) else 0.5)
        except:
            pass

    def start_outro_music(self):
        try:
            # Try to load and play outro.mp3
            pygame.mixer.music.load("assets/audio/outro.mp3")
            pygame.mixer.music.play(-1, fade_ms=1500)
            pygame.mixer.music.set_volume(0 if getattr(self, 'is_muted', False) else 0.5)
        except:
            # Fallback to song2.mp3 if outro.mp3 is not present
            try:
                pygame.mixer.music.load("assets/audio/song2.mp3")
                pygame.mixer.music.play(-1, fade_ms=1500)
                pygame.mixer.music.set_volume(0 if getattr(self, 'is_muted', False) else 0.5)
            except:
                pass

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Hắc Quốc Thủ Thành")
        
        # Set Window Icon
        try:
            if os.path.exists("assets/ui/icon.png"):
                icon_img = pygame.image.load("assets/ui/icon.png").convert_alpha()
            else:
                icon_img = pygame.image.load("assets/ui/heart.png").convert_alpha()
            pygame.display.set_icon(icon_img)
        except:
            pass
        
        self.has_cv2 = False
        try:
            import cv2
            self.has_cv2 = True
        except:
            pass
        
        self.logo_cap = None
        self.intro_cap = None

        if self.has_cv2:
            import cv2
            if os.path.exists("assets/video/logo.mp4"): self.logo_cap = cv2.VideoCapture("assets/video/logo.mp4")
            if os.path.exists("assets/video/intro.mp4"): self.intro_cap = cv2.VideoCapture("assets/video/intro.mp4")

        self.delay_timer = 60  # Đợi 2 giây (60 frames) trước khi chiếu logo
        if self.logo_cap and self.logo_cap.isOpened():
            self.state = "START_DELAY"
            self.fade_alpha = 255
        elif self.intro_cap and self.intro_cap.isOpened():
            self.state = "START_DELAY"
            self.fade_alpha = 255
        else:
            self.state = "MENU"
            self.start_menu_music()
            self.menu_anim_y = 0
            self.menu_fade_alpha = 0

        try:
            self.menu_bg = pygame.image.load(BG_IMAGE_PATH).convert()
            self.menu_bg = pygame.transform.scale(self.menu_bg, (SCREEN_W, SCREEN_H))
        except:
            self.menu_bg = None

        try:
            if os.path.exists("assets/backgrounds/settings_bg.png"):
                self.settings_bg = pygame.image.load("assets/backgrounds/settings_bg.png").convert()
                self.settings_bg = pygame.transform.scale(self.settings_bg, (SCREEN_W, SCREEN_H))
            else:
                self.settings_bg = None
        except:
            self.settings_bg = None
            
        # Load level backgrounds
        self.level_bgs = {}
        for i in range(1, 11):
            try:
                bg = pygame.image.load(f"assets/backgrounds/level_{i}_bg.png").convert()
                self.level_bgs[i] = pygame.transform.scale(bg, (GRID_COLS * CELL_SIZE, SCREEN_H))
            except:
                self.level_bgs[i] = None
                
        # Start background music is now handled by start_menu_music()
            
        try:
            self.map_bg = pygame.image.load("assets/backgrounds/map_bg.png").convert()
            self.map_bg = pygame.transform.scale(self.map_bg, (SCREEN_W, SCREEN_H))
        except:
            self.map_bg = None
            
        self.posters = {}
        for name in ENCYCLOPEDIA_DATA.keys():
            self.get_poster(name)
            
        self.show_guide_popup = False

        # Load outro background
        try:
            if os.path.exists("assets/backgrounds/outro_bg.png"):
                self.outro_bg = pygame.image.load("assets/backgrounds/outro_bg.png").convert()
                self.outro_bg = pygame.transform.scale(self.outro_bg, (SCREEN_W, SCREEN_H))
            else:
                self.outro_bg = None
        except:
            self.outro_bg = None

        # Load in-game currency icon (heart.png)
        try:
            self.heart_img = pygame.image.load("assets/ui/heart.png").convert_alpha()
            self.heart_sidebar_icon = pygame.transform.smoothscale(self.heart_img, (24, 24))
            self.heart_card_icon = pygame.transform.smoothscale(self.heart_img, (16, 16))
        except Exception as e:
            print(f"Error loading heart.png: {e}")
            self.heart_img = None
            self.heart_sidebar_icon = None
            self.heart_card_icon = None
                
        # --- Load loading cat ---
        self.loading_cat_frames = []
        self.loading_cat_angle = 0.0
        self.loading_cat_gif_idx = 0
        self.loading_dot_count = 0
        self.loading_dot_tick = 0
        # Thử load GIF frame bằng PIL, fallback về static PNG
        _cat_loaded = False
        try:
            from PIL import Image, ImageSequence
            _gif = Image.open("assets/ui/loading_cat.gif")
            for _f in ImageSequence.Iterator(_gif):
                _fc = _f.convert("RGBA").resize((280, 280))
                _s = pygame.image.fromstring(_fc.tobytes(), _fc.size, "RGBA")
                self.loading_cat_frames.append(_s)
            _cat_loaded = True
        except: pass
        if not _cat_loaded:
            for _name in ["assets/ui/loading_cat.gif", "assets/ui/loading_cat.png"]:
                try:
                    _s = pygame.image.load(_name).convert_alpha()
                    _s = pygame.transform.scale(_s, (280, 280))
                    self.loading_cat_frames = [_s]
                    break
                except: pass

        self.warning_text = ""
        self.warning_timer = 0

        self.clock = pygame.time.Clock()
        self.fonts = {
            'xs': pygame.font.SysFont("Segoe UI", 13),
            'sm': pygame.font.SysFont("Segoe UI", 16, bold=True),
            'md': pygame.font.SysFont("Segoe UI", 20),
            'lg': pygame.font.SysFont("Segoe UI", 32, bold=True),
            'xl': pygame.font.SysFont("Segoe UI", 48, bold=True)
        }
        # Ghi nhớ state video đã chọn (LOGO/INTRO/MENU) để khôi phục sau khi font load xong
        _saved_state = self.state
        
        self.prev_state = "MENU"
        self.dict_selected = "Lurker"
        self.is_muted = False
        try:
            self.click_sfx = pygame.mixer.Sound("assets/audio/click.wav")
            self.click_sfx.set_volume(0.6)
        except:
            self.click_sfx = None
        self.current_level = 1
        self.unlocked_level, self.has_selected_faction, self.has_seen_intro, self.has_beaten_game = load_progress()
        self.ending_unlocked_by_code = False
        self.settings_prompt_password = False
        self.setting_password_input = ""
        self.vua_den = None
        self.vua_trang = None
        for ext in ["png", "jpg", "jpeg", "PNG", "JPG"]:
            try:
                path = f"assets/characters/vua_den.{ext}"
                if os.path.exists(path):
                    self.vua_den = pygame.image.load(path).convert_alpha()
                    self.vua_den = pygame.transform.scale(self.vua_den, (250, 250))
                    break
            except:
                pass
        for ext in ["png", "jpg", "jpeg", "PNG", "JPG"]:
            try:
                path = f"assets/characters/vua_trang.{ext}"
                if os.path.exists(path):
                    self.vua_trang = pygame.image.load(path).convert_alpha()
                    self.vua_trang = pygame.transform.scale(self.vua_trang, (250, 250))
                    break
            except:
                pass

        self.preprocess_sound_icons()
        self.reset_game(1)
        
        # Khôi phục state video (tránh bị reset_game/mặc định ghi đè)
        self.state = _saved_state

    def reset_game(self, level=1):
        self.grid = [[0]*GRID_COLS for _ in range(GRID_ROWS)]
        self.grid[SPAWN_POS[0]][SPAWN_POS[1]] = -1
        self.grid[BASE_POS[0]][BASE_POS[1]] = -1
        
        # Inject predefined obstacles for this level
        for r, c in OBSTACLES_BY_LEVEL.get(level, []):
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                self.grid[r][c] = 2
                
        self.monsters = LinkedList()
        self.towers = []
        self.base = Base(BASE_POS, max_hp=20)
        self.gold = 100 + (level - 1) * 30
        self.current_level = level
        self.wave_queue = Queue()
        self.spawn_timer = 0.0
        self.wave_active = False
        self.selected_tower_name = "Ballista"
        self.dragged_tower_type = None
        self.selected_entity_on_map = None
        self.range_show = []  # [(tower_ref, timer_remaining), ...]
        self.bullets = []
        self.phalanx_spikes = []
        self.floating_texts = []
        for m in WAVES_BY_LEVEL.get(level, []):
            self.wave_queue.enqueue(m)

    def spawn_monster(self):
        if not self.wave_queue.is_empty():
            m_type = self.wave_queue.dequeue()
            m_class = MONSTER_REGISTRY.get(m_type)
            if m_class:
                m_obj = m_class(SPAWN_POS, BASE_POS)
                m_obj.pixel_pos = [
                    SPAWN_POS[1] * CELL_SIZE + CELL_SIZE // 2,
                    SPAWN_POS[0] * CELL_SIZE + CELL_SIZE // 2
                ]
                m_obj.grid_ref = self.grid
                
                # Scatter logic: stronger monsters wander more waypoints before pathing
                # Scatter count by type: Lurker=2, Drifter=2, Brute=3, Phantom=4, Ravager=5, Titan=6
                _scatter_counts = {'Lurker':2,'Drifter':2,'Brute':3,'Phantom':4,'Ravager':5,'Titan':6}
                _scatter_n = _scatter_counts.get(m_type, 2)
                # Expand search radius for stronger monsters
                _scatter_radius = {1:5, 2:6, 3:8, 4:10, 5:12, 6:15}.get(_scatter_n, 8)
                valid_scatters = []
                for r in range(max(0, SPAWN_POS[0]-_scatter_radius), min(GRID_ROWS, SPAWN_POS[0]+_scatter_radius+1)):
                    for c in range(max(0, SPAWN_POS[1]-1), min(GRID_COLS, SPAWN_POS[1]+_scatter_radius+2)):
                        if self.grid[r][c] == 0:
                            valid_scatters.append((r, c))

                m_obj.path = []
                if valid_scatters and _scatter_n > 0:
                    # Build multi-waypoint scatter path
                    combined_path = []
                    cur = SPAWN_POS
                    chosen = random.sample(valid_scatters, min(_scatter_n, len(valid_scatters)))
                    for wp in chosen:
                        seg = bfs_find_path(self.grid, cur, wp)
                        if seg:
                            combined_path.extend(seg)
                            cur = wp
                    if combined_path:
                        m_obj.scatter_target = cur
                        m_obj.path = combined_path

                if not m_obj.path:
                    m_obj.is_scattering = False
                    m_obj.path = bfs_find_path(self.grid, SPAWN_POS, BASE_POS)
                    
                m_obj.path_index = 0
                self.monsters.append(m_obj)
    # ---------------------------------------------------------------- FACTION & SETTINGS
    def draw_intro_story(self):
        self.screen.fill(C_MENU_BG)
        
        idx = getattr(self, 'intro_story_index', 0)
        img_rect = pygame.Rect(SCREEN_W//2 - 420, 25, 840, 270)
        
        if not hasattr(self, 'story_images'):
            self.story_images = {}
            
        if idx not in self.story_images:
            loaded = False
            for ext in ["jpg", "png", "jpeg", "PNG", "JPG"]:
                path = f"assets/story/story_{idx+1}.{ext}"
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        self.story_images[idx] = pygame.transform.scale(img, (840, 270))
                        loaded = True
                        break
                    except:
                        pass
            if not loaded:
                self.story_images[idx] = None
                
        if self.story_images[idx] is not None:
            self.screen.blit(self.story_images[idx], img_rect.topleft)
            pygame.draw.rect(self.screen, (200, 200, 200), img_rect, width=2)
        else:
            pygame.draw.rect(self.screen, (30, 40, 50), img_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), img_rect, width=2)
            txt = self.fonts['md'].render(f"Ảnh minh họa đoạn {idx+1} (Chèn sau)", True, (150, 150, 150))
            self.screen.blit(txt, (img_rect.x + img_rect.w//2 - txt.get_width()//2, img_rect.y + img_rect.h//2 - txt.get_height()//2))

        # Text container box (larger height to prevent overflow)
        text_rect = pygame.Rect(SCREEN_W//2 - 420, 315, 840, 240)
        
        # Translucent glassmorphism-like background
        bg_surface = pygame.Surface((text_rect.w, text_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 25, 38, 245), (0, 0, text_rect.w, text_rect.h), border_radius=12)
        self.screen.blit(bg_surface, text_rect.topleft)
        pygame.draw.rect(self.screen, (100, 80, 180), text_rect, width=2, border_radius=12)
        
        # Section progress indicator
        prog_txt = f"ĐOẠN {idx+1} / {len(INTRO_STORY_TEXTS)}"
        prog_lbl = self.fonts['sm'].render(prog_txt, True, (150, 140, 200))
        self.screen.blit(prog_lbl, (text_rect.right - prog_lbl.get_width() - 20, text_rect.y + 15))
        
        # Title of the story section
        title_lbl = self.fonts['md'].render("HẮC QUỐC KHÁNG CHIẾN LORE", True, (255, 215, 0))
        self.screen.blit(title_lbl, (text_rect.x + 20, text_rect.y + 15))
        
        # Render wrapped text
        text = INTRO_STORY_TEXTS[idx]
        y = text_rect.y + 50
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                y += 10
                continue
            lines = wrap_text(paragraph, self.fonts['md'], 800)
            for ln in lines:
                s = self.fonts['md'].render(ln, True, (255, 255, 255))
                # Add text shadow for enhanced readability and contrast
                shadow = self.fonts['md'].render(ln, True, (0, 0, 0))
                self.screen.blit(shadow, (text_rect.x + 21, y + 1))
                self.screen.blit(s, (text_rect.x + 20, y))
                y += 24

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        # Buttons layout
        # Skip/Thoát Button (Only if previewed from settings)
        if getattr(self, 'intro_from_settings', False):
            skip_btn = pygame.Rect(SCREEN_W//2 - 420, 575, 140, 44)
            is_hover_s = skip_btn.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (140,50,50) if is_hover_s else (100,35,35), skip_btn, border_radius=8)
            pygame.draw.rect(self.screen, (200,100,100) if is_hover_s else (150,70,70), skip_btn, width=2, border_radius=8)
            lbl_s = self.fonts['md'].render("THOÁT", True, (255,255,255))
            self.screen.blit(lbl_s, (skip_btn.x + skip_btn.w//2 - lbl_s.get_width()//2, skip_btn.y + 8))
            if click and is_hover_s:
                self.play_click()
                self.state = "SETTINGS"
                pygame.time.delay(200)

        # Back Button (Quay lại)
        if idx > 0:
            back_btn = pygame.Rect(SCREEN_W//2 + 120, 575, 140, 44)
            is_hover_b = back_btn.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (50,70,100) if is_hover_b else (35,50,75), back_btn, border_radius=8)
            pygame.draw.rect(self.screen, (100,140,200) if is_hover_b else (70,100,150), back_btn, width=2, border_radius=8)
            lbl_b = self.fonts['md'].render("QUAY LẠI", True, (220,230,255))
            self.screen.blit(lbl_b, (back_btn.x + back_btn.w//2 - lbl_b.get_width()//2, back_btn.y + 8))
            if click and is_hover_b:
                self.play_click()
                self.story_button_cooldown = 3.0
                self.intro_story_index -= 1
                pygame.time.delay(200)

        # Update Cooldown
        dt = min(self.clock.get_time() / 1000.0, 0.05)
        self.story_button_cooldown = max(0.0, getattr(self, 'story_button_cooldown', 0.0) - dt)

        # Next Button (Tiếp theo / Bắt đầu)
        is_last = (idx == len(INTRO_STORY_TEXTS) - 1)
        btn_label = "BẮT ĐẦU" if is_last else "TIẾP THEO"
        next_btn = pygame.Rect(SCREEN_W//2 + 280, 575, 140, 44)
        
        cd = getattr(self, 'story_button_cooldown', 0.0)
        is_disabled = (cd > 0.0)
        
        if is_disabled:
            btn_label = f"{btn_label} ({int(math.ceil(cd))}s)"
            pygame.draw.rect(self.screen, (80, 80, 80), next_btn, border_radius=8)
            pygame.draw.rect(self.screen, (120, 120, 120), next_btn, width=2, border_radius=8)
            is_hover_n = False
        else:
            is_hover_n = next_btn.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (50,120,70) if is_hover_n else (35,90,50), next_btn, border_radius=8)
            pygame.draw.rect(self.screen, (100,220,130) if is_hover_n else (70,160,100), next_btn, width=2, border_radius=8)
            
        lbl_n = self.fonts['md'].render(btn_label, True, (150,150,150) if is_disabled else (255,255,255))
        self.screen.blit(lbl_n, (next_btn.x + next_btn.w//2 - lbl_n.get_width()//2, next_btn.y + 8))
        
        if click and is_hover_n and not is_disabled:
            self.play_click()
            self.story_button_cooldown = 3.0
            if is_last:
                if not getattr(self, 'has_seen_intro', False):
                    self.has_seen_intro = True
                    save_progress(self.unlocked_level, getattr(self, 'has_selected_faction', False), self.has_seen_intro, getattr(self, 'has_beaten_game', False))
                self.state = "LEVEL_SELECT" if not getattr(self, 'intro_from_settings', False) else "SETTINGS"
            else:
                self.intro_story_index += 1
            pygame.time.delay(200)

    def draw_final_story(self):
        self.screen.fill(C_MENU_BG)
        
        # Add a gorgeous cinematic top title
        title = self.fonts['xl'].render("KẾT THÚC CHIẾN DỊCH", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 35))
        
        idx = getattr(self, 'final_story_index', 0)
        
        # Image container and dimensions: exactly 16:9 ratio (560 x 315)
        img_rect = pygame.Rect(60, 147, 560, 315)
        
        if not hasattr(self, 'final_story_images'):
            self.final_story_images = {}
            
        if idx not in self.final_story_images:
            loaded = False
            for ext in ["png", "PNG"]:
                path = f"assets/story/final_story_{idx+1}.{ext}"
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        self.final_story_images[idx] = pygame.transform.scale(img, (560, 315))
                        loaded = True
                        break
                    except:
                        pass
            if not loaded:
                self.final_story_images[idx] = None
                
        # Draw Left Side Column (Image Box)
        # Translucent glassmorphic container for the image column
        img_container = pygame.Rect(50, 110, 580, 390)
        img_container_bg = pygame.Surface((img_container.w, img_container.h), pygame.SRCALPHA)
        img_container_bg.fill((20, 25, 38, 160))
        self.screen.blit(img_container_bg, img_container.topleft)
        pygame.draw.rect(self.screen, (100, 100, 120), img_container, width=1, border_radius=12)
        
        if self.final_story_images[idx] is not None:
            self.screen.blit(self.final_story_images[idx], img_rect.topleft)
            pygame.draw.rect(self.screen, (200, 180, 50), img_rect, width=2, border_radius=8)
        else:
            pygame.draw.rect(self.screen, (30, 40, 50), img_rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 100, 100), img_rect, width=2, border_radius=8)
            txt = self.fonts['md'].render(f"Ảnh kết thúc {idx+1} (16:9)", True, (150, 150, 150))
            self.screen.blit(txt, (img_rect.x + img_rect.w//2 - txt.get_width()//2, img_rect.y + img_rect.h//2 - txt.get_height()//2))

        # Draw Right Side Column (Narrative Text scroll box)
        text_rect = pygame.Rect(650, 110, 560, 390)
        
        bg_surface = pygame.Surface((text_rect.w, text_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 25, 38, 245), (0, 0, text_rect.w, text_rect.h), border_radius=12)
        self.screen.blit(bg_surface, text_rect.topleft)
        pygame.draw.rect(self.screen, (200, 180, 50), text_rect, width=2, border_radius=12)
        
        prog_txt = f"ĐOẠN {idx+1} / {len(FINAL_STORY_TEXTS)}"
        prog_lbl = self.fonts['sm'].render(prog_txt, True, (200, 200, 150))
        self.screen.blit(prog_lbl, (text_rect.right - prog_lbl.get_width() - 25, text_rect.y + 20))
        
        title_lbl = self.fonts['md'].render("HẮC QUỐC TRƯỜNG TỒN", True, (255, 255, 0))
        self.screen.blit(title_lbl, (text_rect.x + 25, text_rect.y + 20))
        
        text = FINAL_STORY_TEXTS[idx]
        y = text_rect.y + 70
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                y += 10
                continue
            # Wrapped with width 510 to fit cleanly inside the 560px container
            lines = wrap_text(paragraph, self.fonts['md'], 510)
            for ln in lines:
                s = self.fonts['md'].render(ln, True, (255, 255, 255))
                shadow = self.fonts['md'].render(ln, True, (0, 0, 0))
                self.screen.blit(shadow, (text_rect.x + 26, y + 1))
                self.screen.blit(s, (text_rect.x + 25, y))
                y += 26

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        # Navigation Buttons (Flanking the columns)
        if idx > 0:
            back_btn = pygame.Rect(650, 520, 160, 46)
            is_hover_b = back_btn.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (100,70,50) if is_hover_b else (75,50,35), back_btn, border_radius=8)
            pygame.draw.rect(self.screen, (200,140,100) if is_hover_b else (150,100,70), back_btn, width=2, border_radius=8)
            lbl_b = self.fonts['md'].render("QUAY LẠI", True, (255,230,220))
            self.screen.blit(lbl_b, (back_btn.x + back_btn.w//2 - lbl_b.get_width()//2, back_btn.y + 9))
            if click and is_hover_b:
                self.play_click()
                self.story_button_cooldown = 3.0
                self.final_story_index -= 1
                pygame.time.delay(200)

        # Update Cooldown
        dt = min(self.clock.get_time() / 1000.0, 0.05)
        self.story_button_cooldown = max(0.0, getattr(self, 'story_button_cooldown', 0.0) - dt)

        is_last = (idx == len(FINAL_STORY_TEXTS) - 1)
        btn_label = "XEM OUTRO" if is_last else "TIẾP THEO"
        next_btn = pygame.Rect(1050, 520, 160, 46)
        
        cd = getattr(self, 'story_button_cooldown', 0.0)
        is_disabled = (cd > 0.0)
        
        if is_disabled:
            btn_label = f"{btn_label} ({int(math.ceil(cd))}s)"
            pygame.draw.rect(self.screen, (80, 80, 80), next_btn, border_radius=8)
            pygame.draw.rect(self.screen, (120, 120, 120), next_btn, width=2, border_radius=8)
            is_hover_n = False
        else:
            is_hover_n = next_btn.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (120,100,50) if is_hover_n else (90,70,35), next_btn, border_radius=8)
            pygame.draw.rect(self.screen, (220,200,100) if is_hover_n else (160,140,70), next_btn, width=2, border_radius=8)
            
        lbl_n = self.fonts['md'].render(btn_label, True, (150,150,150) if is_disabled else (255,255,255))
        self.screen.blit(lbl_n, (next_btn.x + next_btn.w//2 - lbl_n.get_width()//2, next_btn.y + 9))
        
        if click and is_hover_n and not is_disabled:
            self.play_click()
            self.story_button_cooldown = 3.0
            if is_last:
                self.state = "OUTRO"
                self.outro_scroll_y = SCREEN_H
                self.outro_skippable = getattr(self, 'final_from_settings', False)
                self.start_outro_music()
            else:
                self.final_story_index += 1
            pygame.time.delay(200)

    def draw_faction_select(self):
        self.screen.fill(C_MENU_BG)
        title = self.fonts['xl'].render("CHỌN MÀU DA CHO PHE CỦA BẠN", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 50))
        
        balance = self.fonts['lg'].render("SỐ DƯ: 99$", True, (100, 255, 100))
        self.screen.blit(balance, (SCREEN_W - balance.get_width() - 20, 20))
        
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        # Phe Da Đen
        black_rect = pygame.Rect(SCREEN_W//2 - 350, 180, 300, 420)
        is_hover_b = black_rect.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (50, 50, 50) if is_hover_b else (30, 30, 30), black_rect, border_radius=15)
        pygame.draw.rect(self.screen, (150, 150, 150), black_rect, width=3, border_radius=15)
        
        img_rect_b = pygame.Rect(black_rect.x + 25, black_rect.y + 25, 250, 250)
        if getattr(self, 'vua_den', None):
            self.screen.blit(self.vua_den, img_rect_b.topleft)
        else:
            pygame.draw.rect(self.screen, (10, 10, 10), img_rect_b)
            txt_b = self.fonts['sm'].render("Hình Vua Hắc Quốc (Chèn sau)", True, (100, 100, 100))
            self.screen.blit(txt_b, (img_rect_b.x + img_rect_b.w//2 - txt_b.get_width()//2, img_rect_b.y + 115))
        
        lbl_b = self.fonts['xl'].render("Da Đen", True, (200, 200, 200))
        self.screen.blit(lbl_b, (black_rect.x + black_rect.w//2 - lbl_b.get_width()//2, black_rect.y + 300))
        price_b = self.fonts['lg'].render("80$", True, (255, 215, 0))
        self.screen.blit(price_b, (black_rect.x + black_rect.w//2 - price_b.get_width()//2, black_rect.y + 350))
        
        # Phe Da Trắng
        white_rect = pygame.Rect(SCREEN_W//2 + 50, 180, 300, 420)
        is_hover_w = white_rect.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (220, 220, 220) if is_hover_w else (200, 200, 200), white_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 100), white_rect, width=3, border_radius=15)
        
        img_rect_w = pygame.Rect(white_rect.x + 25, white_rect.y + 25, 250, 250)
        if getattr(self, 'vua_trang', None):
            self.screen.blit(self.vua_trang, img_rect_w.topleft)
        else:
            pygame.draw.rect(self.screen, (255, 255, 255), img_rect_w)
            txt_w = self.fonts['sm'].render("Hình Vua Bạch Quốc (Chèn sau)", True, (150, 150, 150))
            self.screen.blit(txt_w, (img_rect_w.x + img_rect_w.w//2 - txt_w.get_width()//2, img_rect_w.y + 115))
        
        lbl_w = self.fonts['xl'].render("Da Trắng", True, (40, 40, 40))
        self.screen.blit(lbl_w, (white_rect.x + white_rect.w//2 - lbl_w.get_width()//2, white_rect.y + 300))
        price_w = self.fonts['lg'].render("100$", True, (255, 50, 50))
        self.screen.blit(price_w, (white_rect.x + white_rect.w//2 - price_w.get_width()//2, white_rect.y + 350))
        
        if click:
            if is_hover_b:
                self.play_click()
                self.has_selected_faction = True
                save_progress(self.unlocked_level, self.has_selected_faction, getattr(self, 'has_seen_intro', False), getattr(self, 'has_beaten_game', False))
                if not getattr(self, 'has_seen_intro', False):
                    self.intro_story_index = 0
                    self.intro_from_settings = False
                    self.state = "INTRO_STORY"
                else:
                    self.state = "LEVEL_SELECT"
                pygame.time.delay(200)
            elif is_hover_w:
                self.play_click()
                self.warning_text = "Rấc tiếc bạn không đủ đô để làm da trắng."
                self.warning_timer = 180
                pygame.time.delay(200)
                
        if getattr(self, 'warning_timer', 0) > 0:
            warn = self.fonts['md'].render(self.warning_text, True, (255, 100, 100))
            self.screen.blit(warn, (SCREEN_W//2 - warn.get_width()//2, 615))
            self.warning_timer -= 1
            
        back = pygame.Rect(18, 18, 100, 38)
        pygame.draw.rect(self.screen, (70,70,90) if back.collidepoint(mx,my) else (45,45,65), back, border_radius=5)
        self.screen.blit(self.fonts['md'].render("TRỞ VỀ", True, C_TEXT), (back.x+14, back.y+8))
        if click and back.collidepoint(mx, my):
            self.play_click()
            self.state = "MENU"; pygame.time.delay(200)

    def draw_settings(self):
        # Draw background image dimmed
        if getattr(self, 'settings_bg', None):
            self.screen.blit(self.settings_bg, (0, 0))
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 185))  # Darken the background
            self.screen.blit(dim, (0, 0))
        elif self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 185))  # Darken the background
            self.screen.blit(dim, (0, 0))
        else:
            self.screen.fill(C_MENU_BG)
            
        title = self.fonts['xl'].render("CÀI ĐẶT", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 80))
        
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        is_ending_unlocked = getattr(self, 'has_beaten_game', False) or getattr(self, 'ending_unlocked_by_code', False)
        is_popup_active = getattr(self, 'settings_prompt_password', False)
        is_mid_game = getattr(self, 'settings_prev_state', 'MENU') == 'PAUSE'

        # --- Premium Mute Button next to Title ---
        vol_rect = pygame.Rect(SCREEN_W//2 + 210, 74, 52, 52)
        is_hover_vol = vol_rect.collidepoint(mx, my) and not is_popup_active
        if is_hover_vol:
            draw_glow(self.screen, vol_rect.centerx, vol_rect.centery, 32, (0, 230, 255))
        
        btn_color = (40, 50, 70) if is_hover_vol else (25, 28, 40)
        border_color = (0, 230, 255) if is_hover_vol else (100, 105, 120)
        pygame.draw.rect(self.screen, btn_color, vol_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, vol_rect, width=2, border_radius=12)
        
        if self.is_muted:
            if getattr(self, 'mute_icon', None):
                self.screen.blit(self.mute_icon, (vol_rect.x + 10, vol_rect.y + 10))
            else:
                lbl_vol = self.fonts['sm'].render("MUTE", True, (255, 100, 100))
                self.screen.blit(lbl_vol, (vol_rect.x + vol_rect.w//2 - lbl_vol.get_width()//2, vol_rect.y + vol_rect.h//2 - lbl_vol.get_height()//2))
        else:
            if getattr(self, 'unmute_icon', None):
                self.screen.blit(self.unmute_icon, (vol_rect.x + 10, vol_rect.y + 10))
            else:
                lbl_vol = self.fonts['sm'].render("VOL", True, (100, 255, 100))
                self.screen.blit(lbl_vol, (vol_rect.x + vol_rect.w//2 - lbl_vol.get_width()//2, vol_rect.y + vol_rect.h//2 - lbl_vol.get_height()//2))
                
        if click and is_hover_vol:
            if getattr(self, 'settings_mute_cooldown', 0) <= 0:
                self.play_click()
                self.is_muted = not self.is_muted
                pygame.mixer.music.set_volume(0 if self.is_muted else 0.5)
                self.settings_mute_cooldown = 15
                pygame.time.delay(150)
                
        if getattr(self, 'settings_mute_cooldown', 0) > 0:
            self.settings_mute_cooldown -= 1

        # --- Menu Options Buttons list ---
        btns = [
            (pygame.Rect(SCREEN_W//2-190, 145, 380, 44), "PHÁT LẠI CỐT TRUYỆN", (60,160,100), "STORY"),
            (pygame.Rect(SCREEN_W//2-190, 199, 380, 44), "CHỌN LẠI MÀU DA", (60,100,160), "FACTION"),
            (pygame.Rect(SCREEN_W//2-190, 253, 380, 44), "XÓA TIẾN TRÌNH", (200,60,60), "RESET"),
            (pygame.Rect(SCREEN_W//2-190, 307, 380, 44), "XEM KẾT THÚC" if is_ending_unlocked else "XEM KẾT THÚC (KHOÁ)", (150,50,150) if is_ending_unlocked else (100,100,100), "ENDING"),
            (pygame.Rect(SCREEN_W//2-190, 361, 380, 44), "XEM OUTRO" if is_ending_unlocked else "XEM OUTRO (KHOÁ)", (180,50,120) if is_ending_unlocked else (100,100,100), "OUTRO_REPLAY"),
            (pygame.Rect(SCREEN_W//2-190, 415, 380, 44), "MỞ KHÓA TẤT CẢ MÀN" if is_ending_unlocked else "MỞ KHÓA TẤT CẢ MÀN (KHOÁ)", (190,140,40) if is_ending_unlocked else (100,100,100), "UNLOCK_ALL"),
            (pygame.Rect(SCREEN_W//2-190, 469, 380, 44), "HƯỚNG DẪN CHƠI", (0,150,180), "GUIDE"),
        ]
        
        for rect, label, c, action in btns:
            is_dev_btn = action in ["STORY", "FACTION", "RESET", "ENDING", "OUTRO_REPLAY", "UNLOCK_ALL"]
            is_disabled = is_mid_game and is_dev_btn
            
            if is_disabled:
                # Disabled color style
                btn_color = (35, 35, 38)
                border_color = (60, 60, 65)
                text_color = (110, 110, 115)
                disp_label = label + " (VÔ HIỆU KHI CHƠI)"
                is_hover = False
            else:
                btn_color = c
                border_color = (min(c[0]+30,255), min(c[1]+30,255), min(c[2]+30,255))
                text_color = (255, 255, 255)
                disp_label = label
                is_hover = rect.collidepoint(mx, my) and not is_popup_active
                
            draw_rect = rect.inflate(6, 6) if is_hover else rect
            pygame.draw.rect(self.screen, border_color if is_hover else btn_color, draw_rect, border_radius=10)
            if not is_hover:
                pygame.draw.rect(self.screen, border_color, draw_rect, width=1, border_radius=10)
                
            lbl = self.fonts['md'].render(disp_label, True, text_color)
            self.screen.blit(lbl, (draw_rect.x + draw_rect.w//2 - lbl.get_width()//2, draw_rect.y + 10))
            
            if click and is_hover and not is_popup_active and not is_disabled:
                self.play_click()
                if action == "STORY":
                    self.intro_story_index = 0
                    self.intro_from_settings = True
                    self.story_button_cooldown = 3.0  # Cooldown
                    self.state = "INTRO_STORY"
                elif action == "FACTION":
                    self.state = "FACTION_SELECT"
                elif action == "RESET":
                    self.unlocked_level = 1
                    self.has_selected_faction = False
                    self.has_seen_intro = False
                    self.has_beaten_game = False
                    self.ending_unlocked_by_code = False
                    save_progress(self.unlocked_level, self.has_selected_faction, self.has_seen_intro, False)
                    self.state = "MENU"
                elif action == "ENDING":
                    if is_ending_unlocked:
                        self.final_story_index = 0
                        self.final_from_settings = True
                        self.story_button_cooldown = 3.0  # Cooldown
                        self.state = "FINAL_STORY"
                        self.start_ending_music()
                    else:
                        self.settings_prompt_password = True
                        self.setting_password_input = ""
                elif action == "OUTRO_REPLAY":
                    if is_ending_unlocked:
                        self.state = "OUTRO"
                        self.outro_scroll_y = SCREEN_H
                        self.outro_skippable = True  # Replay is skippable
                        self.start_outro_music()
                    else:
                        self.settings_prompt_password = True
                        self.setting_password_input = ""
                elif action == "UNLOCK_ALL":
                    if is_ending_unlocked:
                        self.unlocked_level = 10
                        save_progress(10, self.has_selected_faction, self.has_seen_intro, self.has_beaten_game)
                        self.warning_text = "Đã mở khóa toàn bộ 10 màn chơi!"
                        self.warning_timer = 180
                    else:
                        self.settings_prompt_password = True
                        self.setting_password_input = ""
                elif action == "GUIDE":
                    self.show_guide_popup = True
                pygame.time.delay(200)
                
        # --- Back button in Settings ---
        back = pygame.Rect(18, 18, 100, 38)
        is_back_hover = back.collidepoint(mx, my) and not is_popup_active
        pygame.draw.rect(self.screen, (70,70,90) if is_back_hover else (45,45,65), back, border_radius=8)
        pygame.draw.rect(self.screen, (150,150,180) if is_back_hover else (80,85,105), back, width=1, border_radius=8)
        self.screen.blit(self.fonts['md'].render("TRỞ VỀ", True, C_TEXT), (back.x+14, back.y+8))
        if click and is_back_hover and not is_popup_active:
            self.play_click()
            prev_s = getattr(self, 'settings_prev_state', "MENU")
            self.state = prev_s
            pygame.time.delay(200)

        # Draw lock note if ending/outro/all levels are locked
        if not is_ending_unlocked:
            lbl_note = self.fonts['sm'].render("(*) Người chơi phá đảo game để truy cập tính năng này", True, (220, 120, 120))
            self.screen.blit(lbl_note, (SCREEN_W//2 - lbl_note.get_width()//2, 525))

        # Warning/Info Text display
        if getattr(self, 'warning_timer', 0) > 0:
            warn = self.fonts['md'].render(getattr(self, 'warning_text', ''), True, (255, 100, 100))
            self.screen.blit(warn, (SCREEN_W//2 - warn.get_width()//2, 555))
            self.warning_timer -= 1

        # Render Password Input Popup
        if is_popup_active:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 220))
            self.screen.blit(overlay, (0,0))
            
            box_w, box_h = 500, 250
            box_rect = pygame.Rect(SCREEN_W//2 - box_w//2, SCREEN_H//2 - box_h//2, box_w, box_h)
            pygame.draw.rect(self.screen, (22, 25, 35), box_rect, border_radius=12)
            pygame.draw.rect(self.screen, (150, 50, 150), box_rect, width=3, border_radius=12)
            
            lbl_title = self.fonts['lg'].render("CẦN PHÁ ĐẢO HOẶC MẬT MÃ", True, (255, 255, 255))
            self.screen.blit(lbl_title, (SCREEN_W//2 - lbl_title.get_width()//2, box_rect.y + 20))
            
            lbl_sub = self.fonts['md'].render("Nhập mã nhà phát triển để mở khóa:", True, (180, 180, 200))
            self.screen.blit(lbl_sub, (SCREEN_W//2 - lbl_sub.get_width()//2, box_rect.y + 60))
            
            input_box = pygame.Rect(SCREEN_W//2 - 150, box_rect.y + 100, 300, 45)
            pygame.draw.rect(self.screen, (15, 18, 25), input_box, border_radius=8)
            pygame.draw.rect(self.screen, (200, 180, 50), input_box, width=2, border_radius=8)
            
            bullet_str = "*" * len(self.setting_password_input) if self.setting_password_input else "Nhập số..."
            bullet_color = (255, 255, 50) if self.setting_password_input else (100, 100, 110)
            lbl_pw = self.fonts['lg'].render(bullet_str, True, bullet_color)
            self.screen.blit(lbl_pw, (SCREEN_W//2 - lbl_pw.get_width()//2, input_box.y + 4))
            
            lbl_note = self.fonts['xs'].render("Người chơi phá đảo game để truy cập tính năng này", True, (220, 120, 120))
            self.screen.blit(lbl_note, (SCREEN_W//2 - lbl_note.get_width()//2, box_rect.y + 160))
            
            lbl_hint = self.fonts['xs'].render("Ấn ENTER để xác nhận | ESC để hủy", True, (130, 130, 150))
            self.screen.blit(lbl_hint, (SCREEN_W//2 - lbl_hint.get_width()//2, box_rect.y + 205))

        # Draw lock note if ending/outro/all levels are locked
        if not is_ending_unlocked:
            lbl_note = self.fonts['sm'].render("(*) Người chơi phá đảo game để truy cập tính năng này", True, (220, 120, 120))
            self.screen.blit(lbl_note, (SCREEN_W//2 - lbl_note.get_width()//2, 525))

        # Warning/Info Text display
        if getattr(self, 'warning_timer', 0) > 0:
            warn = self.fonts['md'].render(getattr(self, 'warning_text', ''), True, (255, 100, 100))
            self.screen.blit(warn, (SCREEN_W//2 - warn.get_width()//2, 555))
            self.warning_timer -= 1

        # Render Password Input Popup
        if is_popup_active:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 220))
            self.screen.blit(overlay, (0,0))
            
            box_w, box_h = 500, 250
            box_rect = pygame.Rect(SCREEN_W//2 - box_w//2, SCREEN_H//2 - box_h//2, box_w, box_h)
            pygame.draw.rect(self.screen, (22, 25, 35), box_rect, border_radius=12)
            pygame.draw.rect(self.screen, (150, 50, 150), box_rect, width=3, border_radius=12)
            
            lbl_title = self.fonts['lg'].render("CẦN PHÁ ĐẢO HOẶC MẬT MÃ", True, (255, 255, 255))
            self.screen.blit(lbl_title, (SCREEN_W//2 - lbl_title.get_width()//2, box_rect.y + 20))
            
            lbl_sub = self.fonts['md'].render("Nhập mã nhà phát triển để mở khóa:", True, (180, 180, 200))
            self.screen.blit(lbl_sub, (SCREEN_W//2 - lbl_sub.get_width()//2, box_rect.y + 60))
            
            input_box = pygame.Rect(SCREEN_W//2 - 150, box_rect.y + 100, 300, 45)
            pygame.draw.rect(self.screen, (15, 18, 25), input_box, border_radius=8)
            pygame.draw.rect(self.screen, (200, 180, 50), input_box, width=2, border_radius=8)
            
            bullet_str = "*" * len(self.setting_password_input) if self.setting_password_input else "Nhập số..."
            bullet_color = (255, 255, 50) if self.setting_password_input else (100, 100, 110)
            lbl_pw = self.fonts['lg'].render(bullet_str, True, bullet_color)
            self.screen.blit(lbl_pw, (SCREEN_W//2 - lbl_pw.get_width()//2, input_box.y + 4))
            
            lbl_note = self.fonts['xs'].render("Người chơi phá đảo game để truy cập tính năng này", True, (220, 120, 120))
            self.screen.blit(lbl_note, (SCREEN_W//2 - lbl_note.get_width()//2, box_rect.y + 160))
            
            lbl_hint = self.fonts['xs'].render("Ấn ENTER để xác nhận | ESC để hủy", True, (130, 130, 150))
            self.screen.blit(lbl_hint, (SCREEN_W//2 - lbl_hint.get_width()//2, box_rect.y + 205))

    # ---------------------------------------------------------------- MENU
    
    def draw_outro(self):
        # 1. Draw background (with dimming overlay)
        if getattr(self, 'outro_bg', None):
            self.screen.blit(self.outro_bg, (0, 0))
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 140))  # Dark overlay for better text readability, set to 140 to make it brighter
            self.screen.blit(dim, (0, 0))
        elif self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 140))
            self.screen.blit(dim, (0, 0))
        else:
            self.screen.fill((10, 10, 15))

        # 2. Draw scrolling text
        lines = OUTRO_TEXT.strip().split('\n')
        line_height = 34
        start_y = getattr(self, 'outro_scroll_y', SCREEN_H)
        
        y = start_y
        for line in lines:
            line_str = line.strip()
            # Render only if visible on screen
            if -50 <= y <= SCREEN_H + 50:
                if not line_str:
                    pass
                elif line_str.startswith("==="):
                    lbl = self.fonts['md'].render(line_str, True, (255, 100, 180)) # Pink themed dividers
                    self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, y))
                elif line_str.startswith("---"):
                    lbl = self.fonts['lg'].render(line_str, True, (255, 215, 0))   # Gold headers
                    self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, y))
                elif line_str.startswith("*"):
                    lbl = self.fonts['xs'].render(line_str, True, (150, 150, 150)) # Small grey joke text
                    self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, y))
                elif "Nguyễn Thành Thiện Nhân" in line_str or "25521290" in line_str or "bersious." in line_str:
                    lbl = self.fonts['md'].render(line_str, True, (0, 230, 255))   # Cyan author highlight
                    self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, y))
                elif "Cảm ơn bạn iu dấu đã chơi hết con game vô nghĩa này" in line_str:
                    lbl = self.fonts['lg'].render(line_str, True, (255, 80, 150))  # Special thank you
                    self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, y))
                else:
                    lbl = self.fonts['md'].render(line_str, True, (240, 240, 240)) # Off-white text
                    self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, y))
            y += line_height

        # 3. Update scroll position slowly (0.8 px/frame)
        self.outro_scroll_y = getattr(self, 'outro_scroll_y', SCREEN_H) - 0.8
        
        # 4. Check if finished
        total_height = len(lines) * line_height
        if self.outro_scroll_y < -total_height:
            self.state = "MENU"
            self.start_menu_music()

        # 5. Skip button (if skippable)
        if getattr(self, 'outro_skippable', False):
            mx, my = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()[0]
            skip_btn = pygame.Rect(SCREEN_W - 160, 20, 140, 38)
            is_hover = skip_btn.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (100, 35, 35) if is_hover else (70, 25, 25), skip_btn, border_radius=6)
            pygame.draw.rect(self.screen, (180, 70, 70) if is_hover else (120, 45, 45), skip_btn, width=1, border_radius=6)
            lbl = self.fonts['xs'].render("BỎ QUA (ESC)", True, (255, 255, 255))
            self.screen.blit(lbl, (skip_btn.x + skip_btn.w//2 - lbl.get_width()//2, skip_btn.y + 10))
            if click and is_hover:
                self.play_click()
                self.state = "MENU"
                self.start_menu_music()

    def draw_guide_popup(self):
        if not getattr(self, 'show_guide_popup', False):
            return
            
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        # 1. Dark background overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        self.screen.blit(overlay, (0, 0))
        
        # 2. Main Dialog Box
        dialog_w, dialog_h = 780, 520
        dialog_x = SCREEN_W // 2 - dialog_w // 2
        dialog_y = SCREEN_H // 2 - dialog_h // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        # Draw translucent glassmorphic backdrop
        pygame.draw.rect(self.screen, (22, 25, 35), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (0, 230, 255), dialog_rect, width=2, border_radius=15)
        
        # Title
        title_lbl = self.fonts['lg'].render("HƯỚNG DẪN CHƠI CƠ BẢN", True, (0, 230, 255))
        self.screen.blit(title_lbl, (SCREEN_W//2 - title_lbl.get_width()//2, dialog_y + 15))
        
        # Line dividers
        pygame.draw.line(self.screen, (80, 80, 110), (dialog_x + 30, dialog_y + 55), (dialog_x + dialog_w - 30, dialog_y + 55), 1)
        
        # Draw vertical divider line in the middle
        pygame.draw.line(self.screen, (60, 60, 80), (SCREEN_W // 2, dialog_y + 70), (SCREEN_W // 2, dialog_y + dialog_h - 70), 1)
        
        col1_x = dialog_x + 30
        col2_x = SCREEN_W // 2 + 25
        col_w = 330
        
        left_items = [
            ("⚡ ĐẶT THÁP PHÒNG THỦ", "Chọn tháp từ danh sách ở chân màn hình, rồi click vào ô đất trống trên bản đồ để xây dựng.", (0, 230, 255)),
            ("❤️ TIỀN TỆ (TIM CRYSTAL)", "Tim dùng để mua/nâng cấp tháp. Tiêu diệt quái vật để thu thập thêm Tim.", (255, 100, 100)),
            ("🧠 PATHFINDING ĐƯỜNG ĐI", "Quái vật tự tìm đường ngắn nhất bằng BFS. Bạn không thể đặt tháp chặn hoàn toàn đường đi.", (100, 255, 100)),
            ("⬆️ NÂNG CẤP / BÁN THÁP", "Click chuột vào tháp đã xây để mở bảng menu tùy chọn Nâng cấp (tăng chỉ số) hoặc Bán tháp.", (255, 200, 50)),
            ("🏹 VÒNG TRÒN TẦM BẮN", "Rà chuột lên tháp để hiển thị vòng tầm bắn chuột. Tháp tự động bắn quái thông minh.", (180, 150, 255))
        ]
        
        right_items = [
            ("🏹 BALLISTA (THÁP TÊN)", "Sát thương đơn mục tiêu ổn định, tầm bắn trung bình, chi phí nâng cấp cực rẻ.", (240, 240, 240)),
            ("🔥 IGNIS (THÁP LỬA)", "Phun lửa gây sát thương diện rộng (AOE) cực mạnh lên nhóm quái đi sát nhau.", (255, 120, 50)),
            ("🗡️ ARES (THÁP KIẾM)", "Gây lượng sát thương vật lý khổng lồ, tầm siêu xa nhưng tốc độ bắn rất chậm.", (200, 80, 255)),
            ("💎 HEPHAESTUS (THÁP ĐẬP)", "Đặc biệt! Tăng đáng kể lượng Tim nhận được khi tiêu diệt quái vật gần tháp.", (255, 215, 0))
        ]
        
        def draw_wrapped_item(x, y, title, desc, title_color):
            # Render title
            lbl_title = self.fonts['sm'].render(title, True, title_color)
            self.screen.blit(lbl_title, (x, y))
            curr_y = y + 20
            
            # Wrap description text to col_w
            words = desc.split(' ')
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                if self.fonts['xs'].size(test_line)[0] > col_w:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
                
            # Draw wrapped lines
            for line in lines:
                lbl_line = self.fonts['xs'].render(line, True, (190, 190, 200))
                self.screen.blit(lbl_line, (x + 8, curr_y))
                curr_y += 16
            return curr_y
            
        # Draw Left Column
        y1 = dialog_y + 70
        for title, desc, color in left_items:
            y1 = draw_wrapped_item(col1_x, y1, title, desc, color) + 12
            
        # Draw Right Column
        y2 = dialog_y + 70
        lbl_col2_title = self.fonts['md'].render("📌 HỆ THỐNG THÁP PHÒNG THỦ", True, (255, 215, 0))
        self.screen.blit(lbl_col2_title, (col2_x, y2))
        y2 += 30
        
        for title, desc, color in right_items:
            y2 = draw_wrapped_item(col2_x, y2, title, desc, color) + 12
            
        # Close Button
        close_btn = pygame.Rect(SCREEN_W//2 - 60, dialog_y + dialog_h - 52, 120, 34)
        is_hover = close_btn.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (0, 160, 200) if is_hover else (0, 120, 150), close_btn, border_radius=8)
        pygame.draw.rect(self.screen, (0, 230, 255) if is_hover else (0, 180, 210), close_btn, width=1, border_radius=8)
        lbl_c = self.fonts['md'].render("ĐÓNG", True, (255, 255, 255))
        self.screen.blit(lbl_c, (close_btn.x + close_btn.w//2 - lbl_c.get_width()//2, close_btn.y + 6))
        
        if click and is_hover:
            self.play_click()
            self.show_guide_popup = False
            pygame.time.delay(200)

    def draw_menu(self):
        if getattr(self, 'menu_anim_y', 0) > 0:
            self.menu_anim_y -= 3
            if self.menu_anim_y < 0: self.menu_anim_y = 0
            
        offset_y = getattr(self, 'menu_anim_y', 0)

        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill(C_MENU_BG)
        
        # Caution warning badge at top-left (extremely visible & premium)
        caution_text = "Caution: Game 13+, nhiều cảnh bạo lực, dark."
        lbl = self.fonts['sm'].render(caution_text, True, (255, 110, 110))
        badge_w = lbl.get_width() + 20
        badge_h = lbl.get_height() + 10
        badge_rect = pygame.Rect(20, 20, badge_w, badge_h)
        bg_surface = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180)) # Semi-transparent black
        self.screen.blit(bg_surface, (20, 20))
        pygame.draw.rect(self.screen, (220, 45, 45), badge_rect, width=1, border_radius=5)
        self.screen.blit(lbl, (20 + 10, 20 + 5))
        
        # Dời dòng chữ bản quyền xuống góc dưới bên phải, size nhỏ
        sub = self.fonts['xs'].render("Hắc Quốc Thủ Thành — DSA Project @UIT 2026", True, (100, 110, 120))
        self.screen.blit(sub, (SCREEN_W - sub.get_width() - 10, SCREEN_H - sub.get_height() - 10))

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        # Moved buttons down by 180 pixels to avoid overlapping the central logo
        btns = [
            (pygame.Rect(SCREEN_W//2-180, 380 + offset_y, 360, 54), "BẮT ĐẦU CHIẾN DỊCH", (30,120,60), (50,200,100), "SELECT"),
            (pygame.Rect(SCREEN_W//2-180, 444 + offset_y, 360, 54), "TỪ ĐIỂN DỮ LIỆU",    (30, 60,120), (60,120,240),"DICT"),
            (pygame.Rect(SCREEN_W//2-180, 508 + offset_y, 360, 54), "CÀI ĐẶT",            (120,80, 30), (200,140,60), "SETTINGS"),
            (pygame.Rect(SCREEN_W//2-180, 572 + offset_y, 360, 54), "THOÁT TRÒ CHƠI",     (120,40, 40), (200,60,60), "QUIT"),
        ]
        for rect, label, cn, ch, action in btns:
            is_hover = rect.collidepoint(mx, my)
            draw_rect = rect.inflate(10, 10) if is_hover else rect
            pygame.draw.rect(self.screen, ch if is_hover else cn, draw_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 200, 50) if is_hover else (150, 150, 150), draw_rect, width=3, border_radius=8)
            lbl = self.fonts['lg'].render(label, True, (255,255,255))
            self.screen.blit(lbl, (draw_rect.x + draw_rect.w//2 - lbl.get_width()//2, draw_rect.y + 10))
            if click and is_hover:
                self.play_click()
                self.screen.fill((255,255,255))
                pygame.display.flip()
                pygame.time.delay(100)
                if action == "QUIT":  pygame.quit(); sys.exit()
                if action == "DICT":  self.state = "DICT"; self.prev_state = "MENU"; pygame.time.delay(200)
                if action == "SETTINGS":
                    self.settings_prev_state = "MENU"
                    self.state = "SETTINGS"
                    pygame.time.delay(200)
                if action == "SELECT": 
                    if not getattr(self, 'has_selected_faction', False):
                        self.state = "FACTION_SELECT"
                    elif not getattr(self, 'has_seen_intro', False):
                        self.intro_story_index = 0
                        self.intro_from_settings = False
                        self.story_button_cooldown = 3.0
                        self.state = "INTRO_STORY"
                    else:
                        self.state = "LEVEL_SELECT"
                    pygame.time.delay(200)

        # Fade-in: giảm alpha mỗi frame rồi vẽ overlay đè lên tất cả
        fa = getattr(self, 'menu_fade_alpha', 0)
        if fa > 0:
            self.menu_fade_alpha = max(0, fa - 3)
            dark = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dark.fill((0, 0, 0, fa))
            self.screen.blit(dark, (0, 0))

    def draw_level_select(self):
        if getattr(self, 'map_bg', None):
            self.screen.blit(self.map_bg, (0, 0))
        else:
            self.screen.fill(C_MENU_BG)
            
        # Draw a beautiful dimmed backdrop over map_bg to increase contrast
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 100))
        self.screen.blit(dim, (0, 0))

        title = self.fonts['xl'].render("CHỌN LEVEL", True, (255, 255, 255))
        # Add nice drop shadow to title
        title_shadow = self.fonts['xl'].render("CHỌN LEVEL", True, (0, 0, 0))
        self.screen.blit(title_shadow, (SCREEN_W//2 - title_shadow.get_width()//2 + 2, 52))
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 50))
        
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        for i in range(1, 11):
            x = 240 + ((i-1)%5)*200
            y = 200 + ((i-1)//5)*150
            
            rect = pygame.Rect(x-40, y-40, 80, 80)
            is_unlocked = i <= self.unlocked_level
            is_hover = rect.collidepoint(mx, my)
            draw_rect = rect.inflate(12, 12) if is_hover else rect # Inflate slightly more for better premium pop-out effect
            
            # 1. Draw glowing effect behind the cell on hover
            if is_hover:
                glow_color = (80, 220, 100) if is_unlocked else (220, 60, 60)
                draw_glow(self.screen, x, y, 65, glow_color)
            
            # 2. Draw base background under the thumbnail
            pygame.draw.rect(self.screen, (20, 22, 30), draw_rect, border_radius=15)
            
            # 3. Draw rounded thumbnail
            if self.level_bgs.get(i):
                # Scale thumbnail to match cell size
                thumb_scaled = pygame.transform.scale(self.level_bgs[i], draw_rect.size)
                
                # Mask corners to make it rounded
                temp_surf = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(temp_surf, (255, 255, 255, 255), (0, 0, draw_rect.w, draw_rect.h), border_radius=15)
                temp_surf.blit(thumb_scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                
                # Apply dark overlay over thumbnail if locked
                if not is_unlocked:
                    dark_overlay = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 200)) # Darken locked level thumbnail
                    temp_surf.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                
                self.screen.blit(temp_surf, draw_rect.topleft)
            else:
                # Fallback if no level background image is found
                fallback_color = (30, 80, 45) if is_unlocked else (40, 40, 40)
                pygame.draw.rect(self.screen, fallback_color, draw_rect, border_radius=15)

            # 4. Draw beautiful premium borders
            if is_unlocked:
                border_color = (255, 215, 0) if is_hover else (140, 180, 255)
            else:
                border_color = (220, 60, 60) if is_hover else (60, 65, 80)
            
            border_width = 3 if is_hover else 2
            pygame.draw.rect(self.screen, border_color, draw_rect, width=border_width, border_radius=15)
            
            # 5. Draw cell content (Number or Lock)
            if is_unlocked:
                lbl = self.fonts['xl'].render(str(i), True, (255, 255, 255))
                shadow = self.fonts['xl'].render(str(i), True, (0, 0, 0))
                self.screen.blit(shadow, (x - shadow.get_width()//2 + 2, y - shadow.get_height()//2 + 2))
                self.screen.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))
                
                # Gamification: Show a shining gold star if this level is completed/beaten!
                is_beaten = i < self.unlocked_level or (i == 10 and getattr(self, 'has_beaten_game', False))
                if is_beaten:
                    star_lbl = self.fonts['md'].render("⭐", True, (255, 215, 0))
                    # Draw a tiny glow behind the star
                    draw_glow(self.screen, draw_rect.right - 12, draw_rect.y + 12, 16, (255, 215, 0))
                    self.screen.blit(star_lbl, (draw_rect.right - 22, draw_rect.y + 2))
            else:
                # Elegant locked look
                lbl = self.fonts['lg'].render("🔒", True, (240, 240, 240))
                self.screen.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))
            
            # Handle level selection click
            if click and is_hover:
                if is_unlocked:
                    self.play_click()
                    self.screen.fill((255,255,255))
                    pygame.display.flip()
                    pygame.time.delay(100)
                    self.reset_game(i)
                    self.state = "STORY"
                    pygame.time.delay(200)
                else:
                    self.warning_text = "Vui lòng hoàn thành màn chơi trước đó!"
                    self.warning_timer = 120
                    
        if getattr(self, 'warning_timer', 0) > 0:
            warn = self.fonts['lg'].render(self.warning_text, True, (255, 50, 50))
            # Text shadow for warning message
            warn_shadow = self.fonts['lg'].render(self.warning_text, True, (0, 0, 0))
            self.screen.blit(warn_shadow, (SCREEN_W//2 - warn_shadow.get_width()//2 + 2, SCREEN_H - 98))
            self.screen.blit(warn, (SCREEN_W//2 - warn.get_width()//2, SCREEN_H - 100))
            self.warning_timer -= 1
                
        # Back Button (Trở về)
        back = pygame.Rect(18, 18, 100, 38)
        is_back_hover = back.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (70,70,90) if is_back_hover else (45,45,65), back, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 180) if is_back_hover else (80, 85, 105), back, width=1, border_radius=8)
        self.screen.blit(self.fonts['md'].render("TRỞ VỀ", True, C_TEXT), (back.x+14, back.y+8))
        if click and is_back_hover:
            self.play_click()
            self.state = "MENU"; pygame.time.delay(200)
            
        # Gameplay Guide Button in Level Select (top-right corner)
        guide_btn = pygame.Rect(SCREEN_W - 160, 18, 140, 38)
        is_guide_hover = guide_btn.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (0, 150, 180) if is_guide_hover else (0, 100, 120), guide_btn, border_radius=8)
        pygame.draw.rect(self.screen, (0, 230, 255) if is_guide_hover else (0, 180, 210), guide_btn, width=1, border_radius=8)
        lbl_g = self.fonts['md'].render("HƯỚNG DẪN", True, (255, 255, 255))
        self.screen.blit(lbl_g, (guide_btn.x + guide_btn.w//2 - lbl_g.get_width()//2, guide_btn.y + 8))
        if click and is_guide_hover:
            self.play_click()
            self.show_guide_popup = True
            pygame.time.delay(200)

    # --------------------------------------------------------------- STORY
    def get_new_elements_for_level(self, level):
        if level == 1:
            new_monsters = set(WAVES_BY_LEVEL[1])
            new_towers = set(TOWERS_BY_LEVEL[1])
        else:
            prev_monsters = set()
            for l in range(1, level):
                prev_monsters.update(WAVES_BY_LEVEL.get(l, []))
            curr_monsters = set(WAVES_BY_LEVEL.get(level, []))
            new_monsters = curr_monsters - prev_monsters
            
            prev_towers = set()
            for l in range(1, level):
                prev_towers.update(TOWERS_BY_LEVEL.get(l, []))
            curr_towers = set(TOWERS_BY_LEVEL.get(level, []))
            new_towers = curr_towers - prev_towers
        return list(new_monsters), list(new_towers)

    def draw_story(self):
        self.screen.fill(C_MENU_BG)
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        # Draw a beautiful, unified Title banner at the top
        hdr = self.fonts['xl'].render(
            f"NHẬT KÝ CHIẾN DỊCH  —  CỬA ẢI {self.current_level}", True, (255, 215, 0))
        # Title drop shadow
        shadow_hdr = self.fonts['xl'].render(
            f"NHẬT KÝ CHIẾN DỊCH  —  CỬA ẢI {self.current_level}", True, (0, 0, 0))
        self.screen.blit(shadow_hdr, (SCREEN_W//2 - shadow_hdr.get_width()//2 + 2, 42))
        self.screen.blit(hdr, (SCREEN_W//2 - hdr.get_width()//2, 40))

        # ------------------------------------------------------------ LEFT COLUMN: LORE
        left_rect = pygame.Rect(60, 110, 540, 430)
        # Translucent glassmorphic panel
        bg_left = pygame.Surface((left_rect.w, left_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(bg_left, (25, 20, 35, 240), (0, 0, left_rect.w, left_rect.h), border_radius=16)
        self.screen.blit(bg_left, left_rect.topleft)
        pygame.draw.rect(self.screen, (120, 60, 220), left_rect, width=2, border_radius=16)

        # Lore panel title
        title_l = self.fonts['lg'].render("TIỂU THUYẾT CHIẾN TRẬN", True, (255, 215, 0))
        self.screen.blit(title_l, (left_rect.x + 25, left_rect.y + 20))
        
        # Left aligned lore text with wrapping
        story = CAMPAIGN_STORY.get(self.current_level, "Chuẩn bị chiến đấu!")
        story_lines = wrap_text(story, self.fonts['md'], 490)
        sy = left_rect.y + 70
        for ln in story_lines:
            s_lbl = self.fonts['md'].render(ln, True, (240, 245, 255))
            shadow = self.fonts['md'].render(ln, True, (0, 0, 0))
            self.screen.blit(shadow, (left_rect.x + 26, sy + 1))
            self.screen.blit(s_lbl, (left_rect.x + 25, sy))
            sy += 26

        # ------------------------------------------------------------ RIGHT COLUMN: NEW ENTITIES
        right_rect = pygame.Rect(660, 110, 540, 430)
        # Translucent glassmorphic panel
        bg_right = pygame.Surface((right_rect.w, right_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(bg_right, (18, 22, 35, 240), (0, 0, right_rect.w, right_rect.h), border_radius=16)
        self.screen.blit(bg_right, right_rect.topleft)
        pygame.draw.rect(self.screen, (0, 180, 255), right_rect, width=2, border_radius=16)

        # Entities panel title
        title_r = self.fonts['lg'].render("THỰC THỂ MỚI XUẤT HIỆN", True, (0, 230, 255))
        self.screen.blit(title_r, (right_rect.x + 25, right_rect.y + 20))

        new_monsters, new_towers = self.get_new_elements_for_level(self.current_level)
        all_new = [(m, "monster") for m in new_monsters] + [(t, "tower") for t in new_towers]
        
        if all_new:
            ey = right_rect.y + 70
            for item, item_type in all_new:
                info = ENCYCLOPEDIA_DATA.get(item, {})
                card_rect = pygame.Rect(right_rect.x + 20, ey, 500, 56)
                
                # Dynamic card and border colors depending on type
                card_bg = (40, 30, 50) if item_type == "monster" else (30, 40, 55)
                card_border = (220, 80, 80) if item_type == "monster" else (80, 160, 240)
                
                pygame.draw.rect(self.screen, card_bg, card_rect, border_radius=8)
                pygame.draw.rect(self.screen, card_border, card_rect, width=1, border_radius=8)
                
                # Draw entity visual icon
                self.draw_entity_icon(item, card_rect.x + 30, card_rect.y + 28)
                
                # Render Name
                name_color = (255, 180, 180) if item_type == "monster" else (180, 220, 255)
                n_lbl = self.fonts['md'].render(info.get('name', item), True, name_color)
                self.screen.blit(n_lbl, (card_rect.x + 70, card_rect.y + 8))
                
                # Render Compact Stats
                st_lbl = self.fonts['xs'].render(info.get('stats', ""), True, (170, 170, 185))
                self.screen.blit(st_lbl, (card_rect.x + 70, card_rect.y + 32))
                
                # Detail Button
                btn = pygame.Rect(card_rect.x + 360, card_rect.y + 13, 120, 30)
                is_hover = btn.collidepoint(mx, my)
                btn_c = (120, 50, 50) if item_type == "monster" else (40, 90, 150)
                if is_hover:
                    btn_c = (160, 70, 70) if item_type == "monster" else (60, 120, 200)
                
                pygame.draw.rect(self.screen, btn_c, btn, border_radius=5)
                b_lbl = self.fonts['xs'].render("XEM CHI TIẾT", True, (255, 255, 255))
                self.screen.blit(b_lbl, (btn.x + btn.w//2 - b_lbl.get_width()//2, btn.y + 6))
                
                if click and is_hover:
                    self.play_click()
                    self.dict_selected = item
                    self.prev_state = "STORY"
                    self.state = "DICT"
                    pygame.time.delay(200)
                
                ey += 66
        else:
            # Decorative flavor text when no new items appear
            flavor_text = "Chiến địa quen thuộc, không có quân địch\nhoặc vũ khí mới xuất hiện. Nữ hoàng hãy\ntập trung chỉ huy tối ưu lực lượng sẵn có!"
            f_y = right_rect.y + 140
            for line in flavor_text.split('\n'):
                f_lbl = self.fonts['md'].render(line, True, (140, 150, 170))
                self.screen.blit(f_lbl, (right_rect.x + right_rect.w//2 - f_lbl.get_width()//2, f_y))
                f_y += 32

        # ------------------------------------------------------------ BOTTOM CONTROLS
        # Back Button to Level Select
        back_btn = pygame.Rect(60, 565, 150, 48)
        is_hover_back = back_btn.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (70, 70, 90) if is_hover_back else (45, 45, 65), back_btn, border_radius=8)
        pygame.draw.rect(self.screen, (150, 150, 180) if is_hover_back else (100, 100, 120), back_btn, width=2, border_radius=8)
        lbl_b = self.fonts['md'].render("QUAY LẠI", True, (220, 230, 255))
        self.screen.blit(lbl_b, (back_btn.x + back_btn.w//2 - lbl_b.get_width()//2, back_btn.y + 11))
        
        if click and is_hover_back:
            self.play_click()
            self.state = "LEVEL_SELECT"
            pygame.time.delay(200)

        # Into Battle Button
        btn_start = pygame.Rect(SCREEN_W//2 - 120, 560, 240, 56)
        is_hover_start = btn_start.collidepoint(mx, my)
        c_btn = (50, 180, 90) if is_hover_start else (30, 140, 65)
        draw_btn = btn_start.inflate(10, 6) if is_hover_start else btn_start
        pygame.draw.rect(self.screen, c_btn, draw_btn, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), draw_btn, width=2, border_radius=12)
        
        lbl_s = self.fonts['lg'].render("VÀO TRẬN", True, (255, 255, 255))
        self.screen.blit(lbl_s, (draw_btn.x + draw_btn.w//2 - lbl_s.get_width()//2, draw_btn.y + 12))

        if click and is_hover_start:
            self.play_click()
            self.wave_active = True
            self.start_cat_loading("GAME")
            pygame.time.delay(150)

    # ---------------------------------------------------------------- DICT
    def draw_dict(self):
        self.screen.fill(C_MENU_BG)
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        back = pygame.Rect(18, 18, 100, 38)
        pygame.draw.rect(self.screen,
                         (70,70,90) if back.collidepoint(mx,my) else (45,45,65), back, border_radius=5)
        self.screen.blit(self.fonts['md'].render("TRỞ VỀ", True, C_TEXT), (back.x+14, back.y+8))
        if click and back.collidepoint(mx, my):
            self.play_click()
            next_state = getattr(self, 'prev_state', "MENU")
            self.state = next_state
            self.prev_state = "MENU"
            # If returning to game, dismiss inspect popup so game resumes
            if next_state == "GAME":
                self.selected_entity_on_map = None
            pygame.time.delay(200)


        pygame.draw.rect(self.screen, (25, 28, 40), (18, 70, 254, SCREEN_H-88), border_radius=12)
        pygame.draw.rect(self.screen, (60, 65, 85), (18, 70, 254, SCREEN_H-88), width=2, border_radius=12)
        y = 90
        for section_name, section_color, items in [
            ("QUÂN BẠCH QUỐC", (255,100,100), ["Lurker","Drifter","Brute","Phantom","Ravager","Titan"]),
            ("VŨ KHÍ HẮC QUỐC",   (100,180,255), ["Ballista","Phalanx","Ignis","Kronos","Ares","Hephaestus","Thanatos"]),
        ]:
            self.screen.blit(self.fonts['sm'].render(section_name, True, section_color), (30, y)); y+=28
            for name in items:
                r = pygame.Rect(26, y, 236, 30)
                sel = (name == self.dict_selected)
                bg = (60, 100, 160) if sel else ((50, 60, 80) if r.collidepoint(mx,my) else (30, 35, 50))
                pygame.draw.rect(self.screen, bg, r, border_radius=6)
                if sel: pygame.draw.rect(self.screen, (100, 200, 255), r, width=2, border_radius=6)
                self.screen.blit(self.fonts['sm'].render(name, True, (255,255,255) if sel else (180,180,180)), (38, y+5))
                if click and r.collidepoint(mx, my): 
                    self.play_click()
                    self.dict_selected = name
                    if hasattr(self, 'posters') and name in self.posters and self.posters[name] is None:
                        del self.posters[name]
                    pygame.time.delay(140)
                y += 34
            y += 14

        d = ENCYCLOPEDIA_DATA.get(self.dict_selected)
        if d:
            px = 288
            box_rect = pygame.Rect(px, 70, SCREEN_W-px-18, SCREEN_H-88)
            pygame.draw.rect(self.screen, (25, 28, 40), box_rect, border_radius=12)
            pygame.draw.rect(self.screen, (60, 65, 85), box_rect, width=2, border_radius=12)
            
            name = self.dict_selected
            
            if not hasattr(self, 'posters'):
                self.posters = {}
                
            # Use shared poster loader (no duplicate code)
            poster = self.get_poster(name)
            
            poster_rect = pygame.Rect(px+30, 100, 300, 300)
            pygame.draw.rect(self.screen, (15, 18, 25), poster_rect, border_radius=10)
            
            if poster:
                self.screen.blit(poster, (px+30, 100))
            else:
                s1 = self.fonts['sm'].render("CHƯA CÓ POSTER", True, (100, 100, 100))
                s2 = self.fonts['sm'].render(f"File mẫu: {name}.png", True, (80, 80, 80))
                self.screen.blit(s1, (poster_rect.x + 150 - s1.get_width()//2, poster_rect.y + 130))
                self.screen.blit(s2, (poster_rect.x + 150 - s2.get_width()//2, poster_rect.y + 160))
                
            rx = px + 360
            self.screen.blit(self.fonts['xl'].render(d['name'], True, (255, 220, 100)), (rx, 90))
            
            # ── Unlock level badge ───────────────────────────────────
            # Build tower_unlock_lv lookup: {tower_name: first level it appears}
            tower_unlock_lv = {}
            for lv in sorted(TOWERS_BY_LEVEL.keys()):
                for t in TOWERS_BY_LEVEL[lv]:
                    if t not in tower_unlock_lv:
                        tower_unlock_lv[t] = lv
            # Build monster_unlock_lv lookup: {monster_name: first level it appears in a wave}
            monster_unlock_lv = {}
            for lv in sorted(WAVES_BY_LEVEL.keys()):
                for m in WAVES_BY_LEVEL[lv]:
                    if m not in monster_unlock_lv:
                        monster_unlock_lv[m] = lv
            unlock_lv = tower_unlock_lv.get(name) or monster_unlock_lv.get(name)
            if unlock_lv:
                badge_txt = f"🔓 Xuất hiện từ Level {unlock_lv}"
                badge_col = (80, 220, 140)
            else:
                badge_txt = "🔓 Level 1"
                badge_col = (80, 200, 120)
            badge_surf = self.fonts['sm'].render(badge_txt, True, badge_col)
            badge_bg = pygame.Rect(rx, 138, badge_surf.get_width() + 20, 28)
            pygame.draw.rect(self.screen, (20, 50, 30), badge_bg, border_radius=5)
            pygame.draw.rect(self.screen, badge_col, badge_bg, width=1, border_radius=5)
            self.screen.blit(badge_surf, (badge_bg.x + 10, badge_bg.y + 5))
            # ──────────────────────────────────────────────────────────
            
            stats_bg = pygame.Rect(rx, 180, box_rect.w - 390, 40)
            pygame.draw.rect(self.screen, (40, 45, 60), stats_bg, border_radius=6)
            self.screen.blit(self.fonts['sm'].render(d['stats'], True, (150, 255, 150)), (rx+15, 190))
            
            self.screen.blit(self.fonts['lg'].render("TIỂU SỬ", True, (180, 180, 200)), (rx, 240))
            lore_lines = wrap_text(d['lore'], self.fonts['md'], box_rect.w - 390)
            ly = 280
            for ln in lore_lines:
                self.screen.blit(self.fonts['md'].render(ln, True, (200, 210, 220)), (rx, ly)); ly += 32
                
            icon_y = max(ly + 40, 420)
            self.screen.blit(self.fonts['lg'].render("BIỂU TƯỢNG IN-GAME", True, (180, 180, 200)), (rx, icon_y))
            icon_bg = pygame.Rect(rx, icon_y + 45, 80, 80)
            pygame.draw.rect(self.screen, (20, 20, 30), icon_bg, border_radius=10)
            pygame.draw.rect(self.screen, (80, 80, 100), icon_bg, width=2, border_radius=10)
            self.draw_entity_icon(name, rx + 40, icon_y + 85)


    # --------------------------------------------------------------- GAME DRAW
    def draw_game(self):
        if getattr(self, 'level_bgs', {}).get(self.current_level):
            self.screen.blit(self.level_bgs[self.current_level], (0, 0))
        else:
            self.screen.fill(C_BG)
            
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rect = (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, C_GRID_LINE, rect, 1)
                
                if self.grid[r][c] == 2:
                    pygame.draw.rect(self.screen, (40, 45, 55), rect)
                    pygame.draw.rect(self.screen, (60, 65, 75), rect, width=2)
                    pygame.draw.rect(self.screen, (30, 35, 45), (c*CELL_SIZE+8, r*CELL_SIZE+8, CELL_SIZE-16, CELL_SIZE-16))

        bx = BASE_POS[1]*CELL_SIZE;  by = BASE_POS[0]*CELL_SIZE
        sx = SPAWN_POS[1]*CELL_SIZE; sy = SPAWN_POS[0]*CELL_SIZE
        
        # Vầng sáng: Base = tím (Hắc Quốc), Spawn = trắng (Bạch Quốc)
        draw_glow(self.screen, bx + CELL_SIZE//2, by + CELL_SIZE//2, 45, (80, 20, 120))
        draw_glow(self.screen, sx + CELL_SIZE//2, sy + CELL_SIZE//2, 45, (200, 200, 220))
        
        pygame.draw.rect(self.screen, C_BASE,  (bx, by, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.screen, C_SPAWN, (sx, sy, CELL_SIZE, CELL_SIZE))
        self.screen.blit(self.fonts['xs'].render("THÀNH", True, (255,255,255)), (bx+6, by+16))
        self.screen.blit(self.fonts['xs'].render("BẠCH MÔN", True, (40,40,40)),   (sx+1, sy+16))

        for t in self.towers:
            tr, tc = t.grid_pos
            tx, ty = tc*CELL_SIZE, tr*CELL_SIZE
            cx, cy = tx+CELL_SIZE//2, ty+CELL_SIZE//2
            name = type(t).__name__
            
            # Vầng sáng tím cho Tháp Hắc Quốc
            draw_glow(self.screen, cx, cy, 35, (80, 20, 120))
            
            border = {1:(120,120,120), 2:(255,215,0), 3:(0,255,255)}.get(t.level, (120,120,120))
            pygame.draw.rect(self.screen, border, (tx+2, ty+2, CELL_SIZE-4, CELL_SIZE-4), t.level)
            
            if name == "Thanatos" and getattr(t, 'is_triggered', False):
                continue
            draw_entity_shape(self.screen, name, cx, cy, 0)

        node = self.monsters.head
        while node:
            m = node.data
            mx2, my2 = int(m.pixel_pos[0]), int(m.pixel_pos[1])
            name = type(m).__name__
            angle = getattr(m, 'angle', 0)
            
            # Vầng sáng trắng cho Quân Bạch Quốc
            draw_glow(self.screen, mx2, my2, 28, (200, 200, 220))
            
            draw_entity_shape(self.screen, name, mx2, my2, angle)
            ratio = max(0, m.hp / m.max_hp)
            pygame.draw.rect(self.screen, (255,0,0), (mx2-15,my2-20,30,4))
            pygame.draw.rect(self.screen, (0,255,0), (mx2-15,my2-20,int(30*ratio),4))
            node = node.next

        for b in self.bullets:        b.draw(self.screen)
        for ft in self.floating_texts: ft.draw(self.screen, self.fonts['sm'])

        # Draw Phalanx spikes
        for coords, tmr in getattr(self, 'phalanx_spikes', []):
            x1, y1, x2, y2 = coords
            alpha = int(255 * max(0.0, min(1.0, tmr / 0.25)))
            # Create transparent surface
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            # Draw outer glow cyan line
            pygame.draw.line(s, (80, 200, 255, int(alpha * 0.5)), (x1, y1), (x2, y2), 8)
            # Draw inner bright silver-white line
            pygame.draw.line(s, (240, 250, 255, alpha), (x1, y1), (x2, y2), 3)
            # Draw sharp spike head
            pygame.draw.circle(s, (255, 255, 255, alpha), (int(x2), int(y2)), 5)
            self.screen.blit(s, (0, 0))

        # Draw range circles for recently placed towers
        for tw, tmr in getattr(self, 'range_show', []):
            alpha_ratio = min(1.0, tmr / 5.0)  # fade out as timer drops
            alpha = int(80 * alpha_ratio)
            tcx = tw.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
            tcy = tw.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
            radius_px = int(tw.range * CELL_SIZE)
            t_name2 = type(tw).__name__
            ring_col = {'Ignis':(255,140,40),'Hephaestus':(255,180,60),'Kronos':(180,100,255),
                        'Phalanx':(60,220,255),'Ares':(255,60,60),'Thanatos':(220,100,255)}.get(t_name2,(100,200,255))
            # Filled translucent circle
            rsurf = pygame.Surface((radius_px*2+4, radius_px*2+4), pygame.SRCALPHA)
            pygame.draw.circle(rsurf, (*ring_col, alpha), (radius_px+2, radius_px+2), radius_px)
            self.screen.blit(rsurf, (tcx - radius_px - 2, tcy - radius_px - 2))
            # Solid ring outline
            pygame.draw.circle(self.screen, ring_col, (tcx, tcy), radius_px, 2)
            # Label
            if tmr > 3.5:
                rlbl = self.fonts['xs'].render(f'{t_name2} range', True, ring_col)
                self.screen.blit(rlbl, (tcx - rlbl.get_width()//2, tcy - radius_px - 18))

        # SIDEBAR
        SB = GRID_COLS * CELL_SIZE
        pygame.draw.rect(self.screen, C_SIDEBAR, (SB, 0, SIDEBAR_WIDTH, SCREEN_H))
        # Thin highlight line on left edge
        pygame.draw.line(self.screen, (60, 65, 85), (SB, 0), (SB, SCREEN_H), 2)
        
        self.screen.blit(self.fonts['lg'].render(f"LEVEL: {self.current_level}/10", True, C_TEXT), (SB+12, 12))
        if getattr(self, 'heart_sidebar_icon', None):
            self.screen.blit(self.heart_sidebar_icon, (SB+12, 48))
            self.screen.blit(self.fonts['lg'].render(f"{self.gold}", True, (255, 100, 180)), (SB+42, 46))
        else:
            self.screen.blit(self.fonts['lg'].render(f"❤️ {self.gold}", True, (255, 100, 180)), (SB+12, 46))
        hp_c = (0,220,0) if self.base.hp > 8 else (255,50,50)
        self.screen.blit(self.fonts['sm'].render(f"HP: {int(self.base.hp)}/{self.base.max_hp}", True, hp_c), (SB+12, 84))

        avail = TOWERS_BY_LEVEL.get(self.current_level, ["Ballista"])
        y = 115
        sel_tw = getattr(self, 'dragged_tower_type', None)  # selected tower name
        if sel_tw:
            hint_header = f"Đang chọn: {sel_tw}  (Click ô để đặt)"
        else:
            hint_header = "─── VŨ KHÍ ─── (Click để chọn)"
        self.screen.blit(self.fonts['xs'].render(hint_header, True, (120, 200, 255) if sel_tw else C_TEXT_DIM), (SB+8, y)); y += 22
        mx3, my3 = pygame.mouse.get_pos()
        lclick = pygame.mouse.get_pressed()[0]

        # Pause button
        pause_btn = pygame.Rect(SCREEN_W - 54, 10, 44, 44)
        is_hover_pause = pause_btn.collidepoint(mx3, my3)
        draw_rect = pause_btn.inflate(6, 6) if is_hover_pause else pause_btn
        
        if is_hover_pause:
            draw_glow(self.screen, draw_rect.centerx, draw_rect.centery, 26, (0, 230, 255))
            
        btn_color = (40, 50, 70) if is_hover_pause else (25, 28, 40)
        border_color = (0, 230, 255) if is_hover_pause else (100, 105, 120)
        pygame.draw.rect(self.screen, btn_color, draw_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, draw_rect, width=2, border_radius=12)
        
        # Mathematical vertical pause lines
        bar_w = 4
        bar_h = 16
        gap = 6
        cx = draw_rect.centerx
        cy = draw_rect.centery
        left_bar = pygame.Rect(cx - bar_w - gap//2, cy - bar_h//2, bar_w, bar_h)
        right_bar = pygame.Rect(cx + gap//2, cy - bar_h//2, bar_w, bar_h)
        pygame.draw.rect(self.screen, (255, 255, 255), left_bar, border_radius=1)
        pygame.draw.rect(self.screen, (255, 255, 255), right_bar, border_radius=1)
        
        if lclick and is_hover_pause:
            self.play_click()
            self.state = "PAUSE"
            pygame.time.delay(200)

        # Tower card tiles (PvZ style – click to select)
        CARD_W = SIDEBAR_WIDTH - 16
        CARD_H = 56
        for tw_name in avail:
            tw_cls = TOWER_REGISTRY.get(tw_name)
            if not tw_cls: continue
            cost = tw_cls((0,0)).cost
            is_selected = (sel_tw == tw_name)
            is_hover_card = pygame.Rect(SB+8, y, CARD_W, CARD_H).collidepoint(mx3, my3)
            can_afford = self.gold >= cost

            # Card background
            if is_selected:
                bg = (60, 100, 190)
            elif not can_afford:
                bg = (35, 30, 30)
            elif is_hover_card:
                bg = (50, 70, 110)
            else:
                bg = (30, 35, 50)

            card_rect = pygame.Rect(SB+8, y, CARD_W, CARD_H)
            pygame.draw.rect(self.screen, bg, card_rect, border_radius=8)
            border_col = (180, 220, 255) if is_selected else ((80, 100, 150) if can_afford else (60, 50, 50))
            border_w = 2 if is_selected else 1
            pygame.draw.rect(self.screen, border_col, card_rect, width=border_w, border_radius=8)

            # Poster image (44x44) on left, fallback to geometric shape
            icon_rect = pygame.Rect(SB+10, y+6, 44, 44)
            pygame.draw.rect(self.screen, (15, 18, 25), icon_rect, border_radius=6)
            poster_full = self.get_poster(tw_name)
            if poster_full:
                # Scale poster to fit 44x44
                if not hasattr(self, '_sidebar_posters'):
                    self._sidebar_posters = {}
                if tw_name not in self._sidebar_posters:
                    self._sidebar_posters[tw_name] = pygame.transform.smoothscale(poster_full, (44, 44))
                self.screen.blit(self._sidebar_posters[tw_name], (icon_rect.x, icon_rect.y))
            else:
                draw_entity_shape(self.screen, tw_name, icon_rect.centerx, icon_rect.centery, 0)

            # Name + cost
            name_col = (255, 255, 80) if can_afford else (120, 100, 100)
            self.screen.blit(self.fonts['sm'].render(tw_name, True, name_col), (SB+60, y+8))
            heart_col = (255, 100, 180) if can_afford else (140, 70, 100)
            if getattr(self, 'heart_card_icon', None):
                self.screen.blit(self.heart_card_icon, (SB+60, y+32))
                self.screen.blit(self.fonts['sm'].render(f"{cost}", True, heart_col), (SB+80, y+30))
            else:
                self.screen.blit(self.fonts['sm'].render(f"❤️ {cost}", True, heart_col), (SB+60, y+30))

            # Selected tick mark
            if is_selected:
                tick = self.fonts['md'].render("✓", True, (100, 230, 140))
                self.screen.blit(tick, (SB+8+CARD_W-20, y+8))

            y += CARD_H + 5

        # Instructions at bottom
        y_hint = SCREEN_H - 88
        for txt in ["Phải Click: Nâng cấp tháp", "Click quái/tháp: Xem info", "R: Chơi lại  |  ESC: Dừng"]:
            self.screen.blit(self.fonts['xs'].render(txt, True, C_TEXT_DIM), (SB+8, y_hint)); y_hint += 20

        # ── Ghost preview on grid cell when tower selected ────────────
        if sel_tw and mx3 <= GRID_COLS * CELL_SIZE:
            col_g = mx3 // CELL_SIZE
            row_g = my3 // CELL_SIZE
            if 0 <= row_g < GRID_ROWS and 0 <= col_g < GRID_COLS:
                gx = col_g * CELL_SIZE
                gy = row_g * CELL_SIZE
                valid_cell = (self.grid[row_g][col_g] == 0)
                ghost_col = (50, 180, 100, 100) if valid_cell else (200, 50, 50, 100)
                ghost_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                ghost_surf.fill(ghost_col)
                pygame.draw.rect(ghost_surf, (150, 220, 150, 200) if valid_cell else (255, 80, 80, 200),
                                 (0, 0, CELL_SIZE, CELL_SIZE), 2)
                draw_entity_shape(ghost_surf, sel_tw, CELL_SIZE//2, CELL_SIZE//2, 0)
                self.screen.blit(ghost_surf, (gx, gy))
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # ── Entity Inspect Popup ─────────────────────────────────────
        entity = getattr(self, 'selected_entity_on_map', None)
        if entity:
            name = type(entity).__name__
            # Position popup: prefer above entity, keep on screen
            if hasattr(entity, 'pixel_pos'):
                ex, ey = int(entity.pixel_pos[0]), int(entity.pixel_pos[1])
            else:
                ex = entity.grid_pos[1]*CELL_SIZE + CELL_SIZE//2
                ey = entity.grid_pos[0]*CELL_SIZE + CELL_SIZE//2

            BOX_W, BOX_H = 230, 88
            px = min(max(ex - BOX_W//2, 4), SB - BOX_W - 4)
            py = max(ey - BOX_H - 14, 4)

            # Backdrop
            pop_surf = pygame.Surface((BOX_W, BOX_H), pygame.SRCALPHA)
            pop_surf.fill((10, 14, 28, 220))
            self.screen.blit(pop_surf, (px, py))
            pygame.draw.rect(self.screen, (100, 160, 255), (px, py, BOX_W, BOX_H), width=2, border_radius=8)

            # Entity name
            name_lbl = self.fonts['md'].render(name, True, (255, 230, 100))
            self.screen.blit(name_lbl, (px+10, py+10))

            # Info line (hp if monster, level if tower)
            if hasattr(entity, 'hp') and hasattr(entity, 'max_hp'):
                info_str = f"HP: {int(entity.hp)}/{int(entity.max_hp)}"
            elif hasattr(entity, 'level'):
                info_str = f"Cấp: {entity.level}/3"
            else:
                info_str = ""
            info_lbl = self.fonts['xs'].render(info_str, True, (180, 200, 220))
            self.screen.blit(info_lbl, (px+10, py+38))

            # [!] dict button
            btn_rect = pygame.Rect(px + BOX_W - 36, py + 8, 28, 28)
            self._inspect_btn_rect = btn_rect
            bh = btn_rect.collidepoint(mx3, my3)
            pygame.draw.rect(self.screen, (220, 160, 30) if bh else (160, 110, 20), btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 200, 60), btn_rect, width=1, border_radius=6)
            lbl_ex = self.fonts['md'].render("!", True, (255, 255, 255))
            self.screen.blit(lbl_ex, (btn_rect.x + btn_rect.w//2 - lbl_ex.get_width()//2, btn_rect.y + 4))

            # Hint text
            hint_lbl = self.fonts['xs'].render("Click ngoài để tiếp tục", True, (140, 160, 190))
            self.screen.blit(hint_lbl, (px+10, py+62))



    def draw_pause(self):
        self.draw_game()
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        hdr = self.fonts['xl'].render("TẠM DỪNG", True, (255, 255, 255))
        self.screen.blit(hdr, (SCREEN_W//2 - hdr.get_width()//2, 150))
        
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        
        btns = [
            (pygame.Rect(SCREEN_W//2-150, 240, 300, 52), "TIẾP TỤC", (40, 160, 80), (0, 220, 100), "RESUME"),
            (pygame.Rect(SCREEN_W//2-150, 310, 300, 52), "TỪ ĐIỂN DỮ LIỆU", (60, 120, 240), (100, 160, 255), "DICT"),
            (pygame.Rect(SCREEN_W//2-150, 380, 300, 52), "CÀI ĐẶT", (180, 120, 40), (230, 170, 70), "SETTINGS"),
            (pygame.Rect(SCREEN_W//2-150, 450, 300, 52), "VỀ MENU", (160, 50, 50), (220, 80, 80), "MENU")
        ]
        
        for rect, label, c_norm, c_hov, action in btns:
            is_hover = rect.collidepoint(mx, my)
            draw_rect = rect.inflate(8, 8) if is_hover else rect
            
            # Glowing halo on hover
            if is_hover:
                draw_glow(self.screen, draw_rect.centerx, draw_rect.centery, draw_rect.w//2 + 20, c_hov)
                
            pygame.draw.rect(self.screen, c_hov if is_hover else c_norm, draw_rect, border_radius=12)
            pygame.draw.rect(self.screen, (255, 255, 255) if is_hover else (150, 150, 160), draw_rect, width=2, border_radius=12)
            
            lbl = self.fonts['md'].render(label, True, (255, 255, 255))
            self.screen.blit(lbl, (draw_rect.x + draw_rect.w//2 - lbl.get_width()//2, draw_rect.y + draw_rect.h//2 - lbl.get_height()//2))
            
            if click and is_hover:
                self.play_click()
                pygame.time.delay(200)
                if action == "RESUME": self.state = "GAME"
                elif action == "DICT": self.state = "DICT"; self.prev_state = "PAUSE"
                elif action == "SETTINGS": 
                    self.settings_prev_state = "PAUSE"
                    self.state = "SETTINGS"
                elif action == "MENU": self.start_cat_loading("MENU")

    # -------------------------------------------------------------- UPDATE
    def update_game(self, dt):
        if getattr(self, 'selected_entity_on_map', None):
            return # Pause game logic for inspect

        if self.base.hp <= 0:
            self.state = "GAMEOVER"
            self.gameover_image = random.choice([1, 2, 3, 4, 4])
            self.gameover_quote = random.choice(GAMEOVER_QUOTES)
            return

        if self.wave_active:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_monster()
                self.spawn_timer = 1.2
                if self.wave_queue.is_empty():
                    self.wave_active = False

        dead = []
        node = self.monsters.head
        while node:
            m = node.data
            if getattr(m, 'can_attack_tower', False):
                m.attack_timer = getattr(m, 'attack_timer', 0.0) + dt
                if m.attack_timer >= 1.0 / max(0.1, getattr(m,'attack_speed',1.0)):
                    m.attack_timer = 0.0
                    for t in self.towers:
                        dr = abs(t.grid_pos[0] - m.grid_pos[0])
                        dc = abs(t.grid_pos[1] - m.grid_pos[1])
                        if dr + dc == 1:
                            t.take_damage(getattr(m,'attack_damage',15))
                            self.floating_texts.append(FloatingText(
                                t.grid_pos[1]*CELL_SIZE+24, t.grid_pos[0]*CELL_SIZE,
                                f"-{getattr(m,'attack_damage',15)}", (255,100,0)))
            arrived = m.update(dt, CELL_SIZE)
            if m.hp <= 0:
                reward = getattr(m, 'reward', 10)
                self.gold += reward
                self.floating_texts.append(FloatingText(m.pixel_pos[0], m.pixel_pos[1], f"+{reward} ❤️", (255, 100, 180)))
                m.alive = False
            if arrived and m.alive:
                if self.base.take_damage(m.damage_to_base):
                    self.state = "GAMEOVER"
                    self.gameover_image = random.choice([1, 2, 3, 4, 4])
                    self.gameover_quote = random.choice(GAMEOVER_QUOTES)
                    self.play_click()
                self.floating_texts.append(FloatingText(m.pixel_pos[0], m.pixel_pos[1], f"-{m.damage_to_base}HP", (255,0,0)))
                m.alive = False
            if not m.alive:
                dead.append(m)
            node = node.next
        for m in dead:
            self.monsters.remove(m)

        if not self.wave_active and self.monsters.is_empty() and self.wave_queue.is_empty():
            self.gold += WAVE_CLEAR_BONUS
            if self.current_level < 10 and self.current_level >= self.unlocked_level:
                self.unlocked_level = self.current_level + 1
                save_progress(self.unlocked_level, getattr(self, 'has_selected_faction', False), getattr(self, 'has_seen_intro', False), getattr(self, 'has_beaten_game', False))
            
            if self.current_level < 10:
                self.state = "LEVEL_VICTORY"
                self.victory_image = random.randint(1, 3)
                self.victory_quote = random.choice(VICTORY_QUOTES)
            else:
                self.state = "FINAL_STORY"
                self.final_story_index = 0
                self.final_from_settings = False
                self.story_button_cooldown = 3.0
                self.has_beaten_game = True
                save_progress(self.unlocked_level, getattr(self, 'has_selected_faction', False), getattr(self, 'has_seen_intro', False), True)
                self.start_ending_music()

        for t in self.towers[:]:
            if t.hp <= 0:
                self.grid[t.grid_pos[0]][t.grid_pos[1]] = 0
                self.towers.remove(t)
                # Remove from range_show if present
                self.range_show = [(tw, tmr) for tw, tmr in getattr(self,'range_show',[]) if tw is not t]
                recalculate_paths(self.grid, self.monsters); continue
            t_name = type(t).__name__
            if t_name == "Thanatos" and not getattr(t,'is_triggered',False):
                node = self.monsters.head
                while node:
                    m = node.data
                    if m.grid_pos == t.grid_pos:
                        t.is_triggered = True
                        inner = self.monsters.head
                        while inner:
                            mm = inner.data
                            if abs(mm.grid_pos[0]-t.grid_pos[0])<=1 and abs(mm.grid_pos[1]-t.grid_pos[1])<=1:
                                mm.take_damage(t.damage)
                            inner = inner.next
                        self.floating_texts.append(FloatingText(
                            t.grid_pos[1]*CELL_SIZE+24, t.grid_pos[0]*CELL_SIZE, "BOOM!", (255,50,255)))
                        break
                    node = node.next
                if getattr(t,'is_triggered',False):
                    self.grid[t.grid_pos[0]][t.grid_pos[1]] = 0
                    self.towers.remove(t)
                continue
            if t_name == "Kronos":
                if t.can_fire(dt):
                    node = self.monsters.head
                    while node:
                        m = node.data
                        if t.in_range(m.grid_pos): m.apply_slow(t.slow_multiplier, getattr(t,'slow_duration',2.0))
                        node = node.next
                continue
            if not t.can_fire(dt): continue

            # ── Target selection: prioritise monster closest to BASE (fewest steps left) ──
            pq = PriorityQueue()
            tx_center = t.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
            ty_center = t.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
            node = self.monsters.head
            while node:
                m = node.data
                if m.alive:
                    # Use pixel-level distance for range check (more accurate than grid)
                    pdist = ((m.pixel_pos[0] - tx_center)**2 + (m.pixel_pos[1] - ty_center)**2)**0.5
                    if pdist <= t.range * CELL_SIZE:
                        # For Phalanx, only count if it's on the same row or column!
                        if t_name == "Phalanx":
                            same_row = abs(m.pixel_pos[1] - ty_center) < CELL_SIZE * 0.75
                            same_col = abs(m.pixel_pos[0] - tx_center) < CELL_SIZE * 0.75
                            if not (same_row or same_col):
                                node = node.next
                                continue
                        steps_left = len(m.path) - m.path_index if m.path else 9999
                        pq.push(steps_left, m)
                node = node.next
            if pq.is_empty(): continue
            _, target = pq.pop()

            if isinstance(target, Phantom) and random.random() < getattr(target,'dodge_chance',0.2):
                self.floating_texts.append(FloatingText(target.pixel_pos[0], target.pixel_pos[1], "MISS!", (200,200,200))); continue

            # ── Per-tower attack behaviours ──────────────────────────────────────
            if t_name == "Phalanx":
                # Pierce: hit all monsters that share pixel row OR col (within half-cell tolerance)
                node = self.monsters.head
                has_attacked = False
                while node:
                    m = node.data
                    if not m.alive:
                        node = node.next; continue
                    same_row = abs(m.pixel_pos[1] - ty_center) < CELL_SIZE * 0.75
                    same_col = abs(m.pixel_pos[0] - tx_center) < CELL_SIZE * 0.75
                    pdist = ((m.pixel_pos[0]-tx_center)**2 + (m.pixel_pos[1]-ty_center)**2)**0.5
                    if (same_row or same_col) and pdist <= t.range * CELL_SIZE:
                        m.take_damage(t.damage)
                        self.floating_texts.append(FloatingText(m.pixel_pos[0], m.pixel_pos[1], f"-{t.damage}", (120, 220, 255)))
                        if not hasattr(self, 'phalanx_spikes'):
                            self.phalanx_spikes = []
                        self.phalanx_spikes.append(((tx_center, ty_center, m.pixel_pos[0], m.pixel_pos[1]), 0.25))
                        has_attacked = True
                    node = node.next
                if not has_attacked and target:
                    if not hasattr(self, 'phalanx_spikes'):
                        self.phalanx_spikes = []
                    self.phalanx_spikes.append(((tx_center, ty_center, target.pixel_pos[0], target.pixel_pos[1]), 0.25))

            elif t_name == "Ignis":
                # AoE around TARGET's pixel position
                tx2, ty2 = target.pixel_pos[0], target.pixel_pos[1]
                aoe_px = getattr(t, 'aoe_radius', 1.0) * CELL_SIZE
                node = self.monsters.head
                while node:
                    m = node.data
                    if m.alive:
                        d = ((m.pixel_pos[0]-tx2)**2 + (m.pixel_pos[1]-ty2)**2)**0.5
                        if d <= aoe_px:
                            m.take_damage(t.damage)
                    node = node.next

            elif t_name == "Hephaestus":
                # AoE around TARGET's pixel position (larger radius)
                tx2, ty2 = target.pixel_pos[0], target.pixel_pos[1]
                aoe_px = getattr(t, 'aoe_radius', 1.5) * CELL_SIZE
                node = self.monsters.head
                while node:
                    m = node.data
                    if m.alive:
                        d = ((m.pixel_pos[0]-tx2)**2 + (m.pixel_pos[1]-ty2)**2)**0.5
                        if d <= aoe_px:
                            m.take_damage(t.damage)
                    node = node.next

            else:
                # Single-target: Ballista, Ares
                target.take_damage(t.damage)
            bx2, by2 = t.grid_pos[1]*CELL_SIZE+24, t.grid_pos[0]*CELL_SIZE+24
            if t_name not in ("Phalanx","Kronos"):
                self.bullets.append(Bullet((bx2,by2), target, t_name))

        for b in self.bullets[:]:
            b.update(dt)
            if b.reached: self.bullets.remove(b)
        for ft in self.floating_texts[:]:
            ft.update(dt)
            if ft.life <= 0: self.floating_texts.remove(ft)

        # Tick range-show timers
        self.range_show = [(tw, tmr - dt) for tw, tmr in getattr(self, 'range_show', []) if tmr - dt > 0]
        # Tick Phalanx spike effect timers
        self.phalanx_spikes = [(coords, tmr - dt) for coords, tmr in getattr(self, 'phalanx_spikes', []) if tmr - dt > 0]

    # ------------------------------------------------------------ INPUT
    def handle_input_game(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:     self.reset_game(self.current_level)
            if event.key == pygame.K_ESCAPE:
                self.play_click()
                self.state = "PAUSE"
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # 1. Inspect state clicks
            if getattr(self, 'selected_entity_on_map', None):
                if event.button == 1:
                    btn_rect = getattr(self, '_inspect_btn_rect', None)
                    if btn_rect and btn_rect.collidepoint(mx, my):
                        self.play_click()
                        self.dict_selected = type(self.selected_entity_on_map).__name__
                        self.prev_state = "GAME"
                        self.state = "DICT"
                    else:
                        self.selected_entity_on_map = None # Resume game
                return
                
            # 2. Sidebar clicks – click to SELECT tower type
            SB = GRID_COLS * CELL_SIZE
            if mx > SB and event.button == 1:
                avail = TOWERS_BY_LEVEL.get(self.current_level, ["Ballista"])
                CARD_H = 56
                y = 115 + 22  # match draw_game y start after header
                for tw_name in avail:
                    tw_cls = TOWER_REGISTRY.get(tw_name)
                    if not tw_cls:
                        y += CARD_H + 5
                        continue
                    rect = pygame.Rect(SB+8, y, SIDEBAR_WIDTH-16, CARD_H)
                    if rect.collidepoint(mx, my):
                        # Toggle: clicking the same card deselects
                        if self.dragged_tower_type == tw_name:
                            self.dragged_tower_type = None
                        else:
                            self.dragged_tower_type = tw_name
                        self.play_click()
                        pygame.time.delay(80)
                        return
                    y += CARD_H + 5

            # 3. Grid clicks
            if mx <= SB:
                col, row = mx // CELL_SIZE, my // CELL_SIZE
                if not (0<=row<GRID_ROWS and 0<=col<GRID_COLS): return

                if event.button == 1:
                    # If a tower type is selected, try placing it
                    sel_tw = getattr(self, 'dragged_tower_type', None)
                    if sel_tw:
                        if self.grid[row][col] == 0:
                            tw_class = TOWER_REGISTRY.get(sel_tw)
                            if tw_class:
                                temp = tw_class((row, col))
                                if self.gold >= temp.cost:
                                    self.grid[row][col] = 1
                                    if bfs_find_path(self.grid, SPAWN_POS, BASE_POS):
                                        self.gold -= temp.cost
                                        self.towers.append(temp)
                                        recalculate_paths(self.grid, self.monsters)
                                        # Show range circle 5s after placement
                                        rs = getattr(self, 'range_show', [])
                                        rs = [(tw, tmr) for tw, tmr in rs if tw is not temp]
                                        rs.append((temp, 5.0))
                                        self.range_show = rs
                                    else:
                                        self.grid[row][col] = 0
                                        self.floating_texts.append(FloatingText(mx, my, "BỊT ĐƯỜNG!", (255,0,0)))
                                else:
                                    self.floating_texts.append(FloatingText(mx, my, "THIẾU TIM", (255, 100, 180)))
                        return

                    # No tower selected – check entity inspect
                    for t in self.towers:
                        if t.grid_pos == (row, col):
                            self.selected_entity_on_map = t
                            return
                    node = self.monsters.head
                    while node:
                        m = node.data
                        if abs(m.pixel_pos[0] - mx) < 20 and abs(m.pixel_pos[1] - my) < 20:
                            self.selected_entity_on_map = m
                            return
                        node = node.next

                # Right click to upgrade tower OR cancel selection
                if event.button == 3:
                    if getattr(self, 'dragged_tower_type', None):
                        self.dragged_tower_type = None  # cancel selection
                        return
                    for t in self.towers:
                        if t.grid_pos == (row, col):
                            cost = int(t.cost * 0.5)
                            if self.gold >= cost and t.level < 3:
                                self.gold -= cost
                                t.level += 1
                                t.damage = int(t.damage * 1.5)
                                self.floating_texts.append(FloatingText(mx, my, f"UP LV{t.level}!", (0,255,255)))
                            return

    def update_video_state(self):
        """Render từng frame video lên màn hình và quản lý chuyển trạng thái."""
        try:
            import cv2, numpy
        except:
            self.skip_videos(); return

        if self.state == "START_DELAY":
            self.screen.fill((0, 0, 0))
            self.delay_timer -= 1
            if self.delay_timer <= 0:
                if getattr(self, 'logo_cap', None) and self.logo_cap.isOpened():
                    self.state = "FADE_IN_LOGO"
                    try:
                        pygame.mixer.music.load("assets/audio/logo_audio.mp3")
                        pygame.mixer.music.play(1)
                    except: pass
                elif getattr(self, 'intro_cap', None) and self.intro_cap.isOpened():
                    self.state = "FADE_IN_INTRO"
                    try:
                        pygame.mixer.music.load("assets/audio/intro_audio.mp3")
                        pygame.mixer.music.play(1)
                    except: pass
                else:
                    self.skip_videos()

        elif self.state in ["FADE_IN_LOGO", "LOGO"]:
            if self.logo_cap and self.logo_cap.isOpened():
                ret, frame = self.logo_cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w = frame.shape[:2]
                    frame = cv2.resize(frame, (SCREEN_W, SCREEN_H))
                    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.screen.blit(surf, (0, 0))
                    
                    if self.state == "FADE_IN_LOGO":
                        self.fade_alpha -= 3
                        if self.fade_alpha <= 0:
                            self.fade_alpha = 0
                            self.state = "LOGO"
                        dark = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                        dark.fill((0, 0, 0, max(0, self.fade_alpha)))
                        self.screen.blit(dark, (0, 0))
                else:
                    self.logo_cap.release(); self.logo_cap = None
                    pygame.mixer.music.stop()
                    self.state = "FADE_OUT_LOGO"
                    self.fade_alpha = 0
            else:
                self.state = "FADE_OUT_LOGO"; self.fade_alpha = 0

        elif self.state == "FADE_OUT_LOGO":
            # Bước 1: 15 frame đầu — làm tối nhanh sau khi logo kết thúc
            if not hasattr(self, '_cat_timer'):
                self._cat_timer = 0
                self._quick_fade = 0
            
            self.screen.fill((0, 0, 0))
            
            if self._quick_fade < 15:
                # Giai đoạn fade-to-black nhanh
                self._quick_fade += 1
            else:
                # Giai đoạn hiện mèo (5 giây = 150 frames ở 30fps)
                self._cat_timer += 1

                if self.loading_cat_frames:
                    n = len(self.loading_cat_frames)
                    # Nếu là GIF nhiều frame — chạy ở tốc độ 1 frame mỗi 4 frame game
                    gif_i = (self._cat_timer // 4) % n
                    cat_surf = self.loading_cat_frames[gif_i]
                    # Xoay quanh tâm
                    self.loading_cat_angle = (self.loading_cat_angle + 4) % 360
                    rotated = pygame.transform.rotozoom(cat_surf, self.loading_cat_angle, 1.0)
                    rect = rotated.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30))
                    self.screen.blit(rotated, rect)

                # Dấu chấm động: thay đổi mỗi 18 frame
                self.loading_dot_tick += 1
                if self.loading_dot_tick >= 18:
                    self.loading_dot_tick = 0
                    self.loading_dot_count = (self.loading_dot_count + 1) % 4
                dots = "." * self.loading_dot_count
                loading_text = self.fonts['lg'].render(f"Loading{dots}", True, (200, 200, 200))
                self.screen.blit(loading_text,
                    (SCREEN_W // 2 - loading_text.get_width() // 2, SCREEN_H // 2 + 175))

                if self._cat_timer >= 150:  # 5 giây
                    del self._cat_timer, self._quick_fade
                    if getattr(self, 'intro_cap', None) and self.intro_cap.isOpened():
                        self.state = "FADE_IN_INTRO"
                        try:
                            pygame.mixer.music.load("assets/audio/intro_audio.mp3")
                            pygame.mixer.music.play(1)
                            pygame.mixer.music.queue("assets/audio/bgm.mp3", loops=-1)
                        except: pass
                    else:
                        self.skip_videos()

        elif self.state in ["FADE_IN_INTRO", "INTRO"]:
            if self.intro_cap and self.intro_cap.isOpened():
                ret, frame = self.intro_cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (SCREEN_W, SCREEN_H))
                    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.last_intro_surf = surf.copy()  # Lưu frame cuối để dùng cho cross-dissolve
                    self.screen.blit(surf, (0, 0))
                    
                    if self.state == "FADE_IN_INTRO":
                        self.fade_alpha -= 3
                        if self.fade_alpha <= 0:
                            self.fade_alpha = 0
                            self.state = "INTRO"
                        dark = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                        dark.fill((0, 0, 0, max(0, self.fade_alpha)))
                        self.screen.blit(dark, (0, 0))
                else:
                    self.intro_cap.release(); self.intro_cap = None
                    self.state = "CROSSFADE_TO_MENU"
                    self.crossfade_alpha = 0  # 0 = ảnh nền trong suốt, 255 = ảnh nền hiện rõ
            else:
                self.state = "CROSSFADE_TO_MENU"
                self.crossfade_alpha = 0

        elif self.state == "CROSSFADE_TO_MENU":
            # Vẽ frame cuối của intro phía dưới
            if getattr(self, 'last_intro_surf', None):
                self.screen.blit(self.last_intro_surf, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            # Vẽ menu background đè lên với alpha tăng dần
            alpha = min(255, getattr(self, 'crossfade_alpha', 0))
            if self.menu_bg:
                bg_copy = self.menu_bg.copy()
                bg_copy.set_alpha(alpha)
                self.screen.blit(bg_copy, (0, 0))
            self.crossfade_alpha = alpha + 4
            if alpha >= 255:
                # Chuyển hẳn sang MENU và khởi động hiệu ứng trượt nút
                self.state = "MENU"
                self.menu_anim_y = SCREEN_H + 100
                self.menu_fade_alpha = 0  # Nền đã hiện rõ rồi, không cần fade thêm

    def skip_videos(self):
        """Bỏ qua video, chuyển thẳng vào Menu."""
        if getattr(self, 'logo_cap', None):
            self.logo_cap.release(); self.logo_cap = None
        if getattr(self, 'intro_cap', None):
            self.intro_cap.release(); self.intro_cap = None
        pygame.mixer.music.stop()
        self.state = "MENU"
        self.menu_anim_y = SCREEN_H + 300  # Khoảng nghỉ trước khi nút trượt lên
        self.menu_fade_alpha = 255
        self.start_menu_music()

    def start_cat_loading(self, next_state, frames=90):
        """Hiện mèo xoay vòng rồi chuyển sang next_state sau `frames` frame."""
        self._cat_load_next = next_state
        self._cat_load_timer = frames
        self._cat_load_angle = 0.0
        self._cat_load_gif_i = 0
        self._cat_load_dot_count = 0
        self._cat_load_dot_tick = 0
        self.state = "CAT_LOADING"

    def draw_cat_loading(self):
        """Vẽ màn hình mèo loading."""
        self.screen.fill((0, 0, 0))
        if self.loading_cat_frames:
            n = len(self.loading_cat_frames)
            self._cat_load_gif_i = (getattr(self, '_cat_load_gif_i', 0) + 1)
            gif_idx = (self._cat_load_gif_i // 4) % n
            cat_surf = self.loading_cat_frames[gif_idx]
            self._cat_load_angle = (getattr(self, '_cat_load_angle', 0) + 4) % 360
            rotated = pygame.transform.rotozoom(cat_surf, self._cat_load_angle, 1.0)
            rect = rotated.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30))
            self.screen.blit(rotated, rect)
        # Dấu chấm động
        self._cat_load_dot_tick = getattr(self, '_cat_load_dot_tick', 0) + 1
        if self._cat_load_dot_tick >= 18:
            self._cat_load_dot_tick = 0
            self._cat_load_dot_count = (getattr(self, '_cat_load_dot_count', 0) + 1) % 4
        dots = "." * self._cat_load_dot_count
        txt = self.fonts['lg'].render(f"Loading{dots}", True, (200, 200, 200))
        self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, SCREEN_H // 2 + 175))
        # Đếm xuống
        self._cat_load_timer -= 1
        if self._cat_load_timer <= 0:
            next_s = getattr(self, '_cat_load_next', 'MENU')
            self.state = next_s

    # ------------------------------------------------------------ MAIN LOOP
    async def run(self):
        while True:
            await asyncio.sleep(0)
            VIDEO_STATES = ["START_DELAY", "FADE_IN_LOGO", "LOGO", "FADE_OUT_LOGO", "FADE_IN_INTRO", "INTRO", "CROSSFADE_TO_MENU"]
            if self.state in VIDEO_STATES:
                dt = self.clock.tick(30) / 1000.0
            else:
                dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                        
                if self.state == "GAME": self.handle_input_game(event)
                elif self.state == "OUTRO":
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                            if getattr(self, 'outro_skippable', False):
                                self.play_click()
                                self.state = "MENU"
                                self.start_menu_music()
                elif self.state == "SETTINGS" and getattr(self, 'settings_prompt_password', False):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            self.setting_password_input = self.setting_password_input[:-1]
                        elif event.key == pygame.K_RETURN:
                            if self.setting_password_input == "417":
                                self.ending_unlocked_by_code = True
                                self.settings_prompt_password = False
                                self.setting_password_input = ""
                                self.warning_text = "Đã mở khóa kết thúc trò chơi!"
                                self.warning_timer = 180
                            else:
                                self.setting_password_input = ""
                                self.warning_text = "Mật mã không đúng!"
                                self.warning_timer = 120
                        elif event.key == pygame.K_ESCAPE:
                            self.settings_prompt_password = False
                            self.setting_password_input = ""
                        else:
                            char = event.unicode
                            if char.isdigit() and len(self.setting_password_input) < 10:
                                self.setting_password_input += char
                

                        
            if self.state in VIDEO_STATES:
                self.update_video_state()
            elif self.state == "CAT_LOADING":   self.draw_cat_loading()
            elif self.state == "MENU":     self.draw_menu()
            elif self.state == "FACTION_SELECT": self.draw_faction_select()
            elif self.state == "INTRO_STORY":    self.draw_intro_story()
            elif self.state == "FINAL_STORY":    self.draw_final_story()
            elif self.state == "SETTINGS": self.draw_settings()
            elif self.state == "OUTRO":    self.draw_outro()
            elif self.state == "LEVEL_SELECT": self.draw_level_select()
            elif self.state == "STORY":    self.draw_story()
            elif self.state == "DICT":     self.draw_dict()
            elif self.state == "GAME":
                self.update_game(dt)
                self.draw_game()
            elif self.state == "PAUSE":
                self.draw_pause()
            elif self.state == "GAMEOVER":
                self.screen.fill((40, 10, 10))
                
                # Render random lose image
                if not hasattr(self, 'gameover_img_cache'):
                    self.gameover_img_cache = {}
                img_idx = getattr(self, 'gameover_image', 1)
                
                if img_idx not in self.gameover_img_cache:
                    loaded = False
                    for ext in ["png", "PNG"]:
                        path = f"assets/story/lose_{img_idx}.{ext}"
                        if os.path.exists(path):
                            try:
                                img = pygame.image.load(path).convert_alpha()
                                self.gameover_img_cache[img_idx] = pygame.transform.scale(img, (600, 350))
                                loaded = True
                                break
                            except:
                                pass
                    if not loaded:
                        self.gameover_img_cache[img_idx] = None
                
                img_rect = pygame.Rect(SCREEN_W//2 - 300, 100, 600, 350)
                if self.gameover_img_cache[img_idx] is not None:
                    self.screen.blit(self.gameover_img_cache[img_idx], img_rect.topleft)
                    pygame.draw.rect(self.screen, (200, 50, 50), img_rect, width=3)
                else:
                    pygame.draw.rect(self.screen, (20, 10, 10), img_rect)
                    pygame.draw.rect(self.screen, (100, 50, 50), img_rect, width=3)
                    txt = self.fonts['md'].render(f"Ảnh thua lose_{img_idx} (Chưa có)", True, (150, 100, 100))
                    self.screen.blit(txt, (img_rect.x + img_rect.w//2 - txt.get_width()//2, img_rect.y + img_rect.h//2 - txt.get_height()//2))

                hdr = self.fonts['xl'].render("THÀNH ĐÃ THẤT THỦ!", True, (255, 50, 50))
                self.screen.blit(hdr, (SCREEN_W//2 - hdr.get_width()//2, 40))
                
                mx, my = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()[0]
                
                btn_replay = pygame.Rect(SCREEN_W//2 - 250, 480, 200, 60)
                is_hover_r = btn_replay.collidepoint(mx, my)
                c_r = (180, 40, 40) if is_hover_r else (120, 30, 30)
                pygame.draw.rect(self.screen, c_r, btn_replay, border_radius=10)
                pygame.draw.rect(self.screen, (255,255,255), btn_replay, width=2, border_radius=10)
                lbl_r = self.fonts['lg'].render("CHƠI LẠI", True, (255, 255, 255))
                self.screen.blit(lbl_r, (btn_replay.x + btn_replay.w//2 - lbl_r.get_width()//2, btn_replay.y + 10))
                
                btn_menu = pygame.Rect(SCREEN_W//2 + 50, 480, 200, 60)
                is_hover_m = btn_menu.collidepoint(mx, my)
                c_m = (100, 100, 100) if is_hover_m else (60, 60, 60)
                pygame.draw.rect(self.screen, c_m, btn_menu, border_radius=10)
                pygame.draw.rect(self.screen, (255,255,255), btn_menu, width=2, border_radius=10)
                lbl_m = self.fonts['lg'].render("MENU", True, (255, 255, 255))
                self.screen.blit(lbl_m, (btn_menu.x + btn_menu.w//2 - lbl_m.get_width()//2, btn_menu.y + 10))
                
                # Render quote / caption
                quote_text = getattr(self, 'gameover_quote', "Cuộc chiến khốc liệt đã khép lại...")
                lbl_q = self.fonts['md'].render(quote_text, True, (250, 180, 180))
                q_rect = pygame.Rect(SCREEN_W//2 - 450, 560, 900, 45)
                pygame.draw.rect(self.screen, (30, 5, 5), q_rect, border_radius=8)
                pygame.draw.rect(self.screen, (150, 50, 50), q_rect, width=1, border_radius=8)
                self.screen.blit(lbl_q, (SCREEN_W//2 - lbl_q.get_width()//2, q_rect.y + 10))
                
                if click:
                    if is_hover_r:
                        self.play_click()
                        self.reset_game(self.current_level)
                        self.start_cat_loading("STORY")
                        pygame.time.delay(150)
                    elif is_hover_m:
                        self.play_click()
                        self.start_cat_loading("MENU")
                        pygame.time.delay(150)
            elif self.state == "LEVEL_VICTORY":
                self.screen.fill((10, 40, 20))
                
                # Render random win image
                if not hasattr(self, 'victory_img_cache'):
                    self.victory_img_cache = {}
                img_idx = getattr(self, 'victory_image', 1)
                
                if img_idx not in self.victory_img_cache:
                    loaded = False
                    for ext in ["png", "PNG"]:
                        path = f"assets/story/win_{img_idx}.{ext}"
                        if os.path.exists(path):
                            try:
                                img = pygame.image.load(path).convert_alpha()
                                self.victory_img_cache[img_idx] = pygame.transform.scale(img, (600, 350))
                                loaded = True
                                break
                            except:
                                pass
                    if not loaded:
                        self.victory_img_cache[img_idx] = None
                        
                img_rect = pygame.Rect(SCREEN_W//2 - 300, 100, 600, 350)
                if self.victory_img_cache[img_idx] is not None:
                    self.screen.blit(self.victory_img_cache[img_idx], img_rect.topleft)
                    pygame.draw.rect(self.screen, (50, 200, 100), img_rect, width=3)
                else:
                    pygame.draw.rect(self.screen, (10, 30, 20), img_rect)
                    pygame.draw.rect(self.screen, (50, 150, 80), img_rect, width=3)
                    txt = self.fonts['md'].render(f"Ảnh thắng win_{img_idx} (Chưa có)", True, (100, 150, 100))
                    self.screen.blit(txt, (img_rect.x + img_rect.w//2 - txt.get_width()//2, img_rect.y + img_rect.h//2 - txt.get_height()//2))

                hdr = self.fonts['xl'].render("HẮC QUỐC CHIẾN THẮNG!", True, (255, 255, 50))
                self.screen.blit(hdr, (SCREEN_W//2 - hdr.get_width()//2, 40))
                
                mx, my = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()[0]
                btn = pygame.Rect(SCREEN_W//2 - 120, 480, 240, 60)
                is_hover = btn.collidepoint(mx, my)
                c = (40, 160, 80) if is_hover else (30, 120, 60)
                pygame.draw.rect(self.screen, c, btn, border_radius=10)
                lbl = self.fonts['lg'].render("TIẾP TỤC", True, (255, 255, 255))
                self.screen.blit(lbl, (btn.x + btn.w//2 - lbl.get_width()//2, btn.y + 10))
                
                # Render quote / caption
                quote_text = getattr(self, 'victory_quote', "Kháng chiến trường kỳ nhất định thắng lợi!")
                lbl_q = self.fonts['md'].render(quote_text, True, (180, 250, 180))
                q_rect = pygame.Rect(SCREEN_W//2 - 450, 560, 900, 45)
                pygame.draw.rect(self.screen, (5, 30, 10), q_rect, border_radius=8)
                pygame.draw.rect(self.screen, (50, 150, 80), q_rect, width=1, border_radius=8)
                self.screen.blit(lbl_q, (SCREEN_W//2 - lbl_q.get_width()//2, q_rect.y + 10))
                
                if click and is_hover:
                    self.play_click()
                    self.state = "LEVEL_SELECT"
                    pygame.time.delay(200)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]: self.state="MENU"; pygame.time.delay(300)
                
            # Draw Guide Popup Overlay
            self.draw_guide_popup()
            
            pygame.display.flip()


if __name__ == "__main__":
    game = GameEngine()
    asyncio.run(game.run())
