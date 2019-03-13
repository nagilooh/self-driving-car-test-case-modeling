from pyecore.resources import ResourceSet
import svgwrite
import math


class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    # 'other' must be a number Mat2!
    def __mul__(self, other):
        if isinstance(other, Mat2):
            return Vec2(self.x * other.m[0][0] + self.y * other.m[1][0],
                        self.x * other.m[0][1] + self.y * other.m[1][1])
        else:
            return Vec2(self.x * other, self.y * other)

    # 'other' must be a number!
    def __truediv__(self, other):
        return Vec2(self.x / other, self.y / other)

    def __str__(self):
        return "({0},{1})".format(self.x, self.y)


class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    # 'other' must be a number or Mat3!
    def __mul__(self, other):
        if isinstance(other, Mat3):
            return Vec3(self.x * other.m[0][0] + self.y * other.m[1][0] + self.z * other.m[2][0],
                        self.x * other.m[0][1] + self.y * other.m[1][1] + self.z * other.m[2][1],
                        self.x * other.m[0][2] + self.y * other.m[1][2] + self.z * other.m[2][2],)
        else:
            return Vec3(self.x * other, self.y * other, self.z * other)

    # 'other' must be a number!
    def __truediv__(self, other):
        return Vec3(self.x / other, self.y / other, self.z / other)

    def __str__(self):
        return "({0},{1},{2})".format(self.x, self.y, self.z)


# row-major matrix 2x2
class Mat2:
    def __init__(self,
                 m00=0, m01=0,
                 m10=0, m11=0):
        self.m = [[m00, m01], [m10, m11]]

    def __mul__(self, other):
        result = Mat2()
        for i in range(0, 1):
            for j in range(0, 1):
                for k in range(0, 1):
                    result.m[i][j] += self.m[i][k] * other.m[k][j]
        return result


# row-major matrix 2x2
class Mat3:
    def __init__(self,
                 m00=0, m01=0, m02=0,
                 m10=0, m11=0, m12=0,
                 m20=0, m21=0, m22=0):
        self.m = [[m00, m01, m02], [m10, m11, m12], [m20, m21, m22]]

    def __mul__(self, other):
        result = Mat3()
        for i in range(0, 2):
            for j in range(0, 2):
                for k in range(0, 2):
                    result.m[i][j] += self.m[i][k] * other.m[k][j]
        return result


# t must be Vec2
def translate_matrix(t):
    return Mat3(1, 0, 0,
                0, 1, 0,
                t.x, t.y, 1)


# s must be Vec2
def scale_matrix(s):
    return Mat3(s.x, 0, 0,
                0, s.y, 0,
                0, 0, 1)


def rotation_matrix(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return Mat3(c, -s, 0,
                s, c, 0,
                0, 0, 1)


class Drawable:
    def __init__(self, data=None):
        self.data = data

    def draw(self, target):
        target.add(target.text(self.data.name, insert=(self.data.startPos.x, self.data.startPos.y + 20), opacity=0.25))


class DrawableRoadsegment(Drawable):
    def __init__(self):
        Drawable.__init__(self)

    def draw(self, target):
        intersection = False
        for component in self.data.roadcomponent:
            if hasattr(component, "straight"):
                if not component.straight:
                    intersection = True

        if not intersection:
            for component in self.data.roadcomponent:
                component.drawable.draw(target)


class DrawableRoadcomponent(Drawable):
    def __init__(self):
        Drawable.__init__(self)

    def draw(self, target):
        Drawable.draw(self, target)


class DrawableLane(DrawableRoadcomponent):
    def __init__(self):
        DrawableRoadcomponent.__init__(self)

    def draw(self, target):
        DrawableRoadcomponent.draw(self, target)
        target.add(target.line((self.data.startPos.x, self.data.startPos.y),
                               (self.data.endPos.x, self.data.endPos.y),
                               stroke=svgwrite.rgb(10, 20, 16, '%')))
        start = self.data.startPos + Vec2(0, self.data.size.y)
        end = self.data.endPos + Vec2(0, self.data.size.y)
        target.add(target.line((start.x, start.y),
                               (end.x, end.y),
                               stroke=svgwrite.rgb(10, 20, 16, '%')))


class DrawableSidewalk(DrawableRoadcomponent):
    def __init__(self):
        DrawableRoadcomponent.__init__(self)

    def draw(self, target):
        DrawableRoadcomponent.draw(self, target)
        target.add(target.line((self.data.startPos.x, self.data.startPos.y),
                               (self.data.endPos.x, self.data.endPos.y),
                               stroke=svgwrite.rgb(100, 10, 16, '%')))
        start = self.data.startPos + Vec2(0, self.data.size.y)
        end = self.data.endPos + Vec2(0, self.data.size.y)
        target.add(target.line((start.x, start.y),
                               (end.x, end.y),
                               stroke=svgwrite.rgb(100, 10, 16, '%')))


class DrawableActor(Drawable):
    def __init__(self):
        Drawable.__init__(self)

    def draw(self, target):
        Drawable.draw(self, target)


class DrawableCar(DrawableActor):
    def __init__(self):
        DrawableActor.__init__(self)

    def draw(self, target):
        DrawableActor.draw(self, target)


class DrawablePedestrian(DrawableActor):
    def __init__(self):
        DrawableActor.__init__(self)

    def draw(self, target):
        DrawableActor.draw(self, target)


class Sizes:
    laneWidth = 300
    laneHeight = 50
    sidewalkWidth = 300
    sidewalkHeight = 50
    carWidth = 80
    carHeight = 40
    pedestrianWidth = 20
    pedestrianHeight = 20
    crosswalkWidth = 50
    crosswalkHeight = 50
    gapWidth = 0
    gapHeight = 10


# For RoadComponents (Lanes and Sidewalks)
def set_component_position(component, start_pos=None, end_pos=None, center_pos=None):
    if hasattr(component, 'startPos'):
        return
    else:
        if start_pos is not None:
            component.startPos = start_pos
            component.endPos = component.startPos + Vec2(component.size.x, 0)
        elif end_pos is not None:
            component.endPos = end_pos
            component.startPos = component.endPos - Vec2(component.size.x, 0)
        elif center_pos is not None:
            component.startPos = center_pos - component.size / 2
            component.endPos = component.startPos + component.size
        else:
            print("Missing argument in set_component_position")
            return
        if hasattr(component, 'fromLane'):
            for lane in component.fromLane:
                set_component_position(lane, end_pos=component.startPos)
            for lane in component.toLane:
                set_component_position(lane, start_pos=component.endPos)
        if component.leftLane is not None:
            set_component_position(component.leftLane, start_pos=component.startPos -
                                   Vec2(0, component.size.y / 2 + Sizes.gapHeight + component.leftLane.size.y / 2))
        if component.rightLane is not None:
            set_component_position(component.rightLane, start_pos=component.startPos +
                                   Vec2(0, component.size.y / 2 + Sizes.gapHeight + component.rightLane.size.y / 2))


# For NOT RoadComponents (Actors, Signs)
def set_position_center(component, center_pos=Vec2(0, 0)):
    component.centerPos = center_pos
    component.startPos = component.centerPos - Vec2(component.size.x / 2, 0)
    component.endPos = component.startPos + Vec2(component.size.x, 0)


def move_to_zero(root):
    min_x = 0
    min_y = 0
    for segment in root.roadsegment:
        for component in segment.roadcomponent:
            if component.startPos.x < min_x:
                min_x = component.startPos.x
            if component.startPos.y < min_y:
                min_y = component.startPos.y
    min_x -= 50
    min_y -= 50
    if min_x < 0 or min_y < 0:
        for segment in root.roadsegment:
            for component in segment.roadcomponent:
                component.startPos = component.startPos - Vec2(min_x, min_y)
                component.endPos = component.endPos - Vec2(min_x, min_y)
                # print(component.startPos, component.endPos)


def main():
    # metamodel_name = "metamodel.ecore"
    metamodel_name = "testtrack_modeling_dynamic.ecore"
    # model_name = "model.xmi"
    # model_name = "crosswalk_double_lane.testtrack_modeling_dynamic"
    # model_name = "stopped_car_straight_double_lane_single_sidewalk.testtrack_modeling_dynamic"
    # model_name = "stopped_car_straigt_double_lane_double_sidewalk.testtrack_modeling_dynamic"
    model_name = "3_way_intersection_double_lane.testtrack_modeling_dynamic"
    # model_name = "4_way_intersection_double_lane.testtrack_modeling_dynamic"
    rset = ResourceSet()
    resource = rset.get_resource("input/" + metamodel_name)
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root
    resource = rset.get_resource("input/" + model_name)
    model_root = resource.contents[0]
    # print("Scenario:\t", model_root)
    for segment in model_root.roadsegment:
        drawable_segment = DrawableRoadsegment()
        drawable_segment.data = segment
        segment.drawable = drawable_segment
        # print("Road:\t\t", segment)
        for component in segment.roadcomponent:
            if hasattr(component, 'fromLane'):
                drawable_component = DrawableLane()
                component.size = Vec2(Sizes.laneWidth, Sizes.laneHeight)
                # print("Lane:\t\t", component)
            else:
                drawable_component = DrawableSidewalk()
                component.size = Vec2(Sizes.sidewalkWidth, Sizes.sidewalkHeight)
                # print("Sidewalk:\t", component)
            drawable_component.data = component
            component.drawable = drawable_component

    for actor in model_root.actor:
        if str(actor.type) == "CAR":
            drawable_actor = DrawableCar()
            actor.size = Vec2(Sizes.carWidth, Sizes.carHeight)
        else:
            drawable_actor = DrawablePedestrian()
            actor.size = Vec2(Sizes.pedestrianWidth, Sizes.pedestrianHeight)
        drawable_actor.data = actor
        actor.drawable = drawable_actor

    set_component_position(model_root.roadsegment[0].roadcomponent[0], start_pos=Vec2(0, 0))

    move_to_zero(model_root)

    frame_n = 0
    for frame in model_root.frame:
        dwg = svgwrite.Drawing("output/test" + str(frame_n) + ".svg", profile='tiny')
        for state in frame.state:
            roadcomponent = state.roadcomponent
            set_position_center(state.actor, roadcomponent.startPos + (roadcomponent.endPos - roadcomponent.startPos)/2)
        for segment in model_root.roadsegment:
            segment.drawable.draw(dwg)
        for actor in model_root.actor:
            actor.drawable.draw(dwg)
        dwg.save()
        frame_n += 1


main()
