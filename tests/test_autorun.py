import sys
import types
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
pico = types.ModuleType('pico2d')
for value, name in enumerate([
    'SDL_KEYDOWN', 'SDL_KEYUP', 'SDLK_SPACE', 'SDLK_LEFT', 'SDLK_RIGHT', 'SDLK_a',
], 1):
    setattr(pico, name, value)
pico.get_time = lambda: 0.0
pico.get_canvas_width = lambda: 800
pico.load_image = lambda name: None
sys.modules['pico2d'] = pico

import boy as boy_module
import auto_run as auto_module


class AutoRunTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.draws = []
        self.image = types.SimpleNamespace(
            clip_draw=lambda *args: self.draws.append(args),
            clip_composite_draw=lambda *args: self.draws.append(args),
        )
        boy_module.get_time = lambda: self.now
        auto_module.get_time = lambda: self.now
        boy_module.load_image = lambda name: self.image
        self.boy = boy_module.Boy()

    def key(self, key, down=True, repeat=0):
        self.boy.handle_event(types.SimpleNamespace(
            type=pico.SDL_KEYDOWN if down else pico.SDL_KEYUP,
            key=key, repeat=repeat,
        ))

    def activate(self):
        self.key(pico.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTO_RUN')

    def test_a_starts_a_dedicated_state_class(self):
        self.activate()
        self.assertIsInstance(self.boy.auto_run, auto_module.AutoRun)

    def test_automatic_speed_is_twice_normal_run(self):
        self.activate()
        self.boy.update()
        self.assertEqual(self.boy.x, 406)
        self.key(pico.SDLK_LEFT)
        self.boy.update()
        self.assertEqual(self.boy.x, 403)

    def test_enlarged_size_returns_to_normal_after_cancel(self):
        self.activate()
        self.boy.draw()
        self.assertEqual(self.draws[-1][-2:], (150, 150))
        self.key(pico.SDLK_RIGHT)
        self.boy.draw()
        self.assertEqual(len(self.draws[-1]), 6)
        self.assertEqual(self.draws[-1][2:4], (100, 100))

    def test_entry_remembers_facing_and_clamps_enlarged_body(self):
        self.boy.face_dir = -1
        self.boy.x = 50
        self.activate()
        self.assertEqual(self.boy.x, 75)
        self.assertEqual(self.boy.auto_run.direction, -1)

    def test_right_edge_reverses_and_then_moves_left(self):
        self.activate()
        self.boy.x = 724
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.face_dir), (725, -1))
        self.boy.update()
        self.assertEqual(self.boy.x, 719)

    def test_left_edge_reverses_and_then_moves_right(self):
        self.boy.face_dir = -1
        self.activate()
        self.boy.x = 76
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.face_dir), (75, 1))
        self.boy.update()
        self.assertEqual(self.boy.x, 81)

    def test_repeated_bounces_keep_the_enlarged_sprite_on_screen(self):
        self.activate()
        for _ in range(1000):
            self.boy.update()
            self.assertGreaterEqual(self.boy.x - 75, 0)
            self.assertLessEqual(self.boy.x + 75, 800)



if __name__ == '__main__':
    unittest.main()
