import glfw
import numpy as np
import pandas as pd
from OpenGL.GL import *
from mesh import create_uv_sphere
from particle import ParticleSystem
from text_renderer import TextRenderer

import sys
import os
import ctypes
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

WIDTH, HEIGHT = 1000, 700
yaw = -90.0
pitch = 20.0
distance = 80.0

last_x = WIDTH / 2
last_y = HEIGHT / 2
mouse_pressed = False

def load_shader(path):
    with open(resource_path(path), "r", encoding="utf-8") as file:
        return file.read()


def compile_shader(source, shader_type): 
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(error)

    return shader


def create_shader_program(vertex_path, fragment_path):
    vertex_shader = compile_shader(load_shader(vertex_path), GL_VERTEX_SHADER)
    fragment_shader = compile_shader(load_shader(fragment_path), GL_FRAGMENT_SHADER)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    if not glGetProgramiv(shader_program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(shader_program).decode()
        raise RuntimeError(error)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program


def perspective(fov, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2.0)

    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[0, 0] = f / aspect
    matrix[1, 1] = f
    matrix[2, 2] = (far + near) / (near - far)
    matrix[2, 3] = (2 * far * near) / (near - far)
    matrix[3, 2] = -1.0

    return matrix

def look_at(eye, target, up):
    f = target - eye
    f = f / np.linalg.norm(f)

    s = np.cross(f, up)
    s = s / np.linalg.norm(s)

    u = np.cross(s, f)

    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0] = s[0]
    matrix[0, 1] = s[1]
    matrix[0, 2] = s[2]

    matrix[1, 0] = u[0]
    matrix[1, 1] = u[1]
    matrix[1, 2] = u[2]

    matrix[2, 0] = -f[0]
    matrix[2, 1] = -f[1]
    matrix[2, 2] = -f[2]

    matrix[0, 3] = -np.dot(s, eye)
    matrix[1, 3] = -np.dot(u, eye)
    matrix[2, 3] = np.dot(f, eye)

    return matrix


def translate(x, y, z):
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 3] = x
    matrix[1, 3] = y
    matrix[2, 3] = z
    return matrix


def scale(s):
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0] = s
    matrix[1, 1] = s
    matrix[2, 2] = s
    return matrix


def create_sphere_vao(radius):
    vertices, indices = create_uv_sphere(radius=radius)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    stride = 5 * vertices.itemsize

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindVertexArray(0)

    return vao, len(indices)

def create_particle_vao(particle_count):
    positions = np.zeros((particle_count, 3), dtype=np.float32)
    intensities = np.ones(particle_count, dtype=np.float32)
    colors = np.ones((particle_count, 3), dtype=np.float32)

    vao = glGenVertexArrays(1)
    pos_vbo = glGenBuffers(1)
    intensity_vbo = glGenBuffers(1)
    color_vbo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
    glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_DYNAMIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * positions.itemsize, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, intensity_vbo)
    glBufferData(GL_ARRAY_BUFFER, intensities.nbytes, intensities, GL_DYNAMIC_DRAW)
    glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, intensities.itemsize, None)
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, color_vbo)
    glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_DYNAMIC_DRAW)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 3 * colors.itemsize, None)
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)

    return vao, pos_vbo, intensity_vbo, color_vbo


def create_line_vao(vertices):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)

    glBindVertexArray(0)

    return vao, vbo


def set_mat4(shader, name, matrix):
    location = glGetUniformLocation(shader, name)
    glUniformMatrix4fv(location, 1, GL_TRUE, matrix)


def set_vec3(shader, name, value):
    location = glGetUniformLocation(shader, name)
    glUniform3f(location, value[0], value[1], value[2])

def set_int(shader, name, value):
    location = glGetUniformLocation(shader, name)
    glUniform1i(location, value)

def set_float(shader, name, value):
    location = glGetUniformLocation(shader, name)
    glUniform1f(location, value)

