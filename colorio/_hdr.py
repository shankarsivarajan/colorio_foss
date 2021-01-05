import numpy

from ._linalg import dot, solve


def _xyy_to_xyz100(xyy):
    x, y, Y = xyy
    return numpy.array([Y / y * x, Y, Y / y * (1 - x - y)]) * 100


class HdrLinear:
    """
    RGB color space from the Rec. 2020. Same as Rec. 2100, used in HDR. The
    primary colors are monochromatic at wave lengths 467nm, 532nm, and 630nm.

    <https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2020-2-201510-I!!PDF-E.pdf>.
    """

    def __init__(self):
        # The Y-coordinate is guessed, it does not explicitly appear in the spec.
        primaries_xyy = numpy.array(
            [[0.708, 0.292, 1 / 3], [0.170, 0.797, 1 / 3], [0.131, 0.046, 1 / 3]]
        )
        self.invM = _xyy_to_xyz100(primaries_xyy.T) / 100

        self.alpha = 1.09929682680944
        self.beta = 0.018053968510807

    def from_xyz100(self, xyz100):
        # TODO NaN the values smaller than 0 and larger than 1
        return solve(self.invM, xyz100 / 100)

    def to_xyz100(self, hdr_linear):
        return 100 * dot(self.invM, hdr_linear)

    # gamma corrections:
    def from_hdr1(self, hdr1):
        out = numpy.asarray(hdr1, dtype=float)

        is_smaller = out <= 4.5 * self.beta
        out[is_smaller] /= 4.5
        out[~is_smaller] = ((out[~is_smaller] + self.alpha - 1) / self.alpha) ** (
            1 / 0.45
        )
        return out

    def to_hdr1(self, hdr_linear):
        out = numpy.asarray(hdr_linear, dtype=float)

        is_smaller = hdr_linear <= self.beta
        out[is_smaller] *= 4.5
        out[~is_smaller] = self.alpha * out[~is_smaller] ** 0.45 - self.alpha + 1
        return out
