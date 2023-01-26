import math

import pygame

pygame.font.init()
fonts = 'Helvetica Neue,Helvetica,Ubuntu Sans,Bitstream Vera Sans,DejaVu Sans,Latin Modern Sans,Liberation Sans,' \
        'Nimbus Sans L,Noto Sans,Calibri,Futura,Beteckna,Arial'


class Widget(object):
    fields = []

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.surface = pygame.Surface((rect.width, rect.height), pygame.HWSURFACE)
        for n in self.fields:
            setattr(self, n, None)

    def update(self, data: dict) -> bool:
        res = False
        for n in self.fields:
            if getattr(self, n) != data.get(n):
                res = True
                setattr(self, n, data.get(n))
        return res

    def prepare(self):
        pass

    def draw(self, surf: pygame.Surface):
        surf.blit(self.surface, (self.rect.x, self.rect.y))


class DisplayGyro(Widget):
    BG = (20, 20, 20)
    COL = (255, 255, 255)
    LCOL = (100, 100, 100)
    fields = ['pitch', 'roll']
    font = pygame.font.SysFont(fonts, 24)

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

        s1 = box_text(self.font, "%.0f" % self.roll, box_w, box_h, self.COL, self.BG)
        self.surface.blit(s1, (xc - box_w /2, 2))

        s2 = box_text(self.font, "%.0f" % self.pitch, box_w, box_h, self.COL, self.BG, 270)
        self.surface.blit(s2, (self.rect.width - box_h - 2, yc - box_w / 2))

class Compass(Widget):
    BG = (20, 20, 20)
    COL = (255, 255, 255)
    fields = ['yaw']
    font = pygame.font.SysFont(fonts, 24)
    font2 = pygame.font.SysFont(fonts, 18)
    box_w = 60
    box_h = 36

    def __init__(self, rect: pygame.Rect):
        super().__init__(rect)
        self.besel = pygame.Surface((self.rect.width, self.rect.height))
        self.besel.fill(self.BG)

        x, y = self.rect.center
        xc, yc = min(x, y), min(x, y)
        r = xc - self.box_h - 4

        pygame.draw.circle(self.besel, self.COL, (xc, yc), r, 2)

        for a in range(0, 360, 10):
            n = 20 if a % 90 ==0 else 10
            x1 = xc + (r-n) * math.cos(a*math.pi/180)
            x2 = xc + r * math.cos(a*math.pi/180)
            y1 = yc - (r-n) * math.sin(a*math.pi/180)
            y2 = yc - r * math.sin(a*math.pi/180)
            pygame.draw.line(self.besel, self.COL, (x1, y1), (x2, y2), 2)

        img1 = self.font2.render('N', True, self.COL)
        a, b = img1.get_rect().center
        self.besel.blit(img1, (xc - a, yc - r + 20))

        img1 = pygame.transform.rotate(self.font2.render('S', True, self.COL), 180)
        a, b = img1.get_rect().center
        self.besel.blit(img1, (xc -a, yc +r - 2*b -20))

        img1 = pygame.transform.rotate(self.font2.render('E', True, self.COL), 270)
        a, b = img1.get_rect().center
        self.besel.blit(img1, (xc +r - 2*a -20 , yc - b))

        img1 = pygame.transform.rotate(self.font2.render('W', True, self.COL), 90)
        a, b = img1.get_rect().center
        self.besel.blit(img1, (xc -r +20 , yc - b))

    def prepare(self):
        self.surface.fill(self.BG)
        s1 = pygame.transform.rotate(self.besel, self.yaw)
        r = s1.get_rect()
        self.surface.blit(s1, ((self.rect.width-r.width)/2, (self.rect.height-r.height)/2))

        x, y = self.rect.center
        xc, yc = min(x, y), min(x, y)
        s1 = box_text(self.font, "%.0f" % self.yaw, self.box_w, self.box_h, self.COL, self.BG)
        self.surface.blit(s1, (xc - self.box_w /2, 2))

def box_text(font :pygame.font, text, w, h, col, bg, ang=0):
    surf = pygame.Surface((w, h))
    surf.fill(bg)
    pygame.draw.rect(surf, col, (0,0,w,h), 2)
    img1 = font.render(text, True, col)
    r1 = img1.get_rect()
    surf.blit(img1, ((w - r1.width) / 2, (h - r1.height) / 2))
    if ang > 0:
        return pygame.transform.rotate(surf, ang)
    return surf