def load_texture(path):
    image = Image.open(resource_path(path))
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image = image.convert("RGB")

    max_texture_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
    width, height = image.size

    if width > max_texture_size or height > max_texture_size:
        scale = min(max_texture_size / width, max_texture_size / height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        image = image.resize((new_width, new_height), Image.LANCZOS)
        width, height = image.size

        print(f"Texture resized: {path} -> {width}x{height}")

    img_data = image.tobytes()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGB,
        width,
        height,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        img_data
    )

    glGenerateMipmap(GL_TEXTURE_2D)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture

def mouse_button_callback(window, button, action, mods):
    global mouse_pressed

    if button == glfw.MOUSE_BUTTON_LEFT:
        mouse_pressed = action == glfw.PRESS


def cursor_position_callback(window, xpos, ypos):
    global yaw, pitch, last_x, last_y, mouse_pressed

    if not mouse_pressed:
        last_x = xpos
        last_y = ypos
        return

    xoffset = xpos - last_x
    yoffset = last_y - ypos

    last_x = xpos
    last_y = ypos

    sensitivity = 0.2
    yaw += xoffset * sensitivity
    pitch += yoffset * sensitivity

    pitch = max(-89.0, min(89.0, pitch))


def scroll_callback(window, xoffset, yoffset):
    global distance

    distance -= yoffset * 3.0
    distance = max(20.0, min(200.0, distance))

