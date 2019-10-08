package postprocess

import org.eclipse.emf.common.util.URI
import org.eclipse.emf.ecore.resource.Resource
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl
import testcase.TestcasePackage
import testcase.Lane
import java.util.ArrayList
import testcase.Scenario
import testcase.RoadSegment
import testcase.RoadComponent

class Pair {
	Lane a = null
	Lane b = null
	RoadSegment c = null
	
	new(Lane a, Lane b) {
		this.a = a
		this.b = b
	}
	
	new(Lane a, RoadSegment c) {
		this.a = a
		this.c = c
	}
	
	def getA() {
		a
	}
	
	def getB() {
		b
	}
	
	override toString() {
		if (b !== null) {
			"(" + a.name + ", " + b.name + ")"
		}
		else {
			"(" + a.name + ", " + c.name + ")"
		}
	}
}

class PrintRelations {
	
	static ArrayList<String> allSegments = new ArrayList<String>
	static ArrayList<String> straight = new ArrayList<String>
	static ArrayList<String> notStraight = new ArrayList<String>
	static ArrayList<String> allLanes = new ArrayList<String>
	static ArrayList<Pair> inRoadSegmentList = new ArrayList<Pair>
	static ArrayList<Pair> nextToFromLeftList = new ArrayList<Pair>
	static ArrayList<Pair> nextToFromLeftOppositeList = new ArrayList<Pair>
	static ArrayList<Pair> joinsList = new ArrayList<Pair>
	
	def loadModel(String path) {
		val resSet = new ResourceSetImpl()
        val resource = resSet.getResource(URI.createURI(path), true)
        resource.contents.head as Scenario
	}
	
	def static get_opposite_lanes(RoadSegment roadsegment) {
		var Lane f
		var Lane b
		for (roadcomponent : roadsegment.forward) {
			if (roadcomponent instanceof Lane && roadcomponent.leftLane === null) {
				if (f === null) {
					f = roadcomponent as Lane
				}
				else {
					return null
				}
			}
		}
		for (roadcomponent : roadsegment.backward) {
			if (roadcomponent instanceof Lane && roadcomponent.leftLane === null) {
				if (b === null) {
					b = roadcomponent as Lane
				}
				else {
					return null
				}
			}
		}
		if (f !== null && b !== null) {
			return new Pair(f, b)
		}
	}
	
	def static void collectLeftLane(RoadComponent roadcomponent) {
		if (roadcomponent.leftLane !== null) {
			nextToFromLeftList.add(new Pair(roadcomponent as Lane, roadcomponent.leftLane as Lane))
		}
	}
	
	
	def static void collecttToLane(RoadComponent roadcomponent) {
		if ((roadcomponent as Lane).toLane !== null) {
			var toLanes = (roadcomponent as Lane).toLane
			for (toLane : toLanes) {
				joinsList.add(new Pair(roadcomponent as Lane, toLane as Lane))
			}
		}
	}	
	
	def static void main(String[] args) {
		// Init
		TestcasePackage.eINSTANCE.eClass
		Resource.Factory.Registry.INSTANCE.extensionToFactoryMap.put("xmi",new XMIResourceFactoryImpl())
		val printer = new PrintRelations
		//val model = printer.loadModel("model/2_long_straight_2_lanes.xmi")
		//val model = printer.loadModel("model/3_way_intersection_double_lane2.xmi")
		
		for (var i = 1; i <= 10; i++) {
			
			allSegments = new ArrayList<String>
			straight = new ArrayList<String>
			notStraight = new ArrayList<String>
			allLanes = new ArrayList<String>
			inRoadSegmentList = new ArrayList<Pair>
			nextToFromLeftList = new ArrayList<Pair>
			nextToFromLeftOppositeList = new ArrayList<Pair>
			joinsList = new ArrayList<Pair>
			
			val model = printer.loadModel("output/output/" + i + ".xmi")
			var segmentNumbering = 1
			var laneNumbering = 1
			
			
			for (roadsegment : model.roadsegment) {
				roadsegment.name = "segment" + segmentNumbering++
				allSegments.add(roadsegment.name)
				
				
				for (roadcomponent : roadsegment.forward) {
					collectLeftLane(roadcomponent)
					collecttToLane(roadcomponent)
					roadcomponent.name = "lane" + laneNumbering++
					allLanes.add(roadcomponent.name)
					if ((roadcomponent as Lane).isStraight) {
						straight.add(roadcomponent.name)
					}
					else {
						notStraight.add(roadcomponent.name)
					}
					inRoadSegmentList.add(new Pair(roadcomponent as Lane, roadsegment))
				}
				for (roadcomponent : roadsegment.backward) {
					collectLeftLane(roadcomponent)
					collecttToLane(roadcomponent)
					roadcomponent.name = "lane" + laneNumbering++
					allLanes.add(roadcomponent.name)
					if ((roadcomponent as Lane).isStraight) {
						straight.add(roadcomponent.name)
					}
					else {
						notStraight.add(roadcomponent.name)
					}
					inRoadSegmentList.add(new Pair(roadcomponent as Lane, roadsegment))
				}
				var opposite = get_opposite_lanes(roadsegment)
				if (opposite !== null) {
					nextToFromLeftOppositeList.add(opposite)
				}
			}
		
			println(i + ".xmi")
			print("lanes: ")
			println(allLanes)
			print("straight lanes: ")
			println(straight)
			print("not straight lanes: ")
			println(notStraight)
			print("left: ")
			println(nextToFromLeftList)
			print("left opposite: ")
			println(nextToFromLeftOppositeList)
			print("joins: ")
			println(joinsList)
			print("roadsegments: ")
			println(allSegments)
			print("in roadsegment: ")
			println(inRoadSegmentList)
			println()
			println("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			println()
		}
	}
}