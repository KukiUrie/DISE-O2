import time
import serial
import RPi.GPIO as GPIO

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)  # Asegúrate de que el puerto sea el correcto

# Configuración de los pines de los botones en la Raspberry Pi
BUTTON_PINS = [17, 22, 27, 6, 5, 13, 19]  # Lista con todos los pines de los botones

GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Activa resistencia pull-up interna para cada botón

# Estado inicial
leds_on = False  # Variable para rastrear el estado actual de las tiras de LEDs

# Función para enviar un comando al Arduino
def send_command(command):
    ser.write((command + '\n').encode())  # Envía el comando con una nueva línea al final

# Bucle principal para verificar el estado de los botones
try:
    while True:
        # Revisa el estado de todos los botones
        button_pressed = any(GPIO.input(pin) == GPIO.LOW for pin in BUTTON_PINS)  # True si cualquier botón está presionado

        if button_pressed:
            if not leds_on:
                send_command("ENCENDER")
                leds_on = True
                print("Comando enviado: ENCENDER")
            else:
                send_command("APAGAR")
                leds_on = False
                print("Comando enviado: APAGAR")
            
            # Espera a que se suelten todos los botones antes de continuar
            while any(GPIO.input(pin) == GPIO.LOW for pin in BUTTON_PINS):
                time.sleep(0.1)
        
        # Agrega un pequeño retardo para evitar lecturas rápidas
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Apagando todas las tiras y cerrando la conexión...")
    send_command("APAGAR")  # Apagar todas las tiras al finalizar
    ser.close()
    GPIO.cleanup()  # Limpia la configuración de GPIO
