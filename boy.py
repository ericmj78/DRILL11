from math import pi

from pico2d import (
    load_image, get_time, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT,
)
from transitions import Machine



class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.pressed_keys = []
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
            transitions=[
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE',
                 'after': 'start_idle'},
                {'trigger': 'start_running', 'source': ['IDLE', 'SLEEP'],
                 'dest': 'RUN', 'after': 'start_run'},
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE',
                 'after': 'start_idle'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        self.start_idle()

    def start_idle(self):
        self.frame = 0
        self.idle_start_time = get_time()

    def start_run(self):
        self.frame = 0

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        if event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.type == SDL_KEYDOWN:
                if event.key not in self.pressed_keys:
                    self.pressed_keys.append(event.key)
            elif event.key in self.pressed_keys:
                self.pressed_keys.remove(event.key)

            if self.pressed_keys:
                self.dir = -1 if self.pressed_keys[-1] == SDLK_LEFT else 1
                self.face_dir = self.dir
                if self.state != 'RUN':
                    self.start_running()
            elif self.state == 'RUN':
                self.dir = 0
                self.stop_running()
        elif self.state == 'SLEEP' and event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.wake_up()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if get_time() - self.idle_start_time >= 5.0:
                self.fall_asleep()
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x = max(50, min(self.x + self.dir * 3, get_canvas_width() - 50))

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            row = 300 if self.face_dir == 1 else 200
            rotation = pi / 2 if self.face_dir == 1 else -pi / 2
            self.image.clip_composite_draw(
                0, row, 100, 100, rotation, '', self.x, self.y - 25, 100, 100
            )
