---
layout: operator
title: specularContrib
parent: Material Operators
grand_parent: Operators
permalink: /reference/operators/material/specularContrib
redirect_from:
  - /reference/opType/raytk.operators.material.specularContrib/
op:
  category: material
  images:
  - assets/images/reference/operators/material/specularContrib_beckmann.png
  - assets/images/reference/operators/material/specularContrib_blinnphong.png
  - assets/images/reference/operators/material/specularContrib_cooktorrance.png
  - assets/images/reference/operators/material/specularContrib_gaussian.png
  - assets/images/reference/operators/material/specularContrib_ggx.png
  - assets/images/reference/operators/material/specularContrib_phong.png
  inputs:
  - contextTypes:
    - MaterialContext
    coordTypes:
    - float
    - vec2
    - vec3
    - vec4
    label: Shininess
    name: shininessField
    returnTypes:
    - float
  - contextTypes:
    - MaterialContext
    coordTypes:
    - float
    - vec2
    - vec3
    - vec4
    label: Roughness
    name: roughnessField
    returnTypes:
    - float
    supportedVariableInputs:
    - shininessField
  - contextTypes:
    - MaterialContext
    coordTypes:
    - float
    - vec2
    - vec3
    - vec4
    label: Fresnel
    name: fresnelField
    returnTypes:
    - float
    supportedVariableInputs:
    - shininessField
    - roughnessField
  - contextTypes:
    - MaterialContext
    coordTypes:
    - float
    - vec2
    - vec3
    - vec4
    label: Color
    name: colorField
    returnTypes:
    - vec4
    supportedVariableInputs:
    - shininessField
    - roughnessField
    - fresnelField
  keywords:
  - ggx
  - lighting
  - material
  - modularmat
  - phong
  - shading
  - specular
  name: specularContrib
  opType: raytk.operators.material.specularContrib
  parameters:
  - label: Color
    name: Color
    readOnlyHandling: baked
    regularHandling: runtime
  - label: Level
    name: Level
    readOnlyHandling: baked
    regularHandling: runtime
  - label: Method
    menuOptions:
    - label: Phong
      name: phong
    - label: Blinn-Phong
      name: blinnphong
    - label: Beckmann
      name: beckmann
    - label: Cook-Torrance
      name: cooktorrance
    - label: Gaussian
      name: gaussian
    - label: GGX
      name: ggx
    name: Method
    readOnlyHandling: baked
    regularHandling: runtime
    summary: The type of specular shading to use. Different methods support different
      combinations of the other parameters.
  - label: Shininess
    name: Shininess
  - label: Roughness
    name: Roughness
  - label: Fresnel
    name: Fresnel
  - label: Use Color
    name: Usecolor
    summary: Whether to produce color or just a brightness value.
  - label: Use Light Color
    name: Uselightcolor
    readOnlyHandling: semibaked
    regularHandling: semibaked
    summary: Whether to apply the light color to the color produced by this element.
  - label: Enable Shadow
    name: Enableshadow
    readOnlyHandling: baked
    regularHandling: baked
    summary: Whether to apply the shadow to the color/level produced by this element.
  - label: Enable
    name: Enable
  - label: Use Surface Color
    name: Usesurfacecolor
    readOnlyHandling: semibaked
    regularHandling: semibaked
  shortcuts:
  - sc
  summary: A material element that provides specular light contribution.
  thumb: assets/images/reference/operators/material/specularContrib_thumb.png

---


A material element that provides specular light contribution.