ReturnT thismap(CoordT p, ContextT ctx) {
	#if defined(THIS_SHAPE_equilateral)
	return createSdf(sdEquilateralTriangle(p / THIS_Radius));
	#elif defined(THIS_SHAPE_isosceles)
	return createSdf(sdTriangleIsosceles(p, vec2(THIS_Width, THIS_Height)));
	#elif defined(THIS_SHAPE_arbitrary)
	return createSdf(sdTriangle(p, THIS_Point1, THIS_Point2, THIS_Point3));
	#else
	#error invalidTriangleShape
	#endif
}