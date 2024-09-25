import pygame
import numpy as np
import time
import RPi.GPIO as GPIO
import pyaudio
from scipy.fftpack import fft

# Configurar los pines GPIO
GPIO.setmode(GPIO.BCM)
pins = [17, 27, 22, 5, 6, 13]
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Inicializar Pygame
pygame.init()

# Tamaño de la pantalla
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Juego de Ritmo con Fourier")

# Variables globales
rate = 44100  # Frecuencia de muestreo
chunk = 1024  # Tamaño del buffer
window = np.hanning(chunk)  # Ventana de Hanning para suavizar los datos de FFT

# Inicializar PyAudio
p = pyaudio.PyAudio()

# Abrir el stream de PyAudio para la captura de audio
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                frames_per_buffer=chunk)

# Función para obtener la frecuencia dominante
def get_dominant_frequency(audio_chunk):
    # Aplicar ventana de Hanning y realizar FFT
    fft_data = fft(audio_chunk * window)
    freqs = np.fft.fftfreq(len(fft_data))
    
    # Obtener la magnitud de las frecuencias
    magnitude = np.abs(fft_data)
    
    # Buscar la frecuencia con mayor magnitud (frecuencia dominante)
    idx = np.argmax(magnitude)
    freq = abs(freqs[idx] * rate)
    
    return freq

# Función para asignar pines GPIO a diferentes rangos de frecuencia
def assign_pin_to_frequency(freq):
    if freq < 300:
        return 17  # Frecuencias bajas
    elif 300 <= freq < 600:
        return 27  # Frecuencias medias-bajas
    elif 600 <= freq < 1000:
        return 22  # Frecuencias medias
    elif 1000 <= freq < 2000:
        return 5  # Frecuencias medias-altas
    elif 2000 <= freq < 4000:
        return 6  # Frecuencias altas
    else:
        return 13  # Frecuencias muy altas

# Función principal del juego
def game_loop(song):
    # Cargar y reproducir la canción
    pygame.mixer.init()
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()
    
    start_time = time.time()

    while pygame.mixer.music.get_busy():
        # Leer audio desde el stream en tiempo real
        audio_data = np.frombuffer(stream.read(chunk), dtype=np.int16)
        
        # Obtener la frecuencia dominante
        freq = get_dominant_frequency(audio_data)
        print(f"Frecuencia dominante: {freq} Hz")
        
        # Asignar un botón GPIO según la frecuencia
        assigned_pin = assign_pin_to_frequency(freq)
        display_message(f"Presiona el botón {gpio_key_map[assigned_pin]}")
        
        # Esperar la interacción del usuario
        waiting_for_input = True
        user_input = False
        input_start_time = time.time()
        
        while waiting_for_input:
            for pin in gpio_key_map.keys():
                if GPIO.input(pin) == GPIO.LOW:
                    user_input = True
                    if pin == assigned_pin:
                        waiting_for_input = False
                    else:
                        display_message("Botón incorrecto. Inténtalo de nuevo.")
                        pygame.time.delay(1000)
                        waiting_for_input = False
            
            if time.time() - input_start_time > 2:
                display_message("Tiempo agotado. Inténtalo de nuevo.")
                pygame.time.delay(1000)
                waiting_for_input = False

    pygame.mixer.music.stop()

# Mostrar mensaje en pantalla
def display_message(message):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 40)
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Mapa de colores para los botones
gpio_key_map = {
    17: "Rojo",
    27: "Verde",
    22: "Azul",
    5: "Amarillo",
    6: "Naranja",
    13: "Morado"
}

# Ejecutar el juego
try:
    song = "cancion1.mp3"  # Cambia a la canción que desees cargar
    game_loop(song)
finally:
    GPIO.cleanup()  # Limpiar configuración de pines al final
    stream.stop_stream()
    stream.close()
    p.terminate()
