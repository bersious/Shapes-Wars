class Node:
    """
    Node cơ bản dùng cho các cấu trúc dữ liệu dạng liên kết.

    Tham số:
        data: Dữ liệu lưu trong node (có thể là bất kỳ kiểu dữ liệu nào).

    Thuộc tính:
        data: Dữ liệu được lưu trữ.
        next (Node): Con trỏ đến node tiếp theo.

    Độ phức tạp:
        - Time Complexity: O(1) để khởi tạo.
        - Space Complexity: O(1).
    """
    def __init__(self, data):
        self.data = data
        self.next = None


# =============================================================================
# LINKED LIST — Quản lý danh sách quái vật trên bản đồ
# =============================================================================

class LinkedList:
    """
    Danh sách liên kết đơn (Singly Linked List) dùng để quản lý
    các thực thể (quái vật) đang hoạt động trên bản đồ game.

    Tự triển khai hoàn toàn, không sử dụng thư viện Python có sẵn.
    """

    def __init__(self):
        """
        Khởi tạo danh sách liên kết rỗng.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        """
        Thêm một phần tử vào cuối danh sách.

        Tham số:
            data: Đối tượng cần thêm vào.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        new_node = Node(data)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove(self, target_data):
        """
        Tìm và xóa một phần tử khỏi danh sách.

        Tham số:
            target_data: Đối tượng cần xóa (so sánh bằng 'is').

        Trả về:
            bool: True nếu xóa thành công, False nếu không tìm thấy.

        Độ phức tạp: Time O(n) | Space O(1)
        """
        current = self.head
        previous = None
        while current is not None:
            if current.data is target_data:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current.next is None:
                    self.tail = previous
                self.size -= 1
                return True
            previous = current
            current = current.next
        return False

    def to_list(self):
        """
        Trả về tất cả dữ liệu dưới dạng Python list.

        Độ phức tạp: Time O(n) | Space O(n)
        """
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def is_empty(self):
        """Kiểm tra danh sách có rỗng không. Time O(1)."""
        return self.head is None

    def __len__(self):
        """Trả về số lượng phần tử. Time O(1)."""
        return self.size

    def __iter__(self):
        """Hỗ trợ vòng lặp for...in. Time O(n)."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next


# =============================================================================
# QUEUE — Quản lý hàng đợi quái vật theo từng Wave
# =============================================================================

class Queue:
    """
    Hàng đợi (Queue) theo nguyên tắc FIFO (First In First Out).
    Dùng để quản lý danh sách quái vật sẽ được sinh ra trong mỗi Wave.

    Tự triển khai dựa trên LinkedList nội bộ.
    Không sử dụng collections.deque hay queue.Queue của Python.
    """

    def __init__(self):
        """Khởi tạo hàng đợi rỗng. Time O(1)."""
        self._list = LinkedList()

    def enqueue(self, data):
        """
        Thêm một phần tử vào cuối hàng đợi.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        self._list.append(data)

    def dequeue(self):
        """
        Lấy và xóa phần tử đầu tiên ra khỏi hàng đợi.

        Trả về:
            data: Phần tử ở đầu hàng đợi.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        if self.is_empty():
            raise IndexError("Dequeue từ hàng đợi rỗng.")
        data = self._list.head.data
        self._list.head = self._list.head.next
        if self._list.head is None:
            self._list.tail = None
        self._list.size -= 1
        return data

    def peek(self):
        """
        Xem phần tử đầu tiên mà không xóa.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        if self.is_empty():
            raise IndexError("Peek từ hàng đợi rỗng.")
        return self._list.head.data

    def is_empty(self):
        """Kiểm tra hàng đợi có rỗng không. Time O(1)."""
        return self._list.is_empty()

    def __len__(self):
        """Trả về số lượng phần tử. Time O(1)."""
        return len(self._list)


# =============================================================================
# PRIORITY QUEUE — AI của Tháp phòng thủ chọn mục tiêu để bắn
# =============================================================================

class PriorityQueueNode:
    """
    Node nội bộ dùng cho PriorityQueue, lưu cặp (priority, data).

    Độ phức tạp: Time O(1) | Space O(1)
    """
    def __init__(self, priority, data):
        self.priority = priority
        self.data = data
        self.next = None


class PriorityQueue:
    """
    Hàng đợi ưu tiên (Min-PriorityQueue) dùng cho AI của Tháp.

    Tháp dùng PriorityQueue để xếp hạng các quái vật trong tầm bắn:
    priority nhỏ hơn = ưu tiên cao hơn = được bắn trước.

    Cài đặt theo dạng danh sách liên kết đã sắp xếp (sorted linked list).
    Không sử dụng heapq hay bất kỳ thư viện ngoài nào.
    """

    def __init__(self):
        """Khởi tạo hàng đợi ưu tiên rỗng. Time O(1)."""
        self.head = None
        self.size = 0

    def push(self, priority, data):
        """
        Thêm phần tử vào đúng vị trí theo priority tăng dần.

        Tham số:
            priority (float): Giá trị ưu tiên (nhỏ = ưu tiên cao hơn).
            data: Đối tượng cần thêm.

        Độ phức tạp: Time O(n) | Space O(1)
        """
        new_node = PriorityQueueNode(priority, data)
        if self.head is None or priority < self.head.priority:
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            while current.next is not None and current.next.priority <= priority:
                current = current.next
            new_node.next = current.next
            current.next = new_node
        self.size += 1

    def pop(self):
        """
        Lấy và xóa phần tử có ưu tiên cao nhất (priority nhỏ nhất).

        Trả về:
            tuple: (priority, data) — cặp độ ưu tiên và đối tượng.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        if self.is_empty():
            raise IndexError("Pop từ hàng đợi ưu tiên rỗng.")
        priority = self.head.priority
        data = self.head.data
        self.head = self.head.next
        self.size -= 1
        return (priority, data)

    def peek(self):
        """
        Xem phần tử ưu tiên cao nhất mà không xóa.

        Trả về:
            tuple: (priority, data) — cặp độ ưu tiên và đối tượng.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.

        Độ phức tạp: Time O(1) | Space O(1)
        """
        if self.is_empty():
            raise IndexError("Peek từ hàng đợi ưu tiên rỗng.")
        return (self.head.priority, self.head.data)

    def is_empty(self):
        """Kiểm tra hàng đợi có rỗng không. Time O(1)."""
        return self.head is None

    def clear(self):
        """Xóa toàn bộ hàng đợi. Time O(1)."""
        self.head = None
        self.size = 0

    def __len__(self):
        """Trả về số phần tử. Time O(1)."""
        return self.size
