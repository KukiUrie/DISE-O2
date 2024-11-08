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
failed_attempts = 0  # Contador de intentos fallidos
max_attempts = 5     # Número máximo de intentos permitidos

def send_command(command):
    ser.write((command + '\n').encode())

try:
    while True:
        if not game_started:
            # Reinicia el contador de intentos fallidos
            failed_attempts = 0
            # Espera el comando para iniciar el juego con la dificultad elegida
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

                    # Inicia la música y el juego
                    music_process = subprocess.Popen(["aplay", "cancion.wav"])
                    game_started = True
                    time.sleep(0.5)
                    break
        else:
            # Verifica si se ha alcanzado el límite de intentos fallidos
            if failed_attempts >= max_attempts:
                print("Juego terminado. Se alcanzó el número máximo de intentos fallidos.")
                send_command("END_GAME")  # Envía el comando para finalizar el juego en Arduino
                if music_process:
                    music_process.terminate()  # Detiene la música
                game_started = False  # Reinicia el estado del juego para volver a empezar
                time.sleep(1)  # Pausa antes de reiniciar el ciclo
                continue

            # Verifica el estado de los botones durante el juego
            for index, pin in enumerate(BUTTON_PINS):
                if GPIO.input(pin) == GPIO.LOW:
                    command = f"CHECK_STRIP_{index + 1}"
                    send_command(command)
                    print(f"Comando enviado: {command}")

                    # Verifica la respuesta del Arduino para saber si el intento fue correcto o no
                    response = ser.readline().decode().strip()  # Lee la respuesta del Arduino
                    if response == "ERROR":
                        print("Intento fallido.")
                        failed_attempts += 1  # Incrementa el contador de intentos fallidos
                    elif response == "CORRECTO":
                        print("Intento correcto.")
                        failed_attempts = 0  # Reinicia el contador si el intento es correcto

                    # Espera a que se suelte el botón antes de continuar
                    while GPIO.input(pin) == GPIO.LOW:
                        time.sleep(0.1)
            time.sleep(0.1)

except KeyboardInterrupt:
    print("Cerrando el juego y limpiando los pines GPIO...")
    send_command("END_GAME")  # Finaliza el juego en Arduino si se interrumpe
    if music_process:
        music_process.terminate()
    ser.close()
    GPIO.cleanup()
