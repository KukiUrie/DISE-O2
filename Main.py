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

game_started = False  # Estado del juego (no iniciado)
difficulty_command_sent = False  # Para asegurar que el comando de inicio solo se envíe una vez

def send_command(command):
    ser.write((command + '\n').encode())
    print(f"Comando enviado a Arduino: {command}")

try:
    while True:
        if not game_started:
            # Espera a que un botón de dificultad sea presionado para iniciar el juego
            for pin, command in BUTTON_PINS.items():
                if GPIO.input(pin) == GPIO.LOW:
                    print(f"Botón en GPIO {pin} presionado: Enviando {command} para iniciar el juego")
                    send_command(command)  # Envía el comando de inicio de dificultad
                    game_started = True
                    difficulty_command_sent = True
                    time.sleep(0.5)  # Evita múltiples envíos rápidos
                    break
        else:
            # Si el juego está en curso, los botones sirven como comandos de verificación
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                print(f"Respuesta del Arduino: {response}")
                if response == "FIN_JUEGO":
                    game_started = False  # Juego terminado, listo para reiniciar
                    difficulty_command_sent = False  # Permitir un nuevo inicio

            # Usar los mismos botones para enviar "CHECK_STRIP_X" durante el juego
            for index, (pin, _) in enumerate(BUTTON_PINS.items(), start=1):
                if GPIO.input(pin) == GPIO.LOW:
                    command = f"CHECK_STRIP_{index}"
                    send_command(command)
                    print(f"Comando enviado para juego: {command}")
                    time.sleep(0.1)

except KeyboardInterrupt:
    print("Cerrando el juego y limpiando los pines GPIO...")
    ser.close()
    GPIO.cleanup()
