import numpy

from ..illuminants import whitepoints_cie1931
from ._cielab import CIELAB
from ._color_space import ColorSpace


class CIELCH(ColorSpace):
    def __init__(self, whitepoint=whitepoints_cie1931["D65"]):
        super().__init__("CIELCH", ("L", "C", "h"), 0)
        self.cielab = CIELAB(whitepoint=whitepoint)

    def from_xyz100(self, xyz):
        L, a, b = self.cielab.from_xyz100(xyz)
        C = numpy.hypot(a, b)
        h = numpy.mod(numpy.arctan2(b, a), 2 * numpy.pi) / numpy.pi * 180
        return numpy.array([L, C, h])

    def to_xyz100(self, lch):
        L, C, h = lch
        h_ = h * numpy.pi / 180
        lab = numpy.array([L, C * numpy.cos(h_), C * numpy.sin(h_)])
        return self.cielab.to_xyz100(lab)
