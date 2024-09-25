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
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Boton 5 en pin 6
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Boton 6 en pin 13

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
# Mapeo actualizado para 3 botones
gpio_key_map = {
    17: "Rojo",
    27: "Verde",
    22: "Azul",
    5: " Amarillo",
    6: "Naranja",
    13: "Morado"
}

# Variables globales
score = 0
running = True

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
        # Selección aleatoria de botón GPIO
        gpio_pin, color = random.choice(list(gpio_key_map.items()))
        display_message(f"Presiona el botón {color}")
        
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
        # Botón de inicio personalizado con imagen y posible animación
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

# Función para crear el botón "Start" personalizado
def create_start_button():
    global start_button_hover

    # Animar botón al pasar el ratón por encima
    button_width = 120 if not start_button_hover else 140
    button_height = 60 if not start_button_hover else 80

    # Escalar la imagen del botón según si está "hovered" o no
    button_image = pygame.transform.scale(start_button_image, (button_width, button_height))

    # Obtener la posición centrada del botón en la pantalla
    button_rect = button_image.get_rect(center=(screen_width // 2, screen_height // 2))

    # Dibujar el botón en la pantalla
    screen.blit(button_image, button_rect)

    return button_rect

# Función para crear botones generales
def create_button(text, x, y, w, h, color):
    button_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, button_rect)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

# Bucle principal del juego
running = True
selected_song = None

while running:
    update_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if menu_state['main']:
                if start_button and start_button.collidepoint(event.pos):
                    menu_state['main'] = False
                    menu_state['level'] = True
                    create_buttons()

            elif menu_state['level']:
                for i, btn in enumerate(level_buttons):
                    if btn.collidepoint(event.pos):
                        menu_state['level'] = False
                        menu_state['difficulty'] = True
                        create_buttons()

            elif menu_state['difficulty']:
                for i, btn in enumerate(difficulty_buttons):
                    if btn.collidepoint(event.pos):
                        menu_state['difficulty'] = False
                        menu_state['Cancion'] = True
                        create_buttons()

            elif menu_state['Cancion']:
                for i, btn in enumerate(song_buttons):
                    if btn.collidepoint(event.pos):
                        selected_song = songs[i]
                        menu_state['Cancion'] = False
                        game_loop(selected_song)  # Pasa la canción seleccionada al juego

            if back_button and back_button.collidepoint(event.pos):
                if menu_state['level']:
                    menu_state['level'] = False
                    menu_state['main'] = True
                elif menu_state['difficulty']:
                    menu_state['difficulty'] = False
                    menu_state['level'] = True
                elif menu_state['Cancion']:
                    menu_state['Cancion'] = False
                    menu_state['difficulty'] = True
                create_buttons()

    if menu_state['main']:
        start_button = create_start_button()

    create_buttons()

    pygame.display.flip()
    pygame.time.delay(frame_delay)

cap.release()
pygame.quit()
GPIO.cleanup()  # Limpiar los pines GPIO al salir
sys.exit()
