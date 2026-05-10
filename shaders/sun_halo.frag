#version 330 core

in vec3 vWorldPos;
in vec3 vNormal;

uniform float uTime;
uniform vec3 uCameraPos;

out vec4 FragColor;

void main()
{
    vec3 normal = normalize(vNormal);
    vec3 viewDir = normalize(uCameraPos - vWorldPos);

    float rim = 1.0 - clamp(dot(normal, viewDir), 0.0, 1.0);

    float surfaceGlow = 1.0 - smoothstep(0.08, 0.95, rim);
    float edgeFade = 1.0 - smoothstep(0.78, 1.0, rim);
    float softGlow = pow(surfaceGlow, 1.6) * edgeFade;

    float broadAura = pow(surfaceGlow, 2.8) * 0.08;

    float pulse = 0.65 + 0.35 * sin(uTime * 2.4);
    float wave = 0.5 + 0.5 * sin(
        uTime * 4.0 +
        vWorldPos.y * 0.35 +
        vWorldPos.z * 0.25
    );

    float alpha =
        softGlow *
        (0.30 + 0.08 * pulse + 0.035 * wave) +
        broadAura;

    vec3 innerGlow = vec3(1.0, 0.62, 0.12);
    vec3 outerGlow = vec3(1.0, 0.12, 0.02);

    vec3 color = mix(innerGlow, outerGlow, smoothstep(0.18, 0.98, rim));

    FragColor = vec4(color * alpha * 2.0, alpha);
}
