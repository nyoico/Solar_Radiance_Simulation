from PIL import Image, ImageDraw, ImageFont
import numpy as np
from OpenGL.GL import *


class TextRenderer:
    def __init__(self, shader_program):
        self.shader = shader_program
        self.texture = glGenTextures(1)

        vertices = np.array([
            # x, y,    u, v
            -0.98,  0.95,  0.0, 0.0,
            -0.38,  0.95,  1.0, 0.0,
            -0.38,  0.65,  1.0, 1.0,

            -0.98,  0.95,  0.0, 0.0,
            -0.38,  0.65,  1.0, 1.0,
            -0.98,  0.65,  0.0, 1.0,
        ], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, None)
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            1, 2, GL_FLOAT, GL_FALSE,
            4 * vertices.itemsize,
            ctypes.c_void_p(2 * vertices.itemsize)
        )
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def create_text_texture(self, text):
        img = Image.new("RGBA", (512, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Helvetica.ttc", 32)
            #font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()

        draw.text((30, 30), text, font=font, fill=(255, 255, 255, 255))

        #img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(img, dtype=np.uint8)

        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def render(self):
        glUseProgram(self.shader)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        location = glGetUniformLocation(self.shader, "textTexture")
        glUniform1i(location, 0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)