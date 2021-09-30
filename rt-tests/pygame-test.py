if __name__ == "__main__":

    import pygame
    from pygame.locals import *
    from OpenGL.GL import *
    from OpenGL.GLU import *

    outSize = (1024, 1024)

    pygame.init()
    pygame.display.set_caption('AI Video Project')
    pygame.display.set_mode(outSize, DOUBLEBUF|OPENGL)
    pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)

    glMatrixMode(GL_PROJECTION)
    glOrtho(0, outSize[0], outSize[1], 0, 1, -1)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_TEXTURE_2D)


    while True:
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, outSize[0], outSize[1], 0, GL_RGB, GL_FLOAT, img ) # this is the generated image
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_QUADS)

        glTexCoord(0, 0)
        glVertex2f(0, 0)

        glTexCoord(1, 0)
        glVertex2f(outSize[0], 0)

        glTexCoord(1, 1)
        glVertex2f(outSize[0], outSize[1])

        glTexCoord(0, 1)
        glVertex2f(0, outSize[1])

        glEnd()
        pygame.display.flip()

