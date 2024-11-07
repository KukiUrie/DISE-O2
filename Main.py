import pygame
import cv2
import sys
import random
import time
import serial
import RPi.GPIO as GPIO

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)  # Asegúrate de que el puerto sea el correcto

# Configuración de los pines GPIO de los botones
GPIO.setmode(GPIO.BCM)
button_pins = [17, 27, 22, 5, 6, 13]
for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configura los botones con resistencia pull-up

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
frame_delay = int(1000 / fps)

# Mapeo de colores y botones
gpio_key_map = {
    17: "Rojo",
    27: "Verde",
    22: "Azul",
    5: "Amarillo",
    6: "Naranja",
    13: "Morado"
}

# Variables de juego
score = 0
running = True
difficulty = "Medio"  # Dificultad por defecto
difficulty_speed_map = {
    "Facil": 2,
    "Medio": 1.5,
    "Dificil": 1
}

# Función para enviar comando al Arduino
def send_command_to_arduino(command):
    ser.write((command + '\n').encode())

# Función para mostrar mensaje en pantalla
def display_message(message):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 40)
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Función principal del juego
def game_loop(song):
    global score, running, difficulty
    score = 0
    
    # Reproducir la canción seleccionada
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(-1)
    
    display_message("Presiona ENTER para comenzar.")

    # Espera hasta que el jugador presione ENTER para empezar
    waiting_for_enter = True
    while waiting_for_enter:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting_for_enter = False
                break

    # Juego activo
    while running:
        gpio_pin, color = random.choice(list(gpio_key_map.items()))
        display_message(f"Presiona el botón {color}")
        
        # Enviar comando para encender el LED del color correspondiente
        send_command_to_arduino("ENCENDER " + color)
        
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

            # Control del tiempo de respuesta según dificultad
            if time.time() - start_time > difficulty_speed_map[difficulty]:
                display_message("Tiempo agotado. Inténtalo de nuevo.")
                pygame.time.delay(1000)
                waiting_for_input = False

        # Enviar comando para apagar todos los LEDs
        send_command_to_arduino("APAGAR")
        
        # Muestra la puntuación actual
        display_message(f"Puntuación: {score}")
        pygame.time.delay(1000)

    # Detener la música cuando el juego termine
    pygame.mixer.music.stop()

# Función para actualizar el fondo animado
def update_background():
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (screen_width, screen_height))
    frame_surface = pygame.surfarray.make_surface(frame)
    screen.blit(pygame.transform.rotate(frame_surface, -90), (0, 0))

# Menú principal
def main_menu():
    global running

    # Estado previo para evitar redibujado innecesario
    previous_state = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button and start_button.collidepoint(event.pos):
                    create_buttons()
                    game_loop("song.mp3")  # Inicia el juego con una canción

        # Actualizar el fondo con el video
        update_background()

        pygame.display.flip()

# Limpiar los pines GPIO al salir
GPIO.cleanup()
pygame.quit()
sys.exit()
