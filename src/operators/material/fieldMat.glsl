Sdf thismap(CoordT p, ContextT ctx) {
	Sdf res = inputOp1(p, ctx);
	#if defined(THIS_Uselocalpos) && defined(RAYTK_USE_MATERIAL_POS)
	assignMaterialWithPos(res, THISMAT, p);
	#else
	assignMaterial(res, THISMAT);
	#endif
	return res;
}

vec3 THIS_getColor(vec3 p, MaterialContext matCtx) {
	vec3 mp = getPosForMaterial(p, matCtx);
	#if defined(inputOp2_RETURN_TYPE_vec4)
	return inputOp2(mp, matCtx).rgb;
	#elif defined(inputOp2_RETURN_TYPE_float)
	return vec3(inputOp2(mp, matCtx));
	#else
	#error invalidFieldReturnType
	#endif
}
