import pygame
import cv2
import sys
import random
import time
import RPi.GPIO as GPIO

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
button_pin_1 = 17
button_pin_2 = 27
button_pin_3 = 22
GPIO.setup(button_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

# Variables del juego de teclas
key_color_map = {
    pygame.K_z: "Rojo",
    pygame.K_x: "Verde",
    pygame.K_c: "Azul",
    pygame.K_v: "Amarillo"
}

# Variables globales
score = 0
running = True
selected_song = None

# Diccionario para almacenar el estado del menú
menu_state = {
    'main': True,
    'level': False,
    'difficulty': False,
    'Cancion': False
}

# Lista de canciones
songs = ["cancion1.mp3", "cancion2.mp3", "cancion3.mp3"]

# Función para mostrar mensaje en pantalla
def display_message(message):
    screen.fill((0, 0, 0))
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Función para dibujar el menú principal
def draw_main_menu():
    screen.fill((0, 0, 0))
    display_message("Bienvenido al juego! Presiona Start para comenzar.")
    start_button = create_start_button()
    pygame.display.flip()
    return start_button

# Función principal del juego de teclas
def game_loop(song):
    global score, running
    score = 0
    
    # Reproducir la canción seleccionada
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(-1)
    
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
        # Selección aleatoria de tecla
        key, color = random.choice(list(key_color_map.items()))
        display_message(f"Presiona {pygame.key.name(key).upper()} ({color})")
        
        # Espera la interacción del usuario
        waiting_for_input = True
        start_time = time.time()
        
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == key:
                        score += 1
                        waiting_for_input = False
                    else:
                        display_message("Tecla incorrecta. Inténtalo de nuevo.")
                        time.sleep(1)
                        waiting_for_input = False
                        
            # Detecta si se presionó algún botón físico
            if GPIO.input(button_pin_1) == GPIO.LOW:
                score += 1
                waiting_for_input = False
            elif GPIO.input(button_pin_2) == GPIO.LOW:
                score += 1
                waiting_for_input = False
            elif GPIO.input(button_pin_3) == GPIO.LOW:
                score += 1
                waiting_for_input = False
                        
            # Control del tiempo de respuesta (3 segundos por intento)
            if time.time() - start_time > 3:
                display_message("Tiempo agotado. Inténtalo de nuevo.")
                time.sleep(1)
                waiting_for_input = False
        
        # Muestra la puntuación actual
        display_message(f"Puntuación: {score}")
        time.sleep(1)

    # Detener la música cuando el juego termine
    pygame.mixer.music.stop()

# Función para crear el botón "Start"
def create_start_button():
    button_rect = start_button_image.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(start_button_image, button_rect)
    return button_rect

# Bucle principal del menú
while running:
    if menu_state['main']:
        start_button = draw_main_menu()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button and start_button.collidepoint(event.pos):
                menu_state['main'] = False
                selected_song = songs[0]  # Selecciona una canción por defecto para este ejemplo
                game_loop(selected_song)
    
    pygame.display.flip()
    pygame.time.delay(frame_delay)

cap.release()
pygame.quit()
sys.exit()

GPIO.cleanup()

