ReturnT thismap(CoordT p, ContextT ctx) {
	ReturnT res = inputOp1(p, ctx);
	float amt = THIS_Amount;
	#ifdef THIS_HAS_INPUT_2
	amt += inputOp2(p, ctx);
	#endif
	#ifdef THIS_RETURN_TYPE_Sdf
	res.x -= amt;
	#else
	res -= amt;
	#endif
	return res;
}