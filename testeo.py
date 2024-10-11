import time
import RPi.GPIO as GPIO

# Configurar los pines GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón del medio (Iniciar/Confirmar)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón 2 (Dificultad Fácil)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón 3 (Dificultad Media)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Botón 4 (Dificultad Difícil)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Botón 5 (Regresar al menú)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Botón 6 (Salir)

# Función que muestra el menú de dificultad
def difficulty_menu():
    print("Seleccione la dificultad:")
    print(" - Botón 2: Fácil")
    print(" - Botón 3: Media")
    print(" - Botón 4: Difícil")

    selected_difficulty = None
    while not selected_difficulty:
        if GPIO.input(27) == GPIO.LOW:
            selected_difficulty = "Fácil"
        elif GPIO.input(22) == GPIO.LOW:
            selected_difficulty = "Media"
        elif GPIO.input(5) == GPIO.LOW:
            selected_difficulty = "Difícil"

        # Permitir salir o volver al menú principal
        if GPIO.input(6) == GPIO.LOW:
            print("Volviendo al menú principal...")
            return None
        elif GPIO.input(13) == GPIO.LOW:
            print("Saliendo del sistema...")
            GPIO.cleanup()
            exit()

    print(f"Dificultad seleccionada: {selected_difficulty}")
    time.sleep(2)
    return selected_difficulty

# Menú principal
def main_menu():
    print("Bienvenidos a Focusboard.")  # Mensaje al iniciar
    while True:
        print("\n--- Menú Principal ---")
        print("Presione el botón del medio (Botón 1) para iniciar.")
        print(" - Botón 6: Salir")
        
        # Esperar la selección del botón del medio para continuar
        while GPIO.input(17) == GPIO.HIGH:
            if GPIO.input(13) == GPIO.LOW:
                print("Saliendo del sistema...")
                GPIO.cleanup()
                exit()
            time.sleep(0.1)
        
        print("Iniciando selección de dificultad...")
        selected_difficulty = difficulty_menu()  # Mostrar el menú de selección
        
        if selected_difficulty:
            print(f"Juego iniciado con dificultad: {selected_difficulty}")
            time.sleep(2)  # Esperar un poco antes de volver al menú principal

# Iniciar el menú principal
try:
    main_menu()
finally:
    # Limpiar los pines GPIO al salir
    GPIO.cleanup()
