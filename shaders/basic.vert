#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in float aIntensity;
layout (location = 2) in vec3 aColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 objectColor;
uniform int useVertexColor;

out float vIntensity;
out vec3 vColor;

void main()
{
    vIntensity = aIntensity;

    if (useVertexColor == 1)
        vColor = aColor;
    else
        vColor = objectColor;

    gl_Position = projection * view * model * vec4(aPos, 1.0);
}