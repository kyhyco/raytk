ReturnT thismap(CoordT p, ContextT ctx) {
	#if defined(THIS_HAS_INPUT_coordField)
	float q = inputOp_coordField(p, ctx);
	#elif defined(THIS_Axis_dist)
	float q = length(p);
	#elif defined(THIS_COORD_TYPE_float)
	float q = p;
	#else
	float q = p.THIS_Axis;
	#endif
	q = abs(q - THIS_Center);
	float w = THIS_Width / 2.;
	#if !defined(THIS_Enableblending)
	float amt = step(w, q);
	#elif defined(THIS_HAS_INPUT_blendFunction)
	float amt = clamp(inputOp_blendFunction(clamp(map01(q - w, 0., THIS_Blending), 0., 1.), ctx), 0., 1.);
	#else
	float amt = smoothstep(0, THIS_Blending, q - w);
	#endif
	#ifdef THIS_HAS_INPUT_insideValue
	ReturnT inVal = THIS_asReturnT(inputOp_insideValue(p, ctx));
	#else
	ReturnT inVal = THIS_asReturnT(THIS_Insidevalue);
	#endif
	#ifdef THIS_HAS_INPUT_outsideValue
	ReturnT outVal = THIS_asReturnT(inputOp_outsideValue(p, ctx));
	#else
	ReturnT outVal = THIS_asReturnT(THIS_Outsidevalue);
	#endif
	return mix(inVal, outVal, amt);
}