from pyecore.resources import ResourceSet
import svgutils.transform as sg
import svgutils.compose as sc
import glob
import os


class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    # 'other' must be a number!
    def __truediv__(self, other):
        return Vec2(self.x / other, self.y / other)

    def __str__(self):
        return "({0},{1})".format(self.x, self.y)


class Drawable:
    def __init__(self, data=None, path=None):
        self.data = data
        self.path = path
        self.figure = None
        self.direction = 0

    def draw(self, target):
        self.figure = sg.fromfile(self.path)
        drawing = self.figure.getroot()
        # print("rotating: ", self.direction)
        if hasattr(self.data, 'type'):
            print("actor")
            drawing.rotate(- self.direction, x=int(self.figure.width) / 2, y=int(self.figure.height) / 2)
        start_pos = self.data.startPos
        drawing.moveto(start_pos.x, start_pos.y)
        target.append(drawing)


class DrawableRoadsegment(Drawable):
    def __init__(self):
        Drawable.__init__(self)

    def draw(self, target):
        for component in self.data.forward:
            component.drawable.draw(target)
        for component in self.data.backward:
            component.drawable.draw(target)
        for sign in self.data.sign:
            sign.drawable.draw(target)


class DrawableActor(Drawable):
    def __init__(self):
        Drawable.__init__(self)
        self.direction = 0

    def draw(self, target):
        self.figure = sg.fromfile(self.path)
        drawing = self.figure.getroot()
        start_pos = self.data.startPos
        drawing.moveto(start_pos.x, start_pos.y)
        target.append(drawing)


def set_road_figure(component):
    direction_beginning = component.direction_beginning
    direction_end = component.direction_end
    if hasattr(component, 'straight'):
        if direction_beginning % 360 == 0:
            if direction_end == 90:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn WN closed.svg")
                component.drawable.path = "Assets/Asset_Turn WN closed.svg"
            elif direction_end % 360 == 270:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn WS closed.svg")
                component.drawable.path = "Assets/Asset_Turn WS closed.svg"
            elif direction_end % 360 == 0:
                component.drawable.path = "Assets/Asset_Straight Lane WE closed.svg"
                component.drawable.figure = sg.fromfile("Assets/Asset_Straight Lane WE closed.svg")
        if direction_beginning % 360 == 90:
            if direction_end % 360 == 180:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn SW closed.svg")
                component.drawable.path = "Assets/Asset_Turn SW closed.svg"
            elif direction_end % 360 == 0:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn SE closed.svg")
                component.drawable.path = "Assets/Asset_Turn SE closed.svg"
            elif direction_end % 360 == 90:
                component.drawable.figure = sg.fromfile("Assets/Asset_Straight Lane SN closed.svg")
                component.drawable.path = "Assets/Asset_Straight Lane SN closed.svg"
        if direction_beginning % 360 == 180:
            if direction_end % 360 == 270:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn ES closed.svg")
                component.drawable.path = "Assets/Asset_Turn ES closed.svg"
            elif direction_end % 360 == 90:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn EN closed.svg")
                component.drawable.path = "Assets/Asset_Turn EN closed.svg"
            elif direction_end % 360 == 180:
                component.drawable.path = "Assets/Asset_Straight Lane EW closed.svg"
                component.drawable.figure = sg.fromfile("Assets/Asset_Straight Lane EW closed.svg")
        if direction_beginning % 360 == 270:
            if direction_end % 360 == 0:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn NE closed.svg")
                component.drawable.path = "Assets/Asset_Turn NE closed.svg"
            elif direction_end % 360 == 180:
                component.drawable.figure = sg.fromfile("Assets/Asset_Turn NW closed.svg")
                component.drawable.path = "Assets/Asset_Turn NW closed.svg"
            elif direction_end % 360 == 270:
                component.drawable.figure = sg.fromfile("Assets/Asset_Straight Lane NS closed.svg")
                component.drawable.path = "Assets/Asset_Straight Lane NS closed.svg"
    else:
        if direction_beginning % 180 == 0:
            component.drawable.path = "Assets/Asset_Straight Lane EW.svg"
            component.drawable.figure = sg.fromfile("Assets/Asset_Straight Lane EW.svg")
        elif direction_beginning % 180 == 90:
            component.drawable.path = "Assets/Asset_Straight Lane NS.svg"
            component.drawable.figure = sg.fromfile("Assets/Asset_Straight Lane NS.svg")


def set_road_direction(component, direction_beginning=None, direction_end=None):
    if hasattr(component, 'direction_beginning'):
        return

    component.direction_beginning = direction_beginning
    component.direction_end = direction_end

    if component.direction_beginning is None and component.direction_end is None:
        component.direction_beginning = 0

    if component.direction_beginning is not None:
        if hasattr(component, 'straight'):
            if component.straight:
                component.direction_end = component.direction_beginning
            elif component.fromLane[0].segment.rightNeighborOfNeighbor == component.toLane[0].segment:
                component.direction_end = (component.direction_beginning - 90) % 360
            elif component.fromLane[0].segment.leftNeighborOfNeighbor == component.toLane[0].segment:
                component.direction_end = (component.direction_beginning + 90) % 360
        else:
            component.direction_end = component.direction_beginning
    else:
        if hasattr(component, 'straight'):
            if component.straight:
                component.direction_beginning = component.direction_end
            elif component.fromLane[0].segment.rightNeighborOfNeighbor == component.toLane[0].segment:
                component.direction_beginning = (component.direction_end + 90) % 360
            elif component.fromLane[0].segment.leftNeighborOfNeighbor == component.toLane[0].segment:
                component.direction_beginning = (component.direction_end - 90) % 360
        else:
            component.direction_beginning = component.direction_end
    print("Setting direction: ", component.name, component.direction_beginning, component.direction_end)
    set_road_figure(component)

    if component.leftLane is not None:
        set_road_direction(component.leftLane, direction_beginning=component.direction_beginning % 360)

    if component.rightLane is not None:
        set_road_direction(component.rightLane, direction_beginning=component.direction_beginning % 360)

    if component.left is not None:
        set_road_direction(component.left, direction_beginning=(component.direction_beginning + 180) % 360)

    if hasattr(component, 'straight'):
        for lane in component.toLane:
            set_road_direction(lane, direction_beginning=component.direction_end)
        for lane in component.fromLane:
            set_road_direction(lane, direction_end=component.direction_beginning)


# For RoadComponents (Lanes and Sidewalks)
def set_tolane_position(component, toLane):
    if hasattr(component, 'toLane'):
            start_pos = None
            if toLane.direction_beginning % 360 == component.direction_end % 360 \
                    and toLane.direction_end % 360 == (component.direction_beginning + 180) % 360:
                print("Error! Turning lane cannot be followed by a lane turning in the opposite direction.")
            elif toLane.direction_beginning % 360 == 0:
                if (toLane.direction_end % 360 == 0 or toLane.direction_end % 360 == 270) \
                        and (component.direction_beginning % 360 == 0 or component.direction_beginning % 360 == 90):
                    start_pos = component.startPos + Vec2(int(component.drawable.figure.width), 0)
                elif toLane.direction_end % 360 == 90 or component.direction_beginning % 360 == 270:
                    start_pos = component.startPos + Vec2(int(component.drawable.figure.width),
                                                          int(component.drawable.figure.height) -
                                                          int(toLane.drawable.figure.height))
                else:
                    print("Error! Lane turn weird e.g. turns 180 1°")
            elif toLane.direction_beginning % 360 == 180:
                if (toLane.direction_end % 360 == 180 or toLane.direction_end % 360 == 270) \
                      and (component.direction_beginning % 360 == 180 or component.direction_beginning % 360 == 90):
                    start_pos = component.startPos + Vec2(- int(toLane.drawable.figure.width), 0)
                elif toLane.direction_end % 360 == 90 or component.direction_beginning % 360 == 270:
                    start_pos = component.startPos + Vec2(- int(toLane.drawable.figure.width),
                                                          int(component.drawable.figure.height) -
                                                          int(toLane.drawable.figure.height))
                else:
                    print("Error! Lane turn weird e.g. turns 180° 2")
            elif toLane.direction_beginning % 360 == 270:
                if (toLane.direction_end % 360 == 270 or toLane.direction_end % 360 == 0) \
                   and (component.direction_beginning % 360 == 270 or component.direction_beginning % 360 == 180):
                    start_pos = component.startPos + Vec2(0, int(component.drawable.figure.height))
                elif toLane.direction_end % 360 == 180 or component.direction_beginning % 360 == 0:
                    start_pos = component.startPos + Vec2(int(component.drawable.figure.width) -
                                                          int(toLane.drawable.figure.width),
                                                          int(component.drawable.figure.height))
                else:
                    print("Error! Lane turn weird e.g. turns 180° 3")
            elif toLane.direction_beginning % 360 == 90:
                if (toLane.direction_end % 360 == 90 or toLane.direction_end % 360 == 0) \
                     and (component.direction_beginning % 360 == 90 or component.direction_beginning % 360 == 180):
                    start_pos = component.startPos + Vec2(0, - int(toLane.drawable.figure.height))
                elif toLane.direction_end == 180 or component.direction_beginning % 360 == 0:
                    start_pos = component.startPos + Vec2(int(component.drawable.figure.width) -
                                                          int(toLane.drawable.figure.width),
                                                          - int(toLane.drawable.figure.height))
                else:
                    print("Error! Lane turn weird e.g. turns 180° 4")
            set_road_position(toLane, start_pos)


