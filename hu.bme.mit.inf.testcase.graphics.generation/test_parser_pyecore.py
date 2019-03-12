from pyecore.resources import ResourceSet


def main():
    rset = ResourceSet()
    resource = rset.get_resource("input/metamodel.ecore")
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root
    resource = rset.get_resource("input/model.xmi")
    model_root = resource.contents[0]
    print("Scenario:\t", model_root)
    for segment in model_root.roadsegment:
        print("Road:\t\t", segment)
        for component in segment.roadcomponent:
            if hasattr(component, 'fromLanes'):
                print("Lane:\t\t", component)
            else:
                print("Sidewalk:\t", component)


main()
