uniform vec3 uCamPos;
uniform vec3 uCamRot;  // in radians
uniform float uCamFov;  // in radians

#ifndef THIS_USE_LIGHT_FUNC
uniform vec3 uLightPos1;
uniform vec3 uLightColor1 = vec3(1);
#endif

uniform float uUseRenderDepth;


Sdf map(vec3 q)
{
	Sdf res = thismap(q, createDefaultContext());
	res.x *= 0.5;
	return res;
}

Sdf castRay(Ray ray, float maxDist) {
	float dist = 0;
	Sdf res;
	int i;
	for (i = 0; i < RAYTK_MAX_STEPS; i++) {
		vec3 p = ray.pos + ray.dir * dist;
		res = map(p);
		dist += res.x;
		if (dist < RAYTK_SURF_DIST) {
			#ifdef RAYTK_STEPS_IN_SDF
			res.steps = i + 1;
			#endif
			return res;
		}
		if (dist > maxDist) {
			break;
		}
	}
	res.x = dist;
	#ifdef RAYTK_STEPS_IN_SDF
	res.steps = i + 1;
	#endif
	return res;
}

vec3 calcNormal(in vec3 pos)
{
	vec2 e = vec2(1.0, -1.0)*0.5773*0.005;
	return normalize(
		e.xyy*map(pos + e.xyy).x +
		e.yyx*map(pos + e.yyx).x +
		e.yxy*map(pos + e.yxy).x +
		e.xxx*map(pos + e.xxx).x);
}

// Soft shadow code from http://iquilezles.org/www/articles/rmshadows/rmshadows.htm
float softShadow(vec3 p, MaterialContext matCtx)
{
//	float mint = uShadow.x;
//	float maxt = uShadow.y;
//	float k = uShadow.z;
	float mint = 0.1;
	float maxt = 2.0;
	float k = 0.5;  // hardness
	float res = 1.0;
	float ph = 1e20;
	for (float t=mint; t<maxt;)
	{
		float h = map(p + matCtx.ray.pos*t).x;
		if (h<0.001)
		return 0.0;
		float y = h*h/(2.0*ph);
		float d = sqrt(h*h-y*y);
		res = min(res, k*d/max(0.0, t-y));
		ph = h;
		t += h;
	}
	return res;
}

float calcShadow(in vec3 p, MaterialContext matCtx) {
	vec3 lightVec = normalize(matCtx.light.pos - p);
	Ray shadowRay = Ray(p+matCtx.normal * RAYTK_SURF_DIST*2., lightVec);
	float shadowDist = castRay(shadowRay, RAYTK_MAX_DIST).x;
	if (shadowDist < length(matCtx.light.pos - p)) {
		return 0.1;
	}
	return 1.0;
}

// compute ambient occlusion value at given position/normal
// Source - https://www.shadertoy.com/view/lsKcDD
float calcAO( in vec3 pos, in vec3 nor )
{
//	float occ = uAO.x;
//	float sca = uAO.y;
	float occ = 0.0;
	float sca = 1.0;
	// int n = int(uAO.z);
	int n = 4;
	for( int i=0; i<n; i++ )
	{
		float hr = 0.01 + 0.12*float(i)/4.0;
		vec3 aopos =  nor * hr + pos;
		Sdf res = map(aopos);
		float dd = res.x;
		occ += -(dd-hr)*sca;
		sca *= 0.95;
	}
	return clamp( 1.0 - 3.0*occ, 0.0, 1.0 );
}

vec3 getColorDefault(vec3 p, MaterialContext matCtx) {
	vec3 sunDir = normalize(matCtx.light.pos);
	float occ = calcAO(p, matCtx.normal);
	vec3 mate = vec3(0.28);
	vec3 sunColor = vec3(5.8, 4.0, 3.5);
	vec3 skyColor = vec3(0.5, 0.8, 0.9);
	float sunDiffuse = clamp(dot(matCtx.normal, sunDir), 0, 1.);
	float sunShadow = calcShadow(p+matCtx.normal*0.001, matCtx);
	float skyDiffuse = clamp(0.5+0.5*dot(matCtx.normal, vec3(0, 1, 0)), 0, 1);
	float sunSpec = pow(max(dot(-matCtx.ray.dir, matCtx.normal), 0.), 5) * 0.5;
	vec3 col = mate * sunColor * sunDiffuse * sunShadow;
	col += mate * skyColor * skyDiffuse;
	col += mate * sunColor * sunSpec;
	col *= mix(vec3(0.5), vec3(1.5), occ);
	return col;
}

vec3 getColorInner(vec3 p, MaterialContext matCtx, int m) {
	vec3 col = vec3(0);
//	#ifdef OUTPUT_DEBUG
//	debugOut.x = m;
//	#endif

	if (false) {}
	// #include <materialParagraph>

	else {
		col = getColorDefault(p, matCtx);
	}
	return col;
}

vec3 getColor(vec3 p, MaterialContext matCtx) {
	vec3 col = vec3(0);
	float ratio = matCtx.result.interpolant;
	int m1 = int(matCtx.result.material);
	int m2 = int(matCtx.result.material2);
	if (ratio <= 0) {
		return getColorInner(p, matCtx, m1);
	} else if (ratio >= 1) {
		return getColorInner(p, matCtx, m2);
	} else {
		vec3 col1 = getColorInner(p, matCtx, m1);
		vec3 col2 = getColorInner(p, matCtx, m2);
		return mix(col1, col2, ratio);
	}
}

#ifndef THIS_USE_CAM_FUNC

Ray getViewRay() {
	vec3 pos = uCamPos;
	vec2 resolution = uTDOutputInfo.res.zw;
	vec2 fragCoord = vUV.st*resolution;
	vec2 p = (-resolution+2.0*fragCoord.xy)/resolution.y;

	float aspect = resolution.x/resolution.y;
	float screenWidth = 2*(aspect);
	float distanceToScreen = (screenWidth/2)/tan(uCamFov/2)*1;

	vec3 ro = pos*1;
	ro.x +=0.0;
	ro.y +=0.;

	vec3 ta = pos+vec3(0, 0, -1);//camLookAt;

	// camera matrix
	vec3 ww = normalize(ta - ro);
	vec3 uu = normalize(cross(ww, vec3(0.0, 1, 0.0)));
	vec3 vv = normalize(cross(uu, ww));
	// create view ray
	vec3 rd = normalize(p.x*uu + p.y*vv + distanceToScreen*ww) *rotateMatrix(uCamRot);
	return Ray(pos, rd);
}

#endif

#ifndef THIS_USE_LIGHT_FUNC
Light getLight(vec3 p, LightContext lightCtx) {
	Light light;
	light.pos = uLightPos1;
	light.color = uLightColor1;
	return light;
}
#endif

void main()
{
	#ifdef OUTPUT_DEBUG
	debugOut = vec4(0);
	#endif
	//-----------------------------------------------------
	// camera
	//-----------------------------------------------------

	Ray ray = getViewRay();
	#ifdef OUTPUT_RAYDIR
	rayDirOut = vec4(ray.dir, 0);
	#endif
	#ifdef OUTPUT_RAYORIGIN
	rayOriginOut = vec4(ray.pos, 0);
	#endif
	//-----------------------------------------------------
	// render
	//-----------------------------------------------------

	float renderDepth = uUseRenderDepth > 0 ? min(texture(sTD2DInputs[0], vUV.st).r, RAYTK_MAX_DIST) : RAYTK_MAX_DIST;

	vec3 col = vec3(0);
	// raymarch
	Sdf res = castRay(ray, renderDepth);
	float outDepth = min(res.x, renderDepth);
	#ifdef OUTPUT_DEPTH
	depthOut = TDOutputSwizzle(vec4(vec3(outDepth), 1));
	#endif

	MaterialContext matCtx;
	matCtx.result = res;
	matCtx.context = createDefaultContext();
	matCtx.ray= ray;

	if (res.x > 0.0 && res.x < renderDepth) {
		vec3 p = ray.pos + ray.dir * res.x;
		#ifdef OUTPUT_WORLDPOS
		worldPosOut = vec4(p, 1);
		#endif

		#ifdef OUTPUT_SDF
		sdfOut = TDOutputSwizzle(vec4(res.x, res.x, res.x, 1));
		#endif
//		#ifdef OUTPUT_DEPTH
	//	depthOut = TDOutputSwizzle(vec4(vec3(min(res.x, renderDepth)), 1));
		//depthOut = TDOutputSwizzle(vec4(vec3(res.x)))
//		#endif

		matCtx.normal = calcNormal(p);
		LightContext lightCtx;
		lightCtx.result = res;
		lightCtx.normal = matCtx.normal;
		matCtx.light = getLight(p, lightCtx);
		col = getColor(p, matCtx);

		#ifdef OUTPUT_NORMAL
		normalOut = vec4(matCtx.normal, 0);
		#endif
		#ifdef OUTPUT_COLOR
		colorOut = TDOutputSwizzle(vec4(col, 1));
		#endif
		#ifdef OUTPUT_ORBIT
		orbitOut = res.orbit;
		#endif
	} else {
		#ifdef OUTPUT_WORLDPOS
//		worldPosOut = vec4(ray.pos + ray.dir * outDepth, 0);
		worldPosOut = vec4(0);
		#endif
		#ifdef OUTPUT_SDF
		sdfOut = vec4(0);
		#endif
		#ifdef OUTPUT_COLOR
		colorOut = vec4(0);
		#endif
		#ifdef OUTPUT_NORMAL
		normalOut = vec4(0);
		#endif
		#ifdef OUTPUT_ORBIT
		orbitOut = vec4(0);
		#endif
	}
}