# For RoadComponents (Lanes and Sidewalks)
def set_fromlane_position(component, fromLane):
    if hasattr(component, 'fromLane'):
        start_pos = None
        if fromLane.direction_end % 360 == component.direction_beginning % 360 \
                and fromLane.direction_beginning % 360 == (component.direction_end + 180) % 360:
            print("Error! Turning lane cannot be followed by a lane turning in the opposite direction.")
        if fromLane.direction_end % 360 == 0:
            if (component.direction_end % 360 == 0 or component.direction_end % 360 == 270) \
                    and (fromLane.direction_beginning % 360 == 0 or fromLane.direction_beginning % 360 == 90):
                start_pos = component.startPos + Vec2(- int(fromLane.drawable.figure.width), 0)
            elif component.direction_end % 360 == 90 or fromLane.direction_beginning % 360 == 270:
                start_pos = component.startPos + Vec2(- int(fromLane.drawable.figure.width),
                                                      int(component.drawable.figure.height) -
                                                      int(fromLane.drawable.figure.height))
            else:
                print("Error! Lane turn weird e.g. turns 180° 5")
        elif fromLane.direction_end % 360 == 180:
            if (component.direction_end % 360 == 180 or component.direction_end % 360 == 270) \
                    and (fromLane.direction_beginning % 360 == 180 or fromLane.direction_beginning % 360 == 90):
                start_pos = component.startPos + Vec2(int(component.drawable.figure.width), 0)
            elif component.direction_end % 360 == 90 or fromLane.direction_beginning % 360 == 270:
                start_pos = component.startPos + Vec2(int(component.drawable.figure.width),
                                                      int(component.drawable.figure.height) -
                                                      int(fromLane.drawable.figure.height))
            else:
                print("Error! Lane turn weird e.g. turns 180° 6")
        elif fromLane.direction_end % 360 == 270:
            if (component.direction_end % 360 == 270 or component.direction_end % 360 == 0) \
                    and (fromLane.direction_beginning % 360 == 270 or fromLane.direction_beginning % 360 == 180):
                start_pos = component.startPos + Vec2(0, - int(fromLane.drawable.figure.height))
            elif component.direction_end % 360 == 180 or fromLane.direction_beginning % 360 == 0:
                start_pos = component.startPos + Vec2(int(component.drawable.figure.width) -
                                                      int(fromLane.drawable.figure.width),
                                                      - int(fromLane.drawable.figure.height))
            else:
                print("Error! Lane turn weird e.g. turns 180° 7")
        elif fromLane.direction_end % 360 == 90:
            if (component.direction_end % 360 == 90 or component.direction_end % 360 == 0) \
                    and (fromLane.direction_beginning % 360 == 90 or fromLane.direction_beginning % 360 == 180):
                start_pos = component.startPos + Vec2(0, int(component.drawable.figure.height))
            elif component.direction_end == 180 or fromLane.direction_beginning % 360 == 0:
                start_pos = component.startPos + Vec2(int(component.drawable.figure.width) -
                                                      int(fromLane.drawable.figure.width),
                                                      int(component.drawable.figure.height))
            else:
                print("Error! Lane turn weird e.g. turns 180° 8")
        set_road_position(fromLane, start_pos)


def set_left_lane_position(component, left_lane):
    start_pos = None
    if component.direction_beginning % 360 == 0:
        start_pos = component.startPos - Vec2(0, int(left_lane.drawable.figure.height))
    elif component.direction_beginning % 360 == 180:
        start_pos = component.startPos + Vec2(0, int(left_lane.drawable.figure.height))
    elif component.direction_beginning % 360 == 90:
        start_pos = component.startPos - Vec2(int(left_lane.drawable.figure.width), 0)
    elif component.direction_beginning % 360 == 270:
        start_pos = component.startPos + Vec2(int(left_lane.drawable.figure.width), 0)
    set_road_position(left_lane, start_pos)


