import numpy as np

def create_uv_sphere(radius=1.0, sectors=36, stacks=18):
    vertices = []
    indices = []

    for i in range(stacks + 1):
        stack_angle = np.pi / 2 - i * np.pi / stacks
        xy = radius * np.cos(stack_angle)
        z = radius * np.sin(stack_angle)

        for j in range(sectors + 1):
            sector_angle = j * 2  * np.pi / sectors
            x = xy * np.cos(sector_angle)
            y = xy * np.sin(sector_angle)

            u = j / sectors
            v = i / stacks

            vertices.extend([x, y, z, u, v])

    for i in range(stacks):
        k1 = i * (sectors + 1) 
        k2 = k1 + sectors + 1

        for j in range(sectors): 
            if i != 0:
                indices.extend([k1 + j, k2 + j, k1 + j + 1])
            if i != stacks - 1:
                indices.extend([k1 + j + 1, k2 + j, k2 + j + 1])
    
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)