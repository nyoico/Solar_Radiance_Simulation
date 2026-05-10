#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in float aIntensity;
layout (location = 2) in vec3 aColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 particleColor;
out float particleIntensity;

void main()
{
    particleColor = aColor;
    particleIntensity = max(aIntensity, 0.3);

    gl_Position = projection * view * model * vec4(aPos, 1.0);

    gl_PointSize = 2.0;
}