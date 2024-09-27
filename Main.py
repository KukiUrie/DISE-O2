import pygame
import cv2
import sys
import random
import time
import RPi.GPIO as GPIO  # Importa la biblioteca de GPIO

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
difficulty = "Medio"  # Dificultad por defecto
difficulty_speed_map = {
    "Facil": 2,    # Más tiempo entre desafíos
    "Medio": 1.5,  # Tiempo moderado
    "Dificil": 1   # Menos tiempo entre desafíos
}

# Función para mostrar mensaje en pantalla
def display_message(message):
    screen.fill((0, 0, 0))
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

# Función para mostrar fondo de color
def display_color_background(color):
    screen.fill(color)
    pygame.display.flip()

# Función para obtener el color RGB de un color
def get_color_rgb(color):
    color_map = {
        "Rojo": (255, 0, 0),
        "Verde": (0, 255, 0),
        "Azul": (0, 0, 255),
        "Amarillo": (255, 255, 0),
        "Naranja": (255, 165, 0),
        "Morado": (128, 0, 128)
    }
    return color_map[color]

# Función principal del juego de teclas
def game_loop(song):
    global score, running, difficulty
    score = 0
    
    # Reproducir la canción seleccionada
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(-1)  # Repetir indefinidamente hasta que se detenga manualmente
    
    display_message("Presiona ENTER para comenzar.")

    # Espera hasta que el jugador presione ENTER para empezar
    waiting_for_enter = True
    while waiting_for_enter:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Tecla ENTER
                    waiting_for_enter = False
                    break

    # Juego activo
    while running:
        # Selección aleatoria de botón GPIO
        gpio_pin, color = random.choice(list(gpio_key_map.items()))
        display_message(f"Presiona el botón {color}")
        display_color_background(get_color_rgb(color))  # Muestra el fondo de color

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
                    game_loop(songs[0])  # Inicia el juego con la primera canción

        # Actualizar el fondo con el video
        update_background()

        # Solo redibujar botones si el estado cambió
        if previous_state != menu_state:
            create_buttons()
            previous_state = menu_state

        pygame.display.flip()

# Crear los botones iniciales del menú
create_buttons()

# Iniciar el menú principal
main_menu()

# Limpiar los pines GPIO al salir
GPIO.cleanup()
pygame.quit()
sys.exit()
