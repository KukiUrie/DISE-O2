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
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Boton 4 en pin 5
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Boton 5 en pin 6
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Boton 6 en pin 13

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
    
    display_message("Presiona un botón para comenzar.")

    # Espera hasta que el jugador presione un botón GPIO
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return  # Salida correcta del bucle
        for pin, btn_color in gpio_key_map.items():
            if GPIO.input(pin) == GPIO.LOW:  # Si el botón se presiona
                break
        else:
            continue
        break

    # Juego activo
    while running:
        # Selección aleatoria de botón GPIO
        gpio_pin, color = random.choice(list(gpio_key_map.items()))
        display_message(f"Presiona el botón {color}")
        display_color_background(get_color_rgb(color))  # Muestra el fondo de color

        # Espera la interacción del usuario
        waiting_for_input = True
        start_time = time.time()
        
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return  # Salida correcta del bucle

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

# Función para manejar las dificultades seleccionadas
def handle_difficulty_selection(selected_difficulty):
    global difficulty
    difficulty = selected_difficulty  # Actualiza la dificultad según lo seleccionado
    display_message(f"Dificultad seleccionada: {difficulty}")
    pygame.time.delay(1000)

# Diccionario para almacenar el estado del menú
menu_state = {
    'main': True,
    'level': False,
    'difficulty': False,
    'Cancion': False
}

# Variables para botones
start_button = None
level_buttons = []
difficulty_buttons = []
song_buttons = []
back_button = None

# Lista de canciones (asumiendo que tienes tres canciones en formato .mp3)
songs = ["cancion1.mp3", "cancion2.mp3", "cancion3.mp3"]

# Crear botones según el estado del menú
def create_buttons():
    global start_button, level_buttons, difficulty_buttons, song_buttons, back_button
    if menu_state['main']:
        start_button = create_start_button()
        back_button = None
    elif menu_state['level']:
        num_levels = 5  # Número de niveles
        button_width = 120
        button_height = 50
        spacing = (screen_width - (num_levels * button_width)) // (num_levels + 1)  # Espaciado dinámico y centrado

        level_buttons = [
            create_button(f"Level {i+1}", spacing + i * (button_width + spacing), 250, button_width, button_height, BLUE)
            for i in range(num_levels)
        ]
        back_button = create_button("Back", 350, 350, 100, 50, BLUE)
    elif menu_state['difficulty']:
        num_difficulties = 3  # Número de dificultades
        button_width = 150
        button_height = 50
        spacing = (screen_width - (num_difficulties * button_width)) // (num_difficulties + 1)  # Espaciado dinámico

        difficulty_buttons = [
            create_button(difficulty, spacing + i * (button_width + spacing), 250, button_width, button_height, BLUE)
            for i, difficulty in enumerate(["Facil", "Medio", "Dificil"])
        ]
        back_button = create_button("Back", 350, 350, 100, 50, BLUE)
    elif menu_state['Cancion']:
        num_songs = len(songs)  # Número de canciones
        button_width = 100
        button_height = 50
        spacing = (screen_width - (num_songs * button_width)) // (num_songs + 1)  # Espaciado dinámico

        song_buttons = [
            create_button(f"Cancion {i+1}", spacing + i * (button_width + spacing), 250, button_width, button_height, BLUE)
            for i in range(num_songs)
        ]
        back_button = create_button("Back", 350, 350, 100, 50, BLUE)

# Crear botón de inicio
def create_start_button():
    button_width = 120
    button_height = 80
    x_pos = screen_width // 2 - button_width // 2
    y_pos = screen_height // 2 - button_height // 2
    return pygame.Rect(x_pos, y_pos, button_width, button_height)

# Crear botón de nivel
def create_button(text, x, y, width, height, color):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, button_rect)
    button_text = font.render(text, True, WHITE)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    pygame.display.flip()  # Actualiza la pantalla con el botón renderizado
    return button_rect

# Loop del menú principal
def main_menu():
    global start_button, running, menu_state
    clock = pygame.time.Clock()

    while running:
        create_buttons()
        
        # Revisar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return  # Salida correcta del bucle

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button and start_button.collidepoint(event.pos) and menu_state['main']:
                    menu_state['main'] = False
                    menu_state['level'] = True
                    create_buttons()  # Redibujar botones para el siguiente menú
                    
                if back_button and back_button.collidepoint(event.pos):
                    menu_state = {'main': True, 'level': False, 'difficulty': False, 'Cancion': False}

                # Lógica para manejar la selección de nivel
                for i, button in enumerate(level_buttons):
                    if button.collidepoint(event.pos):
                        menu_state = {'main': False, 'level': False, 'difficulty': True, 'Cancion': False}
                        create_buttons()

                # Lógica para manejar la selección de dificultad
                for i, button in enumerate(difficulty_buttons):
                    if button.collidepoint(event.pos):
                        selected_difficulty = ["Facil", "Medio", "Dificil"][i]
                        handle_difficulty_selection(selected_difficulty)
                        menu_state = {'main': False, 'level': False, 'difficulty': False, 'Cancion': True}
                        create_buttons()

                # Lógica para manejar la selección de canción
                for i, button in enumerate(song_buttons):
                    if button.collidepoint(event.pos):
                        selected_song = songs[i]
                        game_loop(selected_song)  # Iniciar el juego con la canción seleccionada

        # Actualizar el video de fondo
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reiniciar el video
            continue

        # Convertir el frame de BGR a RGB para Pygame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb)
        frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))
        screen.blit(frame_surface, (0, 0))

        # Dibuja el botón "Start" en el menú principal
        if start_button and menu_state['main']:
            if start_button_hover:
                pygame.draw.rect(screen, (0, 255, 0), start_button)  # Cambiar el color cuando el ratón está sobre el botón
            screen.blit(start_button_image, (start_button.x, start_button.y))

        # Actualiza la pantalla
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

# Inicia el menú principal
main_menu()
