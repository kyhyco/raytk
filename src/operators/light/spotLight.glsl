// https://www.shadertoy.com/view/wlcyzf
// https://learnopengl.com/Lighting/Light-casters

Light thismap(CoordT p, LightContext ctx) {
	Light light;
	light.pos = THIS_Position;
	light.color = THIS_Color * THIS_Intensity;
	#ifdef THIS_HAS_INPUT_colorField
	light.color *= fillToVec3(inputOp_colorField(p, ctx));
	#endif
	{
		vec3 spotDir = normalize(THIS_Direction);
		float innerCutoffCos = cos(radians(THIS_Coneangle));
		float outerCutoffCos = cos(radians(THIS_Coneangle + THIS_Conedelta));
		vec3 lightDir = light.pos - p;
		float d = length(lightDir);
		lightDir /= d;
		float theta = dot(-lightDir, spotDir);
		light.color *= clamp((theta - outerCutoffCos) / (innerCutoffCos - outerCutoffCos), 0.0, 1.0);
	}
	#ifdef THIS_Enableattenuation
	{
		float d = length(p - light.pos);
		float start = THIS_Attenuationstart;
		float end = THIS_Attenuationend;
		float atten = smoothstep(end, start, d);
		#ifdef THIS_HAS_INPUT_attenuationField
		light.color *= fillToVec3(inputOp_attenuationField(atten, ctx));
		#else
		light.color *= atten;
		#endif
	}
	#endif
	return light;
}