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

    def test_timeout_at_five_seconds_and_fresh_idle_timer(self):
        self.activate()
        self.now = 4.999
        self.boy.update()
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.now = 5.0
        self.boy.update()
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.idle_start_time, 5.0)
        self.boy.draw()
        self.assertEqual(len(self.draws[-1]), 6)
        self.now = 9.999
        self.boy.update()
        self.assertEqual(self.boy.state, 'IDLE')
        self.now = 10.0
        self.boy.update()
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_either_arrow_cancels_in_the_pressed_direction(self):
        for key, direction in [(pico.SDLK_LEFT, -1), (pico.SDLK_RIGHT, 1)]:
            with self.subTest(direction=direction):
                self.boy = boy_module.Boy()
                self.activate()
                self.key(key)
                self.assertEqual(self.boy.state, 'RUN')
                self.assertEqual(self.boy.dir, direction)
                self.key(key, down=False)
                self.assertEqual(self.boy.state, 'IDLE')

    def test_a_is_ignored_outside_idle(self):
        self.key(pico.SDLK_RIGHT)
        self.key(pico.SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')
        self.key(pico.SDLK_RIGHT, down=False)
        self.now = 5.0
        self.boy.update()
        self.key(pico.SDLK_a)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_a_key_repeat_does_not_restart_after_timeout(self):
        self.activate()
        self.now = 5.0
        self.boy.update()
        self.key(pico.SDLK_a, repeat=1)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_sleep_and_overlapping_arrow_controls_are_preserved(self):
        self.now = 5.0
        self.boy.update()
        self.assertEqual(self.boy.state, 'SLEEP')
        self.key(pico.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')
        self.key(pico.SDLK_LEFT)
        self.key(pico.SDLK_RIGHT)
        self.key(pico.SDLK_RIGHT, down=False)
        self.assertEqual((self.boy.state, self.boy.dir), ('RUN', -1))
        self.key(pico.SDLK_LEFT, down=False)
        self.assertEqual(self.boy.state, 'IDLE')


if __name__ == '__main__':
    unittest.main()
