import pygame
import cv2
import sys
import random
import time
import RPi.GPIO as GPIO  # Importa la biblioteca RPi.GPIO para los botones físicos

# ===========================
# Configuración de GPIO
# ===========================

GPIO.setmode(GPIO.BCM)  # Usamos la numeración BCM para los pines GPIO

# Asignar pines GPIO a botones físicos
button_pin_1 = 17  # Conectar el primer botón físico al pin GPIO 17
button_pin_2 = 27  # Conectar el segundo botón físico al pin GPIO 27
button_pin_3 = 22  # Conectar el tercer botón físico al pin GPIO 22

# Configurar los pines como entradas con resistencia pull-up
GPIO.setup(button_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ===========================
# Inicialización de Pygame
# ===========================

pygame.init()

# Tamaño de la pantalla
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Título de la ventana y icono
pygame.display.set_caption("Focusboard")
try:
    icon_image = pygame.image.load("icon1.png")
    pygame.display.set_icon(icon_image)
except pygame.error:
    print("No se pudo cargar el icono. Asegúrate de que 'icon1.png' esté en el directorio correcto.")

# Configuración de fuente
font = pygame.font.Font(None, 40)

# Cargar la imagen personalizada del botón "Start"
try:
    start_button_image = pygame.image.load("start2.png")  # Asegúrate de tener esta imagen
    start_button_image = pygame.transform.scale(start_button_image, (120, 80))  # Escalar imagen
except pygame.error:
    print("No se pudo cargar la imagen del botón Start. Asegúrate de que 'start2.png' esté en el directorio correcto.")
    start_button_image = None

# Variables para animación básica (botón Start más grande al pasar el ratón)
start_button_hover = False
start_button_rect = start_button_image.get_rect(center=(screen_width // 2, screen_height // 2)) if start_button_image else None

# ===========================
# Cargar el Video con OpenCV
# ===========================

video_path = "background.mp4"  # Asegúrate de tener este video
cap = cv2.VideoCapture(video_path)

# Verificar si el video se cargó correctamente
if not cap.isOpened():
    print("No se pudo cargar el video.")
    GPIO.cleanup()
    pygame.quit()
    sys.exit()

# Obtener FPS del video para sincronizar
fps = cap.get(cv2.CAP_PROP_FPS)
frame_delay = int(1000 / fps) if fps > 0 else 33  # Tiempo de espera entre cuadros

# ===========================
# Colores
# ===========================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ===========================
# Mapeo de Teclas y Colores
# ===========================

key_color_map = {
    pygame.K_z: "Rojo",
    pygame.K_x: "Verde",
    pygame.K_c: "Azul",
    pygame.K_v: "Amarillo"
}

# ===========================
# Variables Globales
# ===========================

score = 0
running = True
game_active = False

# ===========================
# Funciones Auxiliares
# ===========================

def display_message(message, y_offset=0):
    """Muestra un mensaje centrado en la pantalla."""
    screen.fill((0, 0, 0))  # Fondo negro
    text = font.render(message, True, WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2,
                       screen_height // 2 - text.get_height() // 2 + y_offset))
    pygame.display.flip()

def display_score():
    """Muestra la puntuación actual en la esquina superior izquierda."""
    score_text = font.render(f"Puntuación: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def display_video_background():
    """Captura un frame del video y lo muestra como fondo en Pygame."""
    ret, frame = cap.read()
    if not ret:
        # Si el video terminó, reiniciarlo
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir a RGB
        frame = cv2.resize(frame, (screen_width, screen_height))  # Ajustar tamaño
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))  # Convertir a superficie Pygame
        screen.blit(frame_surface, (0, 0))  # Mostrar en pantalla

def handle_buttons():
    """Verifica si alguno de los botones físicos ha sido presionado."""
    global score
    button_pressed = False
    if GPIO.input(button_pin_1) == GPIO.LOW:
        time.sleep(0.1)  # Debounce
        if GPIO.input(button_pin_1) == GPIO.LOW:
            score += 1
            button_pressed = True
    elif GPIO.input(button_pin_2) == GPIO.LOW:
        time.sleep(0.1)
        if GPIO.input(button_pin_2) == GPIO.LOW:
            score += 1
            button_pressed = True
    elif GPIO.input(button_pin_3) == GPIO.LOW:
        time.sleep(0.1)
        if GPIO.input(button_pin_3) == GPIO.LOW:
            score += 1
            button_pressed = True
    return button_pressed

def game_loop(song):
    """Función principal del juego de teclas."""
    global score, running, game_active
    score = 0
    game_active = True

    # Reproducir la canción seleccionada
    try:
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)  # Repetir indefinidamente
    except pygame.error:
        print("No se pudo reproducir la canción. Asegúrate de que el archivo exista.")

    display_message("Presiona Enter para comenzar.")

    # Espera hasta que el jugador presione Enter o el botón Start
    while not game_active and running:
        display_video_background()
        display_message("Presiona Enter para comenzar.")
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_active = True

        # Detectar si se presionó el botón físico Start (si está disponible)
        if start_button_image and start_button_rect.collidepoint(pygame.mouse.get_pos()):
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:
                game_active = True

        # También verifica si algún botón físico fue presionado para iniciar el juego
        if handle_buttons():
            game_active = True

    # Juego activo
    while running and game_active:
        # Selección aleatoria de tecla
        key, color = random.choice(list(key_color_map.items()))
        display_message(f"Presiona {pygame.key.name(key).upper()} ({color})")
        pygame.display.flip()

        waiting_for_input = True
        start_time = time.time()

        while waiting_for_input and running and game_active:
            display_video_background()
            display_score()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == key:
                        score += 1
                        waiting_for_input = False
                    else:
                        display_message("Tecla incorrecta. Inténtalo de nuevo.", y_offset=40)
                        pygame.display.flip()
                        time.sleep(1)
                        waiting_for_input = False

            # Detecta si se presionó algún botón físico
            if handle_buttons():
                waiting_for_input = False

            # Control del tiempo de respuesta (3 segundos por intento)
            if time.time() - start_time > 3:
                display_message("Tiempo agotado. Inténtalo de nuevo.", y_offset=40)
                pygame.display.flip()
                time.sleep(1)
                waiting_for_input = False

        # Muestra la puntuación actual
        display_video_background()
        display_score()
        pygame.display.flip()
        time.sleep(1)

    # Detener la música cuando el juego termine
    pygame.mixer.music.stop()

# ===========================
# Bucle Principal
# ===========================

def main():
    global running
    try:
        # Iniciar el juego con una canción específica
        game_loop("cancion.mp3")  # Reemplaza "cancion.mp3" con la ruta a tu canción

        # Bucle principal para mantener el programa activo hasta que se cierre
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Actualizar el fondo de video
            display_video_background()

            # Si tienes un botón Start en pantalla, puedes dibujarlo aquí
            if start_button_image and not game_active:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    start_button_hover = True
                else:
                    start_button_hover = False

                # Opcional: cambiar el tamaño del botón al pasar el ratón
                if start_button_hover:
                    button_image = pygame.transform.scale(start_button_image, (140, 100))
                else:
                    button_image = pygame.transform.scale(start_button_image, (120, 80))

                screen.blit(button_image, start_button_rect.topleft)

            # Mostrar la puntuación
            display_score()

            pygame.display.flip()
            pygame.time.delay(30)

    finally:
        # Limpiar los GPIO y cerrar Pygame al finalizar
        GPIO.cleanup()
        cap.release()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
    

