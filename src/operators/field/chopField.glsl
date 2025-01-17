ReturnT thismap(CoordT p, ContextT ctx) {
	#if defined(THIS_HAS_INPUT_coordField)
	vec3 q = adaptAsVec3(inputOp_coordField(p, ctx));
	#else
	vec3 q = adaptAsVec3(p);
	#endif
	float u = getAxis(q, int(THIS_Axis));
	vec4 value;
	#if defined(THIS_Coordmode_indextexel)
	{
		int i = int(u);
		#if defined(THIS_Extendmode_hold)
		i = clamp(i, 0, int(THIS_Length - 1));
		#elif defined(THIS_Extendmode_repeat)
		i = int(mod(i, int(THIS_Length)));
		#elif defined(THIS_Extendmode_mirror)
		i = int(modZigZag(u / (THIS_Length - 1)) * (THIS_Length - 1));
		#elif defined(THIS_Extendmode_zero)
		if (i < 0 || i >= int(THIS_Length)) {
			ReturnT res;
			initDefVal(res);
			return res;
		}
		#endif
		value = texelFetch(THIS_texture, ivec2(i, 0), 0);
	}
	#else
	{
		#if defined(THIS_Coordmode_position)
		u = (u - THIS_Translate) / THIS_Scale;
		#elif defined(THIS_Coordmode_scaledindex)
		u = map01(u,  THIS_Indexrange.x, THIS_Indexrange.y);
		#elif defined(THIS_Coordmode_scaledindex)
		u = map01(u, 0, THIS_Length - 1);
		#endif

		#if defined(THIS_Extendmode_hold)
		u = clamp(u, 0, 1);
		#elif defined(THIS_Extendmode_repeat)
		u = fract(u);
		#elif defined(THIS_Extendmode_mirror)
		u = modZigZag(u);
		#elif defined(THIS_Extendmode_zero)
		if (u < 0 || u > 1) {
			ReturnT res;
			initDefVal(res);
			return res;
		}
			#endif

		value = textureLod(THIS_texture, vec2(u, 0.), 0);
	}
	#endif
	return THIS_asReturnT(value);
}