import cv2
import time
import numpy as np
import ctypes
import win32api
import threading
from ctypes import windll
import mss

class Triggerbot:
    def __init__(self):
        user32 = windll.user32
        self.WIDTH, self.HEIGHT = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.size = 40  # Aumentar a área de captura
        self.Fov = {
            "top": int(self.HEIGHT / 2 - self.size),
            "left": int(self.WIDTH / 2 - self.size),
            "width": int(2 * self.size),
            "height": int(2 * self.size)
        }

        # Definindo os limites de cor para roxo em HSV
        self.cmin = np.array([125, 100, 100], dtype=np.uint8)  # Limite inferior para roxo
        self.cmax = np.array([160, 255, 255], dtype=np.uint8)  # Limite superior para roxo

        self.frame = None  # Inicializa o frame como None

    def rgb_to_hsv(self, rgb):
        return cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]

    def Capture(self):
        print("Capturando tela...")
        with mss.mss() as sct:
            while True:
                sct_img = sct.grab(self.Fov)
                self.frame = np.array(sct_img)[:, :, :3]  # Captura a área da tela em RGB

                # Mostrar a imagem capturada para depuração
                cv2.imshow('Frame', self.frame)

                time.sleep(0.016)  # Aproximadamente 60 FPS

    def Color(self):
        if self.frame is not None:
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_RGB2HSV)
            mask1 = cv2.inRange(hsv, self.cmin, self.cmax)  # Faixa 1

            # Encontrar contornos na máscara
            contours, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Encontrar o maior contorno
                largest_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest_contour)
                if M["m00"] > 0:  # Para evitar divisão por zero
                    # Calcular as coordenadas do centro do contorno
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    # Retornar as coordenadas do centro
                    return cX, cY, True

            return None, None, False  # Se não houver contornos
        
    def MoveMouse(self, x, y):
        # Calcular a posição global do mouse
        global_x = x + self.Fov["left"]
        global_y = y + self.Fov["top"]

        # Mover o mouse para a posição calculada
        ctypes.windll.user32.SetCursorPos(global_x, global_y)

    def Send(self):
       
        if win32api.GetAsyncKeyState(0x05) < 0:  # Botão lateral do mouse
            cX, cY, detected = self.Color()
            if detected:
                self.MoveMouse(cX, cY)  # Mover o mouse para a posição detectada
                windll.user32.keybd_event(0x01, 0, 0, 0)  # Pressiona o botão esquerdo do mouse
                windll.user32.keybd_event(0x01, 0, 2, 0)  # Solta o botão esquerdo do mouse

    def Main(self):
        while True:
            self.Send()
            time.sleep(0.01)

if __name__ == "__main__":
    print("Iniciando Triggerbot...")
    triggerbot = Triggerbot()
    threading.Thread(target=triggerbot.Capture).start()
    threading.Thread(target=triggerbot.Main).start()
