
import operator as op
import math
import cocos.euclid as eu
import cocos.collision_model as cm
import numpy as np


class OORectShape(cm.Cshape):
    """
    Implements the Cshape interface that uses rectangles with sides
    parallel to the coordinate axis as geometric shape.

    Distance is not the euclidean distance but the rectangular or max-min
    distance, max( min(x0 - x1), min(y0 - y1) : (xi, yi) in recti )

    Good if actors don't rotate.

    Look at Cshape for other class and methods documentation.
    """

    def __init__(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """
        :Parameters:
            `center` : euclid.Vector2
                rectangle center
            `half_width` : float
                half width of rectangle
            `half_height` : float
                half height of rectangle
        """
        self.center = x1 + x2 +x3 + x4 / 2, y1 + y2 +y3 + y4 / 2
        self.points = x1, y1, x2, y2, x3, y3, x4, y4


    def overlaps(self, other):
        if isinstance(other, cm.AARectShape):
            return oa_rect_overlaps_aa_rect(self, other)
        elif isinstance(other, cm.CircleShape):
            return oa_rect_overlaps_circle(self, other)
        elif isinstance(other, OORectShape):
            return oa_rect_overlaps_oa_rect(self, other)
        raise NotImplementedError(
            "Collision between AARectShape and {0} is not implemented".format(other.__class__.__name__))

    def distance(self, other):
        if isinstance(other, cm.AARectShape):
            return oa_rect_distance_aa_rect(self, other)
        elif isinstance(other, cm.CircleShape):
            return oa_rect_distance_circle(self, other)
        elif isinstance(other, OORectShape):
            return oa_rect_distance_oa_rect(self, other)
        raise NotImplementedError(
            "Distance between AARectShape and {0} is not implemented".format(other.__class__.__name__))

    def near_than(self, other, near_distance):
        return self.distance(other) <= near_distance

    def touches_point(self, x, y):
        # TODO this
        return (abs(self.center[0] - x) < self.rx and
                abs(self.center[1] - y) < self.ry)

    def fits_in_box(self, packed_box):
        # TODO this
        return ((packed_box[0] + self.rx <= self.center[0] <= packed_box[1] - self.rx) and
                (packed_box[2] + self.ry <= self.center[1] <= packed_box[3] - self.ry))

    def minmax(self):
        # TODO this
        return (self.center[0] - self.rx, self.center[0] + self.rx,
                self.center[1] - self.ry, self.center[1] + self.ry)

    def copy(self):
        # TODO this
        return OORectShape(eu.Vector2(*self.center), self.rx, self.ry)

def lineIntersectLine(a0, b0, a1, b1):
    # Two lines defined by points (a0, a1) and (b0, b1)
    # raise Exception("This methos is untested")
    det = np.array([
                 [a0[0], a0[1], a0[2], 1],
                 [a1[0], a1[1], a1[2], 1],
                 [b0[0], b0[1], b0[2], 1],
                 [b1[0], b1[1], b1[2], 1]
                 ])
    x = np.linalg.det(det)
    return x == 0.

def oa_rect_overlaps_aa_rect(self, other):
    # We are defined by points x1..4 and y1..4
    # They are defined by other.center =- other.rx other.ry
    oPoints = ((other.center+other.rx, other.center+other.ry),
               (other.center+other.rx, other.center-other.ry),
               (other.center-other.rx, other.center+other.ry),
               (other.center-other.rx, other.center-other.ry))
    pass

def oa_rect_overlaps_circle(self, other):
    pass

def oa_rect_overlaps_oa_rect(self, other):
    pass

def oa_rect_distance_aa_rect(self, other):
    pass

def oa_rect_distance_circle(self, other):
    pass
def oa_rect_distance_oa_rect(self, other):
    pass

