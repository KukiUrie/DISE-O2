import pygame
import cv2
import sys
import random
import time
import numpy as np
import pyaudio
from scipy.fftpack import fft
import RPi.GPIO as GPIO

# Configurar los pines GPIO
GPIO.setmode(GPIO.BCM)  # Usar la numeración BCM de los pines
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Boton 1 en pin 17
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Boton 2 en pin 27
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Boton 3 en pin 22
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Boton 4 en pin 5
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Boton 5 en pin 6
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Boton 6 en pin 13

# Inicializar Pygame
pygame.init()

# Tamaño de la pantalla
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Título de la ventana
pygame.display.set_caption("Focusboard")
icon_image = pygame.image.load("icon1.png")
pygame.display.set_icon(icon_image)

# Cargar el video usando OpenCV
video_path = "background.mp4"
cap = cv2.VideoCapture(video_path)

# Verificar si el video se cargó correctamente
if not cap.isOpened():
    print("No se pudo cargar el video.")
    sys.exit()

# Variables para controlar la reproducción del video
fps = cap.get(cv2.CAP_PROP_FPS)
frame_delay = int(1000 / fps)  # Tiempo de espera entre cuadros

# Colores
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Configuración de fuente
font = pygame.font.Font(None, 40)

# Cargar la imagen personalizada del botón "Start"
start_button_image = pygame.image.load("star2.png")  # Ruta a tu imagen
start_button_image = pygame.transform.scale(start_button_image, (120, 80))  # Escalar imagen

# Variables para animación básica (botón Start más grande al pasar el ratón)
start_button_hover = False

# Variables del juego de teclas
gpio_key_map = {
    17: "Rojo",
    27: "Verde",
    22: "Azul",
    5: "Amarillo",
    6: "Naranja",
    13: "Morado"
}

# Variables globales
score = 0
running = True

# Inicializar PyAudio para el análisis de Fourier
RATE = 44100  # Frecuencia de muestreo
CHUNK = 1024  # Tamaño de la ventana de muestreo

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Función para obtener la frecuencia dominante usando FFT
def get_dominant_frequency(data):
    fft_data = fft(np.frombuffer(data, dtype=np.int16))
    freqs = np.fft.fftfreq(len(fft_data))
    idx = np.argmax(np.abs(fft_data[:len(fft_data)//2]))
    freq = abs(freqs[idx] * RATE)
    return freq

# Función para asignar el pin basado en la frecuencia dominante
def assign_pin_to_frequency(freq):
    if 300 < freq < 500:
        return 17  # Rojo
    elif 500 < freq < 1000:
        return 27  # Verde
    elif 1000 < freq < 2000:
        return 22  # Azul
    elif 2000 < freq < 3000:
        return 5  # Amarillo
    elif 3000 < freq < 4000:
        return 6  # Naranja
    elif 4000 < freq:
        return 13  # Morado
    return None

# Función para mostrar mensaje en pantalla
def display_message(message):
    screen.fill((0, 0, 0))
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Función principal del juego de teclas
def game_loop(song):
    global score, running
    score = 0
    
    # Reproducir la canción seleccionada
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(-1)  # Repetir indefinidamente hasta que se detenga manualmente
    
    display_message("Presiona Enter para comenzar.")
    
    # Espera hasta que el jugador presione Enter
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                break
        else:
            continue
        break

    # Juego activo
    while running:
        # Capturar datos de audio y obtener la frecuencia dominante
        data = stream.read(CHUNK)
        freq = get_dominant_frequency(data)
        gpio_pin = assign_pin_to_frequency(freq)

        if gpio_pin:
            display_message(f"Presiona el botón {gpio_key_map[gpio_pin]}")
        
        # Espera la interacción del usuario
        waiting_for_input = True
        start_time = time.time()
        
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return

            # Verificar si se presionó alguno de los botones físicos
            for pin, btn_color in gpio_key_map.items():
                if GPIO.input(pin) == GPIO.LOW:  # Si el botón se presiona
                    if pin == gpio_pin:
                        score += 1
                        waiting_for_input = False
                        break
                    else:
                        display_message("Botón incorrecto. Inténtalo de nuevo.")
                        pygame.time.delay(1000)
                        waiting_for_input = False
                        break
            
            # Control del tiempo de respuesta (3 segundos por intento)
            if time.time() - start_time > 3:
                display_message("Tiempo agotado. Inténtalo de nuevo.")
                pygame.time.delay(1000)
                waiting_for_input = False
        
        # Muestra la puntuación actual
        display_message(f"Puntuación: {score}")
        pygame.time.delay(1000)

    # Detener la música cuando el juego termine
    pygame.mixer.music.stop()

# Bucle principal del juego
running = True
selected_song = "cancion1.mp3"  # Puedes cambiarla por la canción deseada

while running:
    update_background()

    # Aquí puedes implementar tu menú, pero por ahora empezará el juego directamente
    game_loop(selected_song)

cap.release()
pygame.quit()
GPIO.cleanup()  # Limpiar los pines GPIO al salir
sys.exit()
