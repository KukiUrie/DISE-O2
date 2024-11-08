import time
import serial
import RPi.GPIO as GPIO

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

# Configuración de los pines de los botones en la Raspberry Pi
BUTTON_PINS = {
    22: "START_GAME_EASY",    # Amarillo - Dificultad Fácil
    17: "START_GAME_MEDIUM",  # Azul - Dificultad Media
    5: "START_GAME_HARD"      # Blanco - Dificultad Difícil
}

GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

game_started = False

def send_command(command):
    ser.write((command + '\n').encode())
    print(f"Comando enviado a Arduino: {command}")  # Mensaje de depuración

try:
    while True:
        if not game_started:
            # Espera a que un botón de dificultad sea presionado para iniciar el juego
            for pin, command in BUTTON_PINS.items():
                if GPIO.input(pin) == GPIO.LOW:
                    print(f"Botón en GPIO {pin} presionado: Enviando {command}")
                    send_command(command)  # Envía el comando de inicio de dificultad
                    game_started = True
                    time.sleep(0.5)  # Evita múltiples envíos rápidos
                    break
        else:
            # Escucha la respuesta del Arduino para saber si el jugador acertó o falló
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                print(f"Respuesta del Arduino: {response}")
                if response == "FIN_JUEGO":
                    game_started = False  # Juego terminado, listo para reiniciar

            # Verifica el estado de los botones durante el juego
            for index, pin in enumerate(BUTTON_PINS):
                if GPIO.input(pin) == GPIO.LOW:
                    command = f"CHECK_STRIP_{index + 1}"
                    send_command(command)
                    time.sleep(0.1)

except KeyboardInterrupt:
    print("Cerrando el juego y limpiando los pines GPIO...")
    ser.close()
    GPIO.cleanup()
