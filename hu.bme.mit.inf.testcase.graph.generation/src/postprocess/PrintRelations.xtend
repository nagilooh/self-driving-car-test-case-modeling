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
import org.eclipse.viatra.query.runtime.emf.EMFScope
import org.eclipse.viatra.query.runtime.api.ViatraQueryEngine
import queries.TestCaseConstraints
import queries.RoadComponentOfRoadSegment
import testcase.TestcaseFactory
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl
import java.util.Collection
import org.eclipse.viatra.query.runtime.api.IPatternMatch
import testcase.StraightLane
import testcase.TurningLane

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

class SegmentOrder {
	RoadSegment center = null
	ArrayList<RoadSegment> segments = new ArrayList<RoadSegment>
	
	new(RoadSegment center) {
		this.center = center
	}
	
	def getCenter() {
		center
	}
	
	def getSegments() {
		segments
	}
	
	def String printSegments() {
		var s = ""
		for (segment : segments) {
			s += segment.name + ", "
		}
		s = s.substring(0, s.length() - 2)
		return s
	}
	
	def addSegment(RoadSegment segment) {
		segments.add(segment)
	}
	
	override toString() {
		"(" + center.name + "; " + printSegments + ")"
	}
}


class PrintRelations {
	
	static ArrayList<String> allSegments //= new ArrayList<String>
	static ArrayList<String> straight //= new ArrayList<String>
	static ArrayList<String> notStraight //= new ArrayList<String>
	static ArrayList<String> allLanes //= new ArrayList<String>
	static ArrayList<Pair> inRoadSegmentList //= new ArrayList<Pair>
	static ArrayList<Pair> nextToFromLeftList //= new ArrayList<Pair>
	static ArrayList<Pair> nextToFromLeftOppositeList //= new ArrayList<Pair>
	static ArrayList<Pair> joinsList //= new ArrayList<Pair>
	static ArrayList<SegmentOrder> connectionOrderList //= new ArrayList<SegmentOrder>
	
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
	
	def EMFScope initializeModelScope() {
		return new EMFScope(TestcasePackage.eINSTANCE.eResource.resourceSet)
	}	
	
	def static ViatraQueryEngine prepareQueryEngine(EMFScope scope) {
		// Access managed query engine
	    val engine = ViatraQueryEngine.on(scope)
	
	    // Initialize all queries on engine
		//TestCaseConstraints.instance().prepare(engine)
	
		return engine
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
			connectionOrderList = new ArrayList<SegmentOrder>
			
			val model = printer.loadModel("output/output-turns-100/" + i + ".xmi")
			var segmentNumbering = 1
			var laneNumbering = 1
			val engine = ViatraQueryEngine.on(new EMFScope(model.eResource))
			val matcher = RoadComponentOfRoadSegment.Matcher.on(engine)
			//Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("ecore", new EcoreResourceFactoryImpl());
			
			
			for (roadsegment : model.roadsegment) {
				roadsegment.name = "segment" + segmentNumbering++
				allSegments.add(roadsegment.name)
				var savedConnectionOrder = false
				
				for (roadcomponent : roadsegment.forward) {
					
					
					
					
					
					collectLeftLane(roadcomponent)
					collecttToLane(roadcomponent)
					roadcomponent.name = "lane" + laneNumbering++
					allLanes.add(roadcomponent.name)
					if (roadcomponent instanceof StraightLane) {
						straight.add(roadcomponent.name)
					}
					else if (roadcomponent instanceof TurningLane) {
						notStraight.add(roadcomponent.name)
						if (!savedConnectionOrder) {
							try {
								val order = new SegmentOrder(roadsegment)
								val fromlane = roadcomponent.fromLane.get(0)
								var matches = matcher.getAllValuesOfroadSegment(fromlane)
								val order_original = matches.get(0)
								order.addSegment(order_original)
								var next_segment = order_original.rightNeighborOfNeighbor
								while (next_segment != order_original) {
									order.addSegment(next_segment)
									next_segment = next_segment.rightNeighborOfNeighbor
								}
								connectionOrderList.add(order)
							
							
							}
							catch (Exception e) {
								println("Error")
							}
							
							savedConnectionOrder = true
						}
					}
					inRoadSegmentList.add(new Pair(roadcomponent as Lane, roadsegment))
				}
				for (roadcomponent : roadsegment.backward) {
					collectLeftLane(roadcomponent)
					collecttToLane(roadcomponent)
					roadcomponent.name = "lane" + laneNumbering++
					allLanes.add(roadcomponent.name)
					if (roadcomponent instanceof StraightLane) {
						straight.add(roadcomponent.name)
					}
					else if (roadcomponent instanceof TurningLane) {
						notStraight.add(roadcomponent.name)
						if (!savedConnectionOrder) {
							val order = new SegmentOrder(roadsegment)
							val fromlane = roadcomponent.fromLane.get(0)
							var matches = matcher.getAllValuesOfroadSegment(fromlane)
							val order_original = matches.get(0)
							order.addSegment(order_original)
							var next_segment = order_original.rightNeighborOfNeighbor
							while (next_segment != order_original) {
								order.addSegment(next_segment)
								next_segment = next_segment.rightNeighborOfNeighbor
							}
							connectionOrderList.add(order)
							savedConnectionOrder = true
						}
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
			print("connection order (clockwise): ")
			println(connectionOrderList)
			println()
			println("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
			println()
		}
	}
}