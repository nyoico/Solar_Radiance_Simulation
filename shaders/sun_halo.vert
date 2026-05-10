#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float uTime;

out vec3 vWorldPos;
out vec3 vNormal;

void main()
{
    vec3 normal = normalize(aPos);

    float wave1 = sin(uTime * 2.0 + aPos.y * 5.0 + aPos.z * 3.0);
    float wave2 = sin(uTime * 3.3 + aPos.x * 4.0);
    float distortion = 1.0 + 0.035 * wave1 + 0.025 * wave2;

    vec3 displaced = aPos * distortion;
    vec4 worldPos = model * vec4(displaced, 1.0);

    vWorldPos = worldPos.xyz;
    vNormal = normalize(mat3(model) * normal);

    gl_Position = projection * view * worldPos;
}