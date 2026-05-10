#version 330 core

out vec4 FragColor;

in vec2 TexCoord;

uniform vec3 objectColor;
uniform sampler2D texture1;
uniform int useTexture;
uniform int useVertexColor;

void main()
{
    if (useTexture == 1)
        FragColor = texture(texture1, TexCoord);
    else
        FragColor = vec4(objectColor, 1.0);
}