import time
import RPi.GPIO as GPIO
import pygame

# Configurar los pines GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón del medio
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón 2
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón 3
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Botón 4
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Botón 5
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón 6

# Configurar LEDs
led_pins = [18, 23, 24]  # Pines de los LEDs para las 3 dificultades
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)

# Inicializar Pygame Mixer para los sonidos
pygame.mixer.init()

# Función para reproducir sonido
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

# Función para encender LEDs
def leds_on():
    for pin in led_pins:
        GPIO.output(pin, GPIO.HIGH)

# Función para apagar LEDs
def leds_off():
    for pin in led_pins:
        GPIO.output(pin, GPIO.LOW)

# Menú principal guiado por botones
def main_menu():
    print("Bienvenido a Focusboard, presione el botón del medio para iniciar")
    play_sound('welcome.mp3')  # Reproducir sonido de bienvenida
    
    # Esperar a que se presione el botón del medio
    while GPIO.input(17) == GPIO.HIGH:
        time.sleep(0.1)
    
    print("Seleccione la dificultad")
    play_sound('select_difficulty.mp3')  # Reproducir sonido de selección
    leds_on()  # Encender los LEDs

    # Esperar a que el usuario seleccione una dificultad (botones 2, 3, o 4)
    selected_difficulty = None
    while not selected_difficulty:
        if GPIO.input(27) == GPIO.LOW:
            selected_difficulty = "Fácil"
        elif GPIO.input(22) == GPIO.LOW:
            selected_difficulty = "Media"
        elif GPIO.input(5) == GPIO.LOW:
            selected_difficulty = "Difícil"

    print(f"Dificultad seleccionada: {selected_difficulty}")
    play_sound(f'{selected_difficulty.lower()}.mp3')  # Reproducir sonido de dificultad seleccionada
    leds_off()  # Apagar los LEDs

    # Aquí continuarías con el siguiente paso del juego
    # ...

# Iniciar el menú principal
try:
    main_menu()
finally:
    # Limpiar los pines GPIO al salir
    GPIO.cleanup()
