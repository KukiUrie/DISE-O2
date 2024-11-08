import time
import serial
import RPi.GPIO as GPIO

ser = serial.Serial('/dev/ttyACM0', 9600)

BUTTON_PINS = [17, 22, 27, 13, 5, 19, 6]
GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

game_started = False

def send_command(command):
    ser.write((command + '\n').encode())

try:
    while True:
        if not game_started:
            for pin in BUTTON_PINS:
                if GPIO.input(pin) == GPIO.LOW:
                    send_command("START_GAME")
                    print("Juego iniciado")
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
    ser.close()
    GPIO.cleanup()
