class Coord:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, coord):
        ret = Coord()

        ret.x = self.x + coord.x
        ret.y = self.y + coord.y
        ret.z = self.z + coord.z

        return ret

    def __sub__(self, coord):
        ret = Coord()

        ret.x = self.x - coord.x
        ret.y = self.y - coord.y
        ret.z = self.z - coord.z

        return ret