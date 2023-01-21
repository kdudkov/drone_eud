# /usr/bin/env python3
import asyncio
import functools
import random
import time

import pygame

from widgets import DisplayGyro


class App(object):
    data = dict()
    widgets = []
    running = False

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.window = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption("EUD")
        pygame.display.set_allow_screensaver(False)

    def run(self):
        loop = asyncio.get_event_loop()
        self.widgets.append(DisplayGyro(pygame.Rect(0, 0, 250, 250)))
        self.running = True

        fut = asyncio.ensure_future(self.pygame_loop(), loop=loop)
        asyncio.ensure_future(self.cron(), loop=loop)

        loop.run_until_complete(fut)

    async def pygame_loop(self):
        last = time.time()

        while self.running:
            last = time.time()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                add_max(self.data, 'pitch', 0.5, -90, 90)

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_DOWN:
                add_max(self.data, 'pitch', -0.5, -90, 90)

            redraw = False
            for w in self.widgets:
                if w.update(self.data):
                    redraw = True
                    w.prepare()
                    w.draw(self.window)

            if redraw:
                pygame.display.flip()
            await asyncio.sleep(0.016)

    async def cron(self):
        random.seed()

        while self.running:
            self.data['roll'] = self.data.get('roll', 0.0) + float(random.randint(0, 100) - 50) / 20
            self.data['pitch'] = self.data.get('pitch', 0.0) + float(random.randint(0, 100) - 50) / 20

            await asyncio.sleep(0.2)

    def do_async(self, fn, *args):
        if asyncio.iscoroutinefunction(fn):
            asyncio.ensure_future(fn(*args), loop=self.loop)
        else:
            self.loop.call_soon(functools.partial(fn, *args))


class VideoSprite(pygame.sprite.Sprite):
    def __init__(self, rect, FPS=25):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((rect.width, rect.height), pygame.HWSURFACE)
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.last_at = 0
        self.frame_delay = 1000 / FPS

    def update(self):
        time_now = pygame.time.get_ticks()
        if time_now > self.last_at + self.frame_delay:
            self.last_at = time_now
            try:
                raw_image = self.proc.stdout.read(self.bytes_per_frame)
                self.image = pygame.image.frombuffer(raw_image, (self.rect.width, self.rect.height), 'RGB')
            except:
                self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.HWSURFACE)
                self.image.fill((0, 0, 0))


def add_max(d, key, v, minv, maxv):
    vv = d.get(key, 0) + v
    if minv <= vv <= maxv:
        d[key] = vv


if __name__ == '__main__':
    App().run()
