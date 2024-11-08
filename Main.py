import time
import serial
import RPi.GPIO as GPIO
import subprocess

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

# Configuración de los pines de los botones en la Raspberry Pi
BUTTON_PINS = [17, 22, 27, 13, 5, 19, 6]
GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

game_started = False
music_process = None

def send_command(command):
    ser.write((command + '\n').encode())

try:
    while True:
        if not game_started:
            for pin in BUTTON_PINS:
                if GPIO.input(pin) == GPIO.LOW:
                    if pin == 22:  # Amarillo - Fácil
                        send_command("START_GAME_EASY")
                        print("Juego iniciado en nivel fácil")
                    elif pin == 17:  # Azul - Medio
                        send_command("START_GAME_MEDIUM")
                        print("Juego iniciado en nivel medio")
                    elif pin == 5:  # Blanco - Difícil
                        send_command("START_GAME_HARD")
                        print("Juego iniciado en nivel difícil")

                    # Inicia la música
                    music_process = subprocess.Popen(["aplay", "cancion.wav"])
                    game_started = True
                    time.sleep(0.5)
                    break
        else:
            for index, pin in enumerate(BUTTON_PINS):
                if GPIO.input(pin) == GPIO.LOW:
                    command = f"CHECK_STRIP_{index + 1}"
                    send_command(command)
                    print(f"Comando enviado: {command}")
                    while GPIO.input(pin) == GPIO.LOW:
                        time.sleep(0.1)
            time.sleep(0.1)

except KeyboardInterrupt:
    print("Cerrando el juego y limpiando los pines GPIO...")
    if music_process:
        music_process.terminate()
    ser.close()
    GPIO.cleanup()
