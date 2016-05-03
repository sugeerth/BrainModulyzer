import visit
import bisect


"""
Provides colors for all the visualization views
"""
class VisItColorTable(object):
    def __init__(self, color_table_name):
        ct = visit.GetColorTable(color_table_name)
        if ct.smoothing != ct.Linear:
            raise Exception("Unimplemented interploation method!")
        self.positions = [ ct.GetControlPoints(i).position for i in range(ct.GetNumControlPoints()) ]
        self.colors = [ ct.GetControlPoints(i).colors for i in range(ct.GetNumControlPoints()) ]
        self.value_range = (0, 1)

    def setRange(self, vr):
        self.value_range = vr

    def getColor(self, value):
        value = (value - self.value_range[0]) / (self.value_range[1] - self.value_range[0])

        if value <= self.positions[0]:
            return self.colors[0]
        elif value >= self.positions[-1]:
            return self.colors[-1]
        else:
            np = bisect.bisect_left(self.positions, value)
            t0 = self.positions[np-1]
            t1 = self.positions[np]
            #assert(value > t0 and value < t1)
            c0 = self.colors[np-1]
            c1 = self.colors[np]
            t = (value - t0) / (t1 - t0)
            return tuple([(1-t)*a + t*b for a, b in zip(c0, c1)])

"""
Provides colors for all the visualization views
"""
class LinearColorTable(object):
    # FIXME: Hardcoding color table names is a bit of a hack
    def __init__(self, color_table_name):
        if color_table_name == 'blue_lightblue':
            self.color0 = (0, 127, 255, 255)
            self.color1 = (0, 255, 255, 255)
        elif color_table_name == 'red_yellow':
            self.color0 = (255, 255, 0, 255)
            self.color1 = (255, 0, 0, 255)
            
        else:
            raise KeyError('Unknown color table ' + color_table_name)
        self.value_range = (0, 1)

    def setRange(self, vr):
        self.value_range = vr

    def getColor(self, t):
        t = (t - self.value_range[0]) / (self.value_range[1] - self.value_range[0])
        return tuple([(1-t)*a + t*b for a, b in zip(self.color0, self.color1)])

"""
Provides colors for all the visualization views
"""
class PosNegColorTable(object):
    # FIXME: Hardcoding color table names is a bit of a hack
    def __init__(self):
       self.positive_color_table = LinearColorTable('red_yellow')
       self.negative_color_table = LinearColorTable('blue_lightblue')

    def setRange(self, vr):
       if (vr[0] > 0):
           self.positive_color_table.setRange(vr)
       elif (vr[1] < 0):
           self.negative_color_table.setRange((-vr[1], -vr[0]))
       else:
           self.negative_color_table.setRange((0, -vr[0]))
           self.positive_color_table.setRange((0, vr[1]))

    def getColor(self, t):
        if t == 0:
            return (255, 255, 255, 255)
        elif t < 0:
            return self.negative_color_table.getColor(-t)
        else:
            return self.positive_color_table.getColor(t)

def CreateColorTable(color_table_name):
    # FIXME: Hardcoding color table names is a bit of a hack
    if color_table_name == 'blue_lightblue_red_yellow':
        return PosNegColorTable()
    else:
        try:
            return LinearColorTable(color_table_name)
        except KeyError:
            return VisItColorTable(color_table_name)
