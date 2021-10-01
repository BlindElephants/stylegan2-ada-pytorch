import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import pickle
import torch

from pythonosc import dispatcher, osc_server
from threading import Thread, Lock

outSize = (1024, 1024)


mutex = Lock()

receiveLatentDirty = False
receiveLatent = []


def receiveLatentVector(addr, *args):
    global receiveLatentDirty, receiveLatent
    if len(args) != 512:
        print('Invalid latent vector size received: {}'.format(len(args)))
        return

    with mutex:
        receiveLatent = np.array(args).reshape(1, 512)
        receiveLatentDirty = True


dispatcher = dispatcher.Dispatcher()
dispatcher.map('/latent', receiveLatentVector)
oscListener = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 8889), dispatcher)
oscListenerThread = Thread(target=oscListener.serve_forever, args=())
print("Starting OSC listener thread.")
oscListenerThread.start()

INPUT_MODEL = os.path.join('data', 'network-snapshot-000000.pkl')
with open(INPUT_MODEL, 'rb') as f:
    model = pickle.load(f)['G_ema'].cuda()

model.eval()

r = np.random.rand(1, 512)


def get_image_from_numpy_array(latent_vector: np.array):
    out_img = torch.as_tensor(latent_vector, device='cuda')
    out_img = model(out_img, None, noise_mode='const')
    out_img = (out_img.permute(0, 2, 3, 1) * 0.5 + 0.5019607843137255).clamp(0.0, 1.0)
    out_img = out_img.reshape(1024, 1024, 3).detach().cpu().numpy()
    return out_img


img = get_image_from_numpy_array(np.random.rand(1, 512))


pygame.init()
pygame.display.set_caption('AI Video Project')
pygame.display.set_mode(outSize, DOUBLEBUF | OPENGL | pygame.NOFRAME)
pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)

glMatrixMode(GL_PROJECTION)
glOrtho(0, outSize[0], outSize[1], 0, 1, -1)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glDisable(GL_DEPTH_TEST)
glClearColor(1.0, 1.0, 1.0, 1.0)
glEnable(GL_TEXTURE_2D)

senderTexture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, senderTexture)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glBindTexture(GL_TEXTURE_2D, 0)


def update():
    global receiveLatentDirty, receiveLatent, img

    if receiveLatentDirty:
        img = get_image_from_numpy_array(receiveLatent)
        receiveLatentDirty = False

    glBindTexture(GL_TEXTURE_2D, senderTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, outSize[0], outSize[1], 0, GL_RGB, GL_FLOAT, img)

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
    glBindTexture(GL_TEXTURE_2D, 0)


while True:
    update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                oscListener.server_close()
                oscListener.shutdown()
                oscListenerThread.join(timeout=2.0)
                quit()