ReturnT thismap(CoordT p, ContextT ctx) {
	p -= THIS_Translate;
	p.yzx = p.THIS_AXIS_PLANE_SWIZZLE;
	float h = THIS_Height;
	float w = THIS_Width;
	#ifdef THIS_HAS_INPUT_1
	h *= inputOp1(p, ctx);
	#endif
	#ifdef THIS_HAS_INPUT_2
	w *= inputOp2(p, ctx);
	#endif
	p /= vec3(w, 1., w);
	float m2 = h*h + 0.25;

	p.xz = abs(p.xz);
	p.xz = (p.z>p.x) ? p.zx : p.xz;
	p.xz -= 0.5;

	vec3 q = vec3( p.z, h*p.y - 0.5*p.x, h*p.x + 0.5*p.y);

	float s = max(-q.x,0.0);
	float t = clamp( (q.y-0.5*p.z)/(m2+0.25), 0.0, 1.0 );

	float a = m2*(q.x+s)*(q.x+s) + q.y*q.y;
	float b = m2*(q.x+0.5*t)*(q.x+0.5*t) + (q.y-m2*t)*(q.y-m2*t);

	float d2 = min(q.y,-q.x*m2-q.y*0.5) > 0.0 ? 0.0 : min(a,b);

	return createSdf(sqrt( (d2+q.z*q.z)/m2 ) * sign(max(q.z,-p.y)));
}