import math

import pygame

pygame.font.init()
fonts = 'Helvetica Neue,Helvetica,Ubuntu Sans,Bitstream Vera Sans,DejaVu Sans,Latin Modern Sans,Liberation Sans,' \
        'Nimbus Sans L,Noto Sans,Calibri,Futura,Beteckna,Arial'


class Widget(object):
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.surface = pygame.Surface((rect.width, rect.height), pygame.HWSURFACE)

    def update(self, data: dict) -> bool:
        pass

    def prepare(self):
        pass

    def draw(self, surf: pygame.Surface):
        surf.blit(self.surface, (self.rect.x, self.rect.y))


class DisplayGyro(Widget):
    BG = (20, 20, 20)
    COL = (255, 255, 255)
    LCOL = (100, 100, 100)
    pitch = None
    roll = None
    yaw = None
    font = pygame.font.SysFont(fonts, 24)

    def update(self, data: dict) -> bool:
        res = any((data.get('pitch', 0) != self.pitch, data.get('roll', 0) != self.roll, data.get('yaw', 0) != self.yaw))
        self.pitch = data.get('pitch', 0)
        self.roll = data.get('roll', 0)
        self.yaw = data.get('yaw', 0)
        return res

    def prepare(self):
        box_w = 60
        box_h = 36

        x, y = self.rect.center
        xc, yc = min(x, y), min(x, y)
        r = xc - box_h - 4

        self.surface.fill(self.BG)

        pygame.draw.line(self.surface, self.LCOL, (xc, yc - r), (xc, yc + r))
        pygame.draw.line(self.surface, self.LCOL, (xc - r, yc), (xc + r, yc))
        pygame.draw.circle(self.surface, self.COL, (xc, yc), r, 2)

        x1 = xc + r * self.roll / 90
        y1 = yc - r * self.pitch / 90
        pygame.draw.circle(self.surface, self.COL, (x1, y1), 8, 2)

        s1 = self.box_text("%.0f" % self.roll, box_w, box_h)
        self.surface.blit(s1, (xc - box_w /2, 2))

        s2 = self.box_text("%.0f" % self.pitch, box_w, box_h, 270)
        self.surface.blit(s2, (self.rect.width - box_h - 2, yc - box_w / 2))

    def box_text(self, text, w, h, ang=0):
        surf = pygame.Surface((w, h))
        surf.fill(self.BG)
        pygame.draw.rect(surf, self.COL, (0,0,w,h), 2)
        img1 = self.font.render(text, True, self.COL)
        r1 = img1.get_rect()
        surf.blit(img1, ((w - r1.width) / 2, (h - r1.height) / 2))
        if ang > 0:
            return pygame.transform.rotate(surf, ang)
        return surf