def set_right_lane_position(component, right_lane):
    start_pos = None
    if component.direction_beginning % 360 == 0:
        start_pos = component.startPos + Vec2(0, int(right_lane.drawable.figure.height))
    elif component.direction_beginning % 360 == 180:
        start_pos = component.startPos - Vec2(0, int(right_lane.drawable.figure.height))
    elif component.direction_beginning % 360 == 90:
        start_pos = component.startPos + Vec2(int(right_lane.drawable.figure.width), 0)
    elif component.direction_beginning % 360 == 270:
        start_pos = component.startPos - Vec2(int(right_lane.drawable.figure.width), 0)
    set_road_position(right_lane, start_pos)


# For RoadComponents (Lanes and Sidewalks)
def set_road_position(component, start_pos):
    if hasattr(component, 'startPos'):
        return
    else:
        if start_pos is not None:
            component.startPos = start_pos

        print("Setting position: ", component.name, component.startPos)

        if hasattr(component, 'toLane'):
            for toLane in component.toLane:
                set_tolane_position(component, toLane)

            for fromLane in component.fromLane:
                set_fromlane_position(component, fromLane)

        if component.leftLane is not None:
            set_left_lane_position(component, component.leftLane)

        if component.rightLane is not None:
            if not component.straight:
                print("Error! Only straight lanes can have rightLane attribute.")
            else:
                set_right_lane_position(component, component.rightLane)

        opposite = get_opposite_lane(component)
        if opposite is not None:
            set_left_lane_position(component, opposite)


def get_opposite_lane(component):
    if not component.straight:
        return None
    else:
        opposites = []
        if component in component.segment.forward:
            for cmp in component.segment.backward:
                if cmp.leftLane is not None and cmp.straigh:
                    opposites.append(cmp)
        else:
            for cmp in component.segment.forward:
                if cmp.leftLane is not None and cmp.straigh:
                    opposites.append(cmp)
        if len(opposites) != 1:
            return None
        else:
            return opposites[0]


def set_sign_figure(sign):
    # TODO Create assets for signs
    if str(type(sign)) == "<class 'pyecore.ecore.SignsStop'>":
        sign.drawable.path = "Assets/Asset_Crosswalk.svg"
        sign.drawable.figure = sg.fromfile("Assets/Asset_Crosswalk.svg")
        # sign.drawable.path = "Assets/Asset_Stop.svg"
        # sign.drawable.figure = sg.fromfile("Assets/Asset_Stop.svg")
    elif str(type(sign)) == "<class 'pyecore.ecore.GiveWaySign'>":
        sign.drawable.path = "Assets/Asset_Crosswalk.svg"
        sign.drawable.figure = sg.fromfile("Assets/Asset_Crosswalk.svg")
        # sign.drawable.path = "Assets/Asset_Give_Way.svg"
        # sign.drawable.figure = sg.fromfile("Assets/Asset_Give_Way.svg")
    elif str(type(sign)) == "<class 'pyecore.ecore.Crosswalk'>":
        sign.drawable.path = "Assets/Asset_Crosswalk.svg"
        sign.drawable.figure = sg.fromfile("Assets/Asset_Crosswalk.svg")


def set_actor_figure(actor):
    # TODO Create assets for actors
    print(actor.type)
    if str(actor.type) == "CAR":
        actor.drawable.path = "Assets/Asset_Actor_Car.svg"
        actor.drawable.figure = sg.fromfile("Assets/Asset_Actor_Car.svg")
        print(actor.type)
    if str(actor.type) == "PEDESTRIAN":
        actor.drawable.path = "Assets/Asset_Actor_Pedestrian.svg"
        actor.drawable.figure = sg.fromfile("Assets/Asset_Actor_Pedestrian.svg")
        print(actor.type)
    # TODO Load assets for other actors


# For NOT RoadComponents (Actors, Signs)
def set_position(element, component):
    # TODO Place car in the correct position in turns
    # TODO Keep car facing the right direction when passing in the opposite lane
    element.startPos = component.startPos + \
                       Vec2(int(component.drawable.figure.width) / 2, int(component.drawable.figure.height) / 2) - \
                       Vec2(int(element.drawable.figure.width) / 2, int(element.drawable.figure.height) / 2)
    if hasattr(element, 'type') and str(element.type) == "CAR":
        element.drawable.direction = (component.direction_beginning + component.direction_end) / 2
        print("direction :", element.drawable.direction)


def move_to_zero(root):
    min_x = 0
    min_y = 0
    for segment in root.roadsegment:
        for component in segment.forward:
            if component.startPos.x < min_x:
                min_x = component.startPos.x
            if component.startPos.y < min_y:
                min_y = component.startPos.y
        for component in segment.backward:
            if component.startPos.x < min_x:
                min_x = component.startPos.x
            if component.startPos.y < min_y:
                min_y = component.startPos.y
    min_x -= 50
    min_y -= 50
    if min_x < 0 or min_y < 0:
        for segment in root.roadsegment:
            for component in segment.forward:
                component.startPos = component.startPos - Vec2(min_x, min_y)
            for component in segment.backward:
                component.startPos = component.startPos - Vec2(min_x, min_y)
            for sign in segment.sign:
                sign.startPos = sign.startPos - Vec2(min_x, min_y)


def get_size(root):
    max_x = 0
    max_y = 0
    for segment in root.roadsegment:
        for component in segment.forward:
            if component.startPos.x + int(component.drawable.figure.width) > max_x:
                max_x = component.startPos.x + int(component.drawable.figure.width)
            if component.startPos.y + int(component.drawable.figure.height) > max_y:
                max_y = component.startPos.y + int(component.drawable.figure.height)
        for component in segment.backward:
            if component.startPos.x + int(component.drawable.figure.width) > max_x:
                max_x = component.startPos.x + int(component.drawable.figure.width)
            if component.startPos.y + int(component.drawable.figure.height) > max_y:
                max_y = component.startPos.y + int(component.drawable.figure.height)
    return Vec2(max_x + 50, max_y + 50)


def load_model(root):
    # print("Scenario:\t", model_root)
    for segment in root.roadsegment:
        drawable_segment = DrawableRoadsegment()
        drawable_segment.data = segment
        segment.drawable = drawable_segment
        # print("Road:\t\t", segment)
        for component in segment.forward:
            component.segment = segment
            drawable_component = Drawable()
            drawable_component.data = component
            component.drawable = drawable_component
        for component in segment.backward:
            component.segment = segment
            drawable_component = Drawable()
            drawable_component.data = component
            component.drawable = drawable_component
        for sign in segment.sign:
            drawable_sign = Drawable()
            drawable_sign.data = sign
            sign.drawable = drawable_sign

    for actor in root.actor:
        drawable_actor = Drawable()
        drawable_actor.data = actor
        actor.drawable = drawable_actor
        set_actor_figure(actor)

    set_road_direction(root.roadsegment[0].forward[0], direction_beginning=0)
    set_road_position(root.roadsegment[0].forward[0], start_pos=Vec2(0, 0))

    for segment in root.roadsegment:
        for sign in segment.sign:
            set_sign_figure(sign)
            set_position(sign, sign.forRoadComponent)

    move_to_zero(root)


def draw_frames(root, name):
    print("Drawing: " + name)

    image_size = get_size(root)
    scale = 0.25

    frame_n = 0
    for frame in root.frame:
        print("Frame ", frame_n)
        dwg = sg.SVGFigure(image_size.y * scale, image_size.x * scale)
        for state in frame.state:
            set_position(state.actor, state.position)
        for segment in root.roadsegment:
            segment.drawable.draw(dwg)
        for actor in root.actor:
            print("act_dir: ", actor.drawable.direction)
            actor.drawable.draw(dwg)

        dwg.save("output/" + name + str(frame_n) + ".svg")
        svg = sg.fromfile("output/" + name + str(frame_n) + ".svg")
        originalsvg = sc.SVG("output/" + name + str(frame_n) + ".svg")
        originalsvg.scale(scale)
        dwg = sc.Figure(svg.height, svg.width, originalsvg)
        dwg.save("output/" + name + str(frame_n) + ".svg")
        frame_n += 1


def main():
    # Load drawing assets

    metamodel_name = "testtrack.ecore"
    model_names = []
    os.chdir("./input")
    for file in glob.glob("*.xmi"):
        model_names.append(file)
    rset = ResourceSet()
    resource = rset.get_resource(metamodel_name)
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root
    os.chdir("./..")

    for model in model_names:
        print(model)
        os.chdir("./input")
        resource = rset.get_resource(model)
        model_root = resource.contents[0]
        os.chdir("./..")
        load_model(model_root)
        draw_frames(model_root, model)


main()
