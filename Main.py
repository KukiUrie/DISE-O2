import time
import serial
import RPi.GPIO as GPIO

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)  # Asegúrate de que el puerto sea el correcto

# Configuración de los pines de los botones y asignación a tiras específicas
GPIO.setmode(GPIO.BCM)  # Usar la numeración BCM de los pines
button_pins = {
    17: "STRIP1",  # Botón 1 controla la Tira 1
    27: "STRIP2",  # Botón 2 controla la Tira 2
    22: "STRIP3",  # Botón 3 controla la Tira 3
    5: "STRIP4",   # Botón 4 controla la Tira 4
    6: "STRIP5",   # Botón 5 controla la Tira 5
    13: "STRIP6",  # Botón 6 controla la Tira 6
    19: "STRIP7"   # Botón 7 controla la Tira 7
}

# Configurar los pines GPIO para los botones
for pin in button_pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Estado de cada tira
strip_states = {strip: False for strip in button_pins.values()}  # False = Apagado, True = Encendido

# Función para enviar un comando al Arduino
def send_command(command):
    ser.write((command + '\n').encode())  # Envía el comando con una nueva línea al final

# Bucle principal para verificar el estado de cada botón
try:
    while True:
        for pin, strip in button_pins.items():
            # Detecta si el botón ha sido presionado
            if GPIO.input(pin) == GPIO.LOW:  # El botón está presionado
                if not strip_states[strip]:
                    send_command(f"ENCENDER_{strip}")
                    strip_states[strip] = True
                    print(f"Comando enviado: ENCENDER_{strip}")
                else:
                    send_command(f"APAGAR_{strip}")
                    strip_states[strip] = False
                    print(f"Comando enviado: APAGAR_{strip}")
                
                # Espera a que se suelte el botón antes de continuar
                while GPIO.input(pin) == GPIO.LOW:
                    time.sleep(0.1)
        
        # Agrega un pequeño retardo para evitar lecturas rápidas
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Apagando todas las tiras y cerrando la conexión...")
    for strip in strip_states.keys():
        send_command(f"APAGAR_{strip}")  # Apagar todas las tiras al finalizar
    ser.close()
    GPIO.cleanup()  # Limpia la configuración de GPIO
