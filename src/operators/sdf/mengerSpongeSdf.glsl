// Based on Klems code https://www.shadertoy.com/view/XljSWm

ReturnT thismap(CoordT p, ContextT ctx) {
	CoordT p0 = p;
	p -= THIS_Translate;
	int n = int(THIS_Steps);
	float scale = THIS_Scale;
	float dist = 0.0;
	for (int i = 0; i < n; i++) {
		#ifdef THIS_EXPOSE_step
		THIS_step = i;
		#endif
		#ifdef THIS_EXPOSE_normstep
		THIS_normstep = float(i) / float(n - 1);
		#endif
		#ifdef THIS_HAS_INPUT_boxScaleField
		float boxScale = inputOp_boxScaleField(p0, ctx);
		#else
		float boxScale = THIS_Boxscale;
		#endif
		#ifdef THIS_HAS_INPUT_crossScaleField
		float crossScale = inputOp_crossScaleField(p0, ctx);
		#else
		float crossScale = THIS_Crossscale;
		#endif
		dist = max(dist, mengerCrossDist(p, crossScale, boxScale)*scale);
		p = fract((p-1.0)*0.5) * 6.0 - 3.0;
		scale /= 3.0;
		#ifdef THIS_HAS_INPUT_stepOffsetField
		p -= fillToVec3(inputOp_stepOffsetField(p0, ctx));
		#else
		p -= THIS_Stepoffset;
		#endif
	}
	return createSdf(dist);
}