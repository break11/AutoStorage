
import math


# class Point2():
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

#     def __repr__(self): return f"{self.__class__.__name__} {self.x} {self.y}"

#     def __sub__(self, pt): return Point2( pt.x - self.x, pt.y - self.y )

#     def __add__(self, pt): return Point2( pt.x + self.x, pt.y + self.y )

#     def __eq__(self, pt): return math.isclose( self.x, pt.x ) and math.isclose( self.y, pt.y )

#     def to_list(self): return [self.x, self.y]

#     @classmethod
#     def from_list(cls, l):
#         x, y = l
#         return Point2(x, y)

class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vec): return Vector2(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec): return Vector2(self.x - vec.x, self.y - vec.y)

    def __mul__(self, vec): return self.cross(vec)

    def __eq__(self, pt): return math.isclose( self.x, pt.x, abs_tol=1e-9 ) and math.isclose( self.y, pt.y, abs_tol=1e-9 )

    def __repr__(self): return f"{self.__class__.__name__} {self.x} {self.y}"
    def __str__(self): return f"{self.x} {self.y}"

    def add(self, number): return Vector2( self.x + number, self.y + number )

    def multiply(self, number): return Vector2( self.x * number, self.y * number )

    def magnitude(self): return math.sqrt( self.x**2 + self.y**2 )

    def dot(self, vec): return self.x * vec.x + self.y * vec.y

    def unit(self): return Vector2( self.x / self.magnitude(), self.y / self.magnitude() )

    def angle(self, vec):
        cosA = self.dot(vec) / (self.magnitude() * vec.magnitude())
        cosA = min( max( -1, cosA), 1)
        # print(self.dot(vec), self.magnitude(), vec.magnitude(), cosA)
        return math.acos( cosA )

    def selfAngle( self ):
        u_vec = self.unit()
        rAngle = math.acos( u_vec.x ) if u_vec.y >= 0 else 2*math.pi - math.acos( u_vec.x )
        return rAngle

    def rotate(self, angle):
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)

        return Vector2(x, y)

    @classmethod
    def fromAngle( cls, angle ):
        angle = angle % (2*math.pi)
        # print (angle, math.sin(angle))
        x = math.cos(angle)
        y = math.sin(angle)
        return Vector2(x, y)
