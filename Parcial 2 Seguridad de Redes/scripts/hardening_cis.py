from netmiko import ConnectHandler
from datetime import datetime
import getpass

pwd_r1 = getpass.getpass("Password SSH para R1-Core: ")
pwd_sw = getpass.getpass("Password SSH para SW-LAN: ")

dispositivos = [
    {"nombre": "R1-Core", "ip": "10.24.12.1", "password": pwd_r1},
    {"nombre": "SW-LAN", "ip": "10.24.12.2", "password": pwd_sw},
]

comandos_cis = [
    "service password-encryption",
    "no ip http server",
    "no ip http secure-server",
    "logging buffered 4096",
    "line con 0",
    "exec-timeout 15 0",
    "exit",
    "line vty 0 4",
    "exec-timeout 15 0",
    "exit",
]

reporte = [
    "INFORME DE HARDENING CIS - MATRICULA 2024-2412",
    f"Fecha de ejecucion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
]

for dev in dispositivos:
    print(f"\n[+] Conectando a {dev['ip']} ({dev['nombre']})...")
    net_device = {
        "device_type": "cisco_ios",
        "host": dev["ip"],
        "username": "admin",
        "password": dev["password"],
        "secret": "enable123",
    }
    try:
        conn = ConnectHandler(**net_device)
        try:
            conn.enable()
        except Exception:
            conn.secret = dev["password"]
            conn.enable()
        print(f"[+] Aplicando politicas de hardening CIS en {dev['ip']}...")
        salida = conn.send_config_set(comandos_cis)
        conn.save_config()
        conn.disconnect()
        msg = f"[SUCCESS] Configuracion aplicada y guardada en {dev['nombre']} ({dev['ip']})"
        print(msg)
        reporte.append(msg)
        reporte.append(salida + "\n" + "-" * 50)
    except Exception as e:
        err = f"[-] Error conectando a {dev['ip']}: {e}"
        print(err)
        reporte.append(err)

with open("Informe_CIS_2024_2412.txt", "w") as f:
    f.write("\n".join(reporte))

print("\n[+] Informe generado en: Informe_CIS_2024_2412.txt")