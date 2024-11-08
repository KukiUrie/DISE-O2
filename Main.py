import time
import serial
import RPi.GPIO as GPIO

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)  # Asegúrate de que el puerto sea el correcto

# Configuración de los pines de los botones en la Raspberry Pi
BUTTON_PINS = [17, 22, 27, 13, 5, 19, 6]  # Pines de cada botón

GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configura cada botón con resistencia pull-up

# Función para enviar un comando al Arduino
def send_command(command):
    ser.write((command + '\n').encode())  # Envía el comando con una nueva línea al final

# Bucle principal para verificar el estado de los botones
try:
    while True:
        for index, pin in enumerate(BUTTON_PINS):
            # Verifica si el botón está presionado
            if GPIO.input(pin) == GPIO.LOW:
                # Envía el comando para verificar si el usuario ha acertado (ejemplo: "CHECK_STRIP_1")
                command = f"CHECK_STRIP_{index + 1}"
                send_command(command)
                print(f"Comando enviado: {command}")

                # Espera a que se suelte el botón antes de continuar
                while GPIO.input(pin) == GPIO.LOW:
                    time.sleep(0.1)

        # Agrega un pequeño retardo para evitar lecturas demasiado rápidas
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Cerrando el juego y limpiando los pines GPIO...")
    ser.close()
    GPIO.cleanup()  # Limpia la configuración de GPIO
