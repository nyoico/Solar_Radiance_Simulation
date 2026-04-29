#version 330 core

out vec4 FragColor;

in float vIntensity;
in vec3 vColor;

void main()
{
    float brightness = clamp(vIntensity * 120.0, 0.2, 1.0);
    FragColor = vec4(vColor * brightness, 1.0);
}