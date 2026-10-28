from pico2d import get_time, get_canvas_width


class AutoRun:
    SPEED = 6
    SCALE = 1.5
    DURATION = 5.0

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0
        self.direction = 1

    def enter(self):
        self.started_at = get_time()
        self.direction = self.boy.face_dir
        self.boy.frame = 0
        self.boy.pressed_keys.clear()
        half_width = 100 * self.SCALE / 2
        self.boy.x = max(half_width, min(self.boy.x, get_canvas_width() - half_width))

    def update(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        half_width = 100 * self.SCALE / 2
        left, right = half_width, get_canvas_width() - half_width
        self.boy.x += self.direction * self.SPEED
        if self.boy.x >= right:
            self.boy.x = right
            self.direction = -1
        elif self.boy.x <= left:
            self.boy.x = left
            self.direction = 1
        self.boy.face_dir = self.direction

    def draw(self):
        size = int(100 * self.SCALE)
        row = 100 if self.boy.face_dir == 1 else 0
        draw_y = self.boy.y + (size - 100) * 0.35
        self.boy.image.clip_draw(
            self.boy.frame * 100, row, 100, 100,
            self.boy.x, draw_y, size, size,
        )
