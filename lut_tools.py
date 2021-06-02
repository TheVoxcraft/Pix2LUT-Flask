import random

def get_header(grid_size):
    return f"""#LUT size
LUT_3D_SIZE {grid_size}

#data domain
DOMAIN_MIN 0.0 0.0 0.0
DOMAIN_MAX 1.0 1.0 1.0

#LUT data points
"""

class Scale1D:
    def __init__(self, domain_max, value_max=1.0):
        self.domain_max : float = domain_max
        self.value_max : float = value_max
        self.values = []
    
    def _scale_down(self, y : tuple) -> tuple:
        assert len(y) == 3
        return (y[0] / self.value_max, y[1] / self.value_max, y[2] / self.value_max)
    
    def _scale_up(self, y : tuple) -> tuple:
        assert len(y) == 3
        return (y[0] * self.value_max, y[1] * self.value_max, y[2] * self.value_max)

    def add(self, x, y):
        scaled_y  = self._scale_down(y) 
        self.values.append((x / self.domain_max, scaled_y))
        self.values.sort()

    def interpolate(self, z):
        minimum_under = 0.
        minimum_under_index = 0
        minimum_over = 1.
        minimum_over_index = -1
        for i,v in enumerate(self.values):
            x, y = v
            if x == z:
                return self._scale_up(y)
            if x < z:
                if minimum_under < x:
                    minimum_under = x
                    minimum_under_index = i
            elif x > z:
                if minimum_over > x:
                    minimum_over = x
                    minimum_over_index = i
        # Found closest indexes under and over z

        betweenZ = (z-minimum_under)/(minimum_over-minimum_under)

        under_data = self.values[minimum_under_index][1]
        over_data = self.values[minimum_over_index][1]

        interpolated = (
            under_data[0] + betweenZ * (over_data[0] - under_data[0]),
            under_data[1] + betweenZ * (over_data[1] - under_data[1]),
            under_data[2] + betweenZ * (over_data[2] - under_data[2])
        )

        return self._scale_up(interpolated)


def load_lut(path):
    with open(path) as fo:
        file = fo.readlines()
    
    file = [i.strip() for i in file]
    grid_size = -1
    firstlines = file[:64]
    for l in firstlines:
        if "LUT_3D_SIZE" in l:
            grid_size = int(l.strip().split(" ")[1])
            break
    assert grid_size > 0

    firstchars = []
    for c in file[:64]:
        if len(c) > 0:
            firstchars.append(c[0])
        else:
            firstchars.append(c)
    try:
        startpoint = min(firstchars.index('0'), firstchars.index('1'))
    except ValueError:
        startpoint = firstchars.index('0')

    return (file[startpoint:], grid_size)

def text_to_lut(txt):
    lut = []
    for l in txt:
        s = l.strip().split(" ")
        lut.append(tuple([float(i) for i in s]))
    return lut

def create_file(lut, grid_size):
    txt = get_header(grid_size)
    for i in lut:
        s = f"{i[0]:.6f} {i[1]:.6f} {i[2]:.6f}\n"
        txt+=s
    return txt

def save_to_file(lutstring, outputpath):
    with open(outputpath, "w") as fo:
        fo.write(lutstring)

def downscaler(lut, from_grid_size, to_grid_size):
    #fromsize = len(lut)
    #tosize = pow(to_grid_size, 3)
    assert from_grid_size > to_grid_size

    new_lut = []
    for grid in range(0, len(lut), from_grid_size):
        scaler = Scale1D(domain_max=from_grid_size)
        for i in range(from_grid_size):
            scaler.add(i, lut[grid+i])

        for i in range(to_grid_size):
            new_point = i/to_grid_size
            new_lut.append(scaler.interpolate(new_point))

    print(len(new_lut))

    return new_lut

def mix(a, b):
    c = []
    for i,j in zip(a,b):
        mix = (i[0]*.5+j[0]*.5, i[1]*.5+j[1]*.5, i[2]*.5+j[2]*.5)
        c.append(mix)
    return c

def rmix(a, b, offset_mix, offset_contrast):
    this_offset1 = .5 + (random.random()-0.5) * 2 * offset_mix
    this_offset2 = .5 + (random.random()-0.5) * 2 * offset_mix
    this_contrast = 1.05 + (random.random()-0.5) * 2 * offset_contrast
    c = []
    if len(a) == 511:
        a.append((1.0,1.0,1.0))
    if len(b) == 511:
        a.append((1.0,1.0,1.0))
    if (len(a) != len(b) ) and ( (len(a) + len(b)) != (512*2)) :
        #print("PROBLEM!", len(a),len(b))
        return None
    for i,j in zip(a,b):
        mix = ( max(min((i[0]*this_offset1 + j[0]*this_offset2) * this_contrast, 1), 0),
                max(min((i[1]*this_offset1 + j[1]*this_offset2) * this_contrast, 1), 0),
                max(min((i[2]*this_offset1 + j[2]*this_offset2) * this_contrast, 1), 0)
            )
        c.append(mix)
    if len(c) == 511:
        c.append((1.0,1.0,1.0))
    elif len(c) != 512:
        return None
    return c


if __name__ == '__main__':
    text_lut, grid_size = load_lut("Arabica 12.CUBE")
    lut = text_to_lut(text_lut)
    print(grid_size)
    downscaled = downscaler(lut, grid_size, 8)
    #save_to_file(create_file(downscaled, 8), "test.cube")

    '''
    scaler = Scale1D(domain_max=100)
    scaler.add(0, (0,0,0))
    scaler.add(50, (80,80,80))
    scaler.add(100, (100,100,100))
    #print(scaler.values)
    print(scaler.interpolate(0.25))'''