def main():
    if not glfw.init():
        raise Exception("GLFW init failed")
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(WIDTH, HEIGHT, "Solar Radiation Simulation", None, None)

    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")

    glfw.make_context_current(window) 

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_PROGRAM_POINT_SIZE)

    shader = create_shader_program(
        "shaders/basic.vert",
        "shaders/basic.frag"
    )

    text_shader = create_shader_program(
        "shaders/text.vert",
        "shaders/text.frag"
    )

    particle_shader = create_shader_program(
        "shaders/particle.vert",
        "shaders/particle.frag"
    )

    sun_halo_shader = create_shader_program(
        "shaders/sun_halo.vert",
        "shaders/sun_halo.frag"
    )

    text_renderer = TextRenderer(text_shader)

    sphere_vao, sphere_index_count = create_sphere_vao(radius=1.0)

    earth_texture = load_texture("textures/earth.jpg")
    sun_texture = load_texture("textures/sun_nasa.jpg")
    space_texture = load_texture("textures/8k_space.jpg")

    particles = ParticleSystem(count=1200)
    particle_vao, particle_vbo, particle_intensity_vbo, particle_color_vbo = create_particle_vao(particles.count)

    solar_df = pd.read_csv(resource_path("data/nasa_solar.csv"))
    solar_values = solar_df["irradiance"].values.astype(np.float32)

    solar_min = np.min(solar_values)
    solar_max = np.max(solar_values)

    solar_index = 0
    solar_timer = 0.0

    last_time = glfw.get_time()

    #projection = perspective(45.0, WIDTH / HEIGHT, 0.1, 500.0)
    fb_width, fb_height = glfw.get_framebuffer_size(window)

    glViewport(0, 0, fb_width, fb_height)

    projection = perspective(
        45.0,
        fb_width / fb_height,
        0.1,
        500.0
    )

    date = "----"
    raw_value = 0.0
    emission_scale = 1.0
    
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        solar_timer += dt

        if solar_timer > 1.0:
            solar_timer = 0.0
            solar_index = (solar_index + 1) % len(solar_values)

            raw_value = solar_values[solar_index]
            date = str(solar_df.iloc[solar_index]["date"])

            normalized = (raw_value - solar_min) / (solar_max - solar_min + 1e-6)
            emission_scale = 0.5 + normalized * 2.0

            particles.set_emission_scale(emission_scale)

            print("NASA date:", solar_df.iloc[solar_index]["date"],
                "irradiance:", raw_value,
                "scale:", emission_scale)
            
            text = (
                "NASA POWER DATA\n"
                f"Date: {date}\n"
                f"Irradiance: {raw_value: }\n"
                f"Scale: {emission_scale: }"
            )

            text_renderer.create_text_texture(text)

        particles.update(dt)

        glClearColor(0.02, 0.02, 0.05, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(shader)

        target = np.array([20.0, 0.0, 0.0], dtype=np.float32)

        yaw_rad = np.radians(yaw)
        pitch_rad = np.radians(pitch)

        eye = np.array([
            target[0] + distance * np.cos(pitch_rad) * np.cos(yaw_rad),
            target[1] + distance * np.cos(pitch_rad) * np.sin(yaw_rad),
            target[2] + distance * np.sin(pitch_rad)
        ], dtype=np.float32)

        up = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        view = look_at(eye, target, up)

        set_mat4(shader, "view", view)
        set_mat4(shader, "projection", projection)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glBindVertexArray(sphere_vao)

        set_int(shader, "useVertexColor", 0)

        # Space Background
        glDepthMask(GL_FALSE)

        set_int(shader, "useTexture", 1)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, space_texture)
        set_int(shader, "texture1", 0)

        space_model = translate(
            eye[0],
            eye[1],
            eye[2]
        ) @ scale(250.0)

        set_mat4(shader, "model", space_model)

        glDisable(GL_CULL_FACE)

        glDrawElements(
            GL_TRIANGLES,
            sphere_index_count,
            GL_UNSIGNED_INT,
            None
        )

        glDepthMask(GL_TRUE)


        # Sun
        set_int(shader, "useTexture", 1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, sun_texture)
        set_int(shader, "texture1", 0)

        sun_model = translate(0.0, 0.0, 0.0) @ scale(10.9)
        set_mat4(shader, "model", sun_model)
        glDrawElements(GL_TRIANGLES, sphere_index_count, GL_UNSIGNED_INT, None)

        # Sun halo
        glUseProgram(sun_halo_shader)

        halo_pulse = 15.2 + 0.28 * np.sin(current_time * 1.6)

        set_mat4(sun_halo_shader, "view", view)
        set_mat4(sun_halo_shader, "projection", projection)
        set_float(sun_halo_shader, "uTime", current_time)
        set_vec3(sun_halo_shader, "uCameraPos", eye)

        halo_model = translate(0.0, 0.0, 0.0) @ scale(halo_pulse)
        set_mat4(sun_halo_shader, "model", halo_model)

        glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glBlendFunc(GL_ONE, GL_ONE)
        glDepthMask(GL_FALSE)

        glBindVertexArray(sphere_vao)
        glDrawElements(GL_TRIANGLES, sphere_index_count, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glBindVertexArray(sphere_vao)
        glUseProgram(shader)
        # Earth
        set_int(shader, "useTexture", 1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, earth_texture)
        set_int(shader, "texture1", 0)

        earth_model = translate(40.0, 0.0, 0.0) @ scale(1.0)
        set_mat4(shader, "model", earth_model)
        glDrawElements(GL_TRIANGLES, sphere_index_count, GL_UNSIGNED_INT, None)

        set_int(shader, "useTexture", 0)
        set_int(shader, "useVertexColor", 1)

        # Particles
        particle_positions = particles.get_positions()
        particle_intensities = particles.get_intensities()
        particle_colors = particles.get_colors()

        glBindBuffer(GL_ARRAY_BUFFER, particle_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, particle_positions.nbytes, particle_positions)

        glBindBuffer(GL_ARRAY_BUFFER, particle_intensity_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, particle_intensities.nbytes, particle_intensities)

        glBindBuffer(GL_ARRAY_BUFFER, particle_color_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, particle_colors.nbytes, particle_colors)

        particle_model = np.identity(4, dtype=np.float32)

        glUseProgram(particle_shader)
        set_mat4(particle_shader, "model", particle_model)
        set_mat4(particle_shader, "view", view)
        set_mat4(particle_shader, "projection", projection)

        glDisable(GL_DEPTH_TEST)

        glEnable(GL_PROGRAM_POINT_SIZE)

        try:
            glEnable(GL_POINT_SPRITE)
        except:
            pass

        glDepthMask(GL_FALSE)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)

        glBindVertexArray(particle_vao)
        glDrawArrays(GL_POINTS, 0, particles.count)
        glBindVertexArray(0)

        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        glDepthMask(GL_FALSE)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glBindVertexArray(particle_vao)
        glDrawArrays(GL_POINTS, 0, particles.count)

        glBindVertexArray(0)

        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glLineWidth(1.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        text_renderer.render()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
