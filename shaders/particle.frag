#version 330 core

out vec4 FragColor;

void main()
{
    vec2 uv = gl_PointCoord - vec2(0.5);
    float d = length(uv);

    float core = smoothstep(0.14, 0.0, d);

    float glow = smoothstep(0.5, 0.05, d);

    float halo = smoothstep(0.5, 0.0, d);
    halo = pow(halo, 2.8);

    float rayX = 1.0 - smoothstep(0.0, 0.025, abs(uv.y));
    float rayY = 1.0 - smoothstep(0.0, 0.025, abs(uv.x));

    rayX *= smoothstep(0.5, 0.05, abs(uv.x));
    rayY *= smoothstep(0.5, 0.05, abs(uv.y));

    float sparkle = (rayX + rayY) * 0.45;

    vec3 haloColor = vec3(1.0, 0.28, 0.03);
    vec3 glowColor = vec3(1.0, 0.55, 0.08);
    vec3 coreColor = vec3(1.0, 0.95, 0.55);

    vec3 color = vec3(0.0);
    color += haloColor * halo * 1.0;
    color += glowColor * glow * 2.0;
    color += coreColor * core * 3.0;
    color += coreColor * sparkle * 1.8;

    float alpha = 0.0;
    alpha += halo * 0.25;
    alpha += glow * 0.55;
    alpha += core * 0.9;
    alpha += sparkle * 0.7;

    if (alpha < 0.015)
        discard;

    FragColor = vec4(color, alpha);
}