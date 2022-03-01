void THIS_merge(inout Sdf res1, in Sdf res2, CoordT p, ContextT ctx) {
MERGE_PREP();
MERGE_BODY();
}

ReturnT thismap(CoordT p, ContextT ctx) {
	ReturnT res;
	if (THIS_Enable < 0.5) {
		res = inputOp1(p, ctx);
	} else {
		CoordT q = p;
		q.THIS_AXIS += THIS_Shift;
		q.THIS_AXIS *= -1;
		q.THIS_AXIS -= THIS_Offset;
		p.THIS_AXIS += THIS_Offset;
		p.THIS_AXIS -= THIS_Shift;
		#pragma r:if THIS_Iterationtype_sign
		setIterationIndex(ctx, 1);
		const int iterB = -1;
		#pragma r:elif THIS_Iterationtype_index
		setIterationIndex(ctx, 0);
		const int iterB = 1;
		#pragma r:endif
		#pragma r:if THIS_EXPOSE_sign
		THIS_sign = 1;
		#pragma r:endif
		#pragma r:if THIS_EXPOSE_index
		THIS_index = 0;
		#pragma r:endif
		#pragma r:if THIS_Mergetype_none
		res = inputOp1(q, ctx);
		#pragma r:else
		res = inputOp1(p, ctx);
		#pragma r:if !THIS_Iterationtype_none
		setIterationIndex(ctx, iterB);
		#pragma r:endif
		#pragma r:if THIS_EXPOSE_sign
		THIS_sign = -1;
		#pragma r:endif
		#pragma r:if THIS_EXPOSE_index
		THIS_index = 1;
		#pragma r:endif
		Sdf res2 = inputOp1(q, ctx);
		THIS_merge(res, res2, p, ctx);
		#pragma r:endif
	}
	return res;
}