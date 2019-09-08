import cairo
import os

class CairoBind:
    def __init__(self, W=300, H=300):
        self.WIDTH = W
        self.HEIGHT = H
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
        self.ctx = cairo.Context(self.surface)

    def move_to(self,x, y):
        self.ctx.move_to(x,y)

    def line_to(self,x, y):
        self.ctx.line_to(x,y)        

    def close_path(self):
        self.ctx.close_path()

    def set_line_width(self, lw):
        self.ctx.set_line_width(lw)

    def fill(self):
        self.ctx.fill()

    def stroke(self):
        self.ctx.stroke()

    def rectangle(self,x0,y0,x1,y1):
        self.ctx.rectangle(x0,y0,x1,y1)

    def set_source_rgba(self, r=0, g=0, b=0, a=1):
        self.ctx.set_source_rgba(r,g,b,a)

    def write_to_png(self, fname='./img/test.png'):
        if not os.path.exists('/'.join(fname.split('/')[:-1])):
            os.mkdirs(fname)
        self.surface.write_to_png(fname)
