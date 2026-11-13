# Examen Parcial #2 — Seguridad de Redes (PNETLab)

**Estudiante:** Jean Heriberto Alvarez Sierra  
**Matrícula:** `2024-2412`  
**Institución:** Instituto Tecnológico de Las Américas (ITLA)  
**Plataforma de Emulación:** PNETLab / VMware Workstation  
** Link del video a Youtube:** 

---

## 1. Descripción General

Este repositorio contiene las configuraciones, scripts de automatización, evidencias gráficas y documentación técnica correspondientes al **Parcial #2 de Seguridad de Redes**. La infraestructura implementa una red empresarial segmentada bajo el esquema de direccionamiento **`10.24.12.0/24`** (derivado de la matrícula `2024-2412`), integrando controles de endurecimiento (*CIS Benchmarks*) mediante Python/Netmiko, autenticación centralizada AAA con RADIUS sobre Active Directory, seguridad a nivel de puerto (*Port-Security*), gestión remota cifrada mediante SSHv2 y monitoreo continuo con Zabbix vía SNMP.

---

## 2. Diagrama de la Topología

La topología implementada en PNETLab sigue un diseño jerárquico que conecta la salida perimetral hacia el núcleo de enrutamiento (`R1-Core`) y la capa de acceso conmutada (`SW-LAN`), donde convergen los servidores de identidad, monitoreo y estaciones de auditoría:

```text
+-------------------------------------------------------+
|                   Internet / Net Cloud                |
|             (Salida WAN y Acceso NAT)                 |
|                 Red: 192.168.141.0/24                 |
+-------------------------------------------------------+
                            |
                            | (port1 - WAN/NAT)
                            v
+-------------------------------------------------------+
|              Fortinet FortiGate 7.0.9                 |
|             (Seguridad Perimetral / NAT)              |
|                  port2: Enlace Core                   |
+-------------------------------------------------------+
                            |
                            | (port2)
                            | (e2/0)
                            v
+-------------------------------------------------------+
|             Router Cisco C7200 (R1-Core)              |
|      (Gateway LAN / Servidor DHCP / AAA RADIUS)       |
|              e2/1: 10.24.12.1/24                      |
+-------------------------------------------------------+
                            |
                            | (e2/1)
                            | (Gi0/0)
                            v
+-------------------------------------------------------+
|            Switch Cisco IOSvL2 (SW-LAN)               |
|     (Capa de Acceso / Port-Security / SNMP / SSH)     |
|               SVI Vlan1: 10.24.12.2/24                |
+-------------------------------------------------------+
       |              |              |              |
   (Gi0/1)        (Gi0/2)        (Gi0/3)        (Gi1/1)
       |              |              |              |
       v              v              v              v
+-------------+ +-------------+ +-------------+ +-------------+
|   Ubuntu    | |   Ubuntu    | |   Windows   | |    Kali     |
|   Desktop   | |   Server    | | Server 2025 | |    Linux    |
|  (Cliente)  | |  (Zabbix)   | |  (AD / NPS) | | (Auditoría) |
|10.24.12.21  | |10.24.12.11  | |10.24.12.10  | |10.24.12.23  |
|   (DHCP)    | | (Estática)  | | (Estática)  | |   (DHCP)    |
+-------------+ +-------------+ +-------------+ +-------------+
```

### Vista de la Topología en PNETLab

![Topología en PNETLab](img/01_topologia_pnetlab.png)

---

## 3. Tabla de Direccionamiento IP

| Dispositivo | Rol en la Topología | Interfaz | Dirección IP | Máscara | Gateway | Método |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Net (Cloud)** | Salida WAN / Puente NAT | `Cloud` | `192.168.141.0/24` | `255.255.255.0` | — | NAT |
| **FortiGate 7.0.9** | Firewall Perimetral | `port1` / `port2` | `192.168.141.x` | `255.255.255.0` | `192.168.141.2` | DHCP / Tránsito |
| **R1-Core (C7200)** | Router Core, DHCP y Cliente AAA | `e2/1` | `10.24.12.1` | `255.255.255.0` | — | Estática |
| **SW-LAN (IOSvL2)** | Switch de Acceso, SNMP y Port-Security | `Vlan1` | `10.24.12.2` | `255.255.255.0` | `10.24.12.1` | Estática |
| **Windows Server 2025** | Active Directory (`itla.local`), DNS y NPS RADIUS | `Ethernet0` | `10.24.12.10` | `255.255.255.0` | `10.24.12.1` | Estática |
| **Ubuntu Server** | Servidor de Monitoreo Zabbix 6.0 LTS | `ens33` | `10.24.12.11` | `255.255.255.0` | `10.24.12.1` | Estática |
| **Ubuntu Desktop** | Cliente LAN, Gestión SSH y Hardening Netmiko | `ens37` | `10.24.12.21` | `255.255.255.0` | `10.24.12.1` | DHCP (`LAN_2024_2412`) |
| **Kali Linux** | Estación de Pruebas y Auditoría | `eth1` | `10.24.12.23` | `255.255.255.0` | `10.24.12.1` | DHCP (`LAN_2024_2412`) |

---

## 4. Estructura del Repositorio

```text
Parcial 2 Seguridad de Redes/
├── configs/
│   ├── FortiGate-VM64-KVM_7-0_0444_202611130834.conf
│   ├── R1_Core_runningConfig.txt
│   └── SW1_runningConfig.txt
├── img/
│   ├── 01_topologia_pnetlab.png
│   ├── 02_r1_dhcp_config.png
│   ├── 03_r1_ssh_vty.png
│   ├── 04_r1_aaa_config.png
│   ├── 05_r1_consola_radius.png
│   ├── 06_sw_ssh_usuarios.png
│   ├── 07_sw_port_security_config.png
│   ├── 08_sw_port_security_violacion.png
│   ├── 09_sw_snmp_config.png
│   ├── 10_win_ad_usuario.png
│   ├── 11_win_nps_politica.png
│   ├── 12_ubuntu_ip_ping.png
│   ├── 13_ubuntu_ssh.png
│   ├── 14_ubuntu_zabbix.png
│   └── 15_ubuntu_zabbix_latest_data.png
├── scripts/
│   ├── hardening_cis.py
│   ├── Informe_CIS_2024_2412.txt
│   ├── R1-Core_Scripts.txt
│   ├── Switch_Scripts.txt
│   └── Zabbix_server_script.txt
├── JeanAlvarez_20242412_p2.txt
└── README.md
```

---

## 5. Controles de Seguridad Implementados

1. **Endurecimiento Automatizado (CIS Benchmarks):** Script en Python (`scripts/hardening_cis.py`) utilizando `netmiko` para aplicar cifrado de contraseñas (`service password-encryption`), deshabilitación de servicios web inseguros (`no ip http server`, `no ip http secure-server`), registro local (`logging buffered 4096`) y tiempos de inactividad (`exec-timeout 15 0`) en consola y líneas VTY, generando el reporte automático `scripts/Informe_CIS_2024_2412.txt`.
2. **Seguridad en Capa 2 (Port-Security):** Configurado en los puertos de acceso de `SW-LAN` (`Gi0/1 - 3`, `Gi1/0`) con un límite máximo de **2 direcciones MAC** y modo de violación **`shutdown`**, deshabilitando el puerto (`err-disabled`) ante suplantación o exceso de direcciones físicas.
3. **Autenticación Centralizada AAA (RADIUS):** Integración entre `R1-Core` y **Windows Server 2025 (NPS + Active Directory)** para autenticar usuarios del grupo `Admins_Red` (`admin_red`) con privilegio nivel 15 (`Cisco-AV-Pair = shell:priv-lvl=15`), restringido exclusivamente a las líneas físicas **Consola (`con 0`)** y **Auxiliar (`aux 0`)**.
4. **Gestión Remota Segura (SSHv2):** Acceso administrativo habilitado únicamente mediante **SSH versión 2** con credenciales locales cifradas (`username admin secret`), bloqueando por completo el protocolo Telnet en las líneas VTY.
5. **Monitoreo Centralizado (SNMP + Zabbix):** Supervisión en tiempo real del estado e interfaces de `SW-LAN` desde **Zabbix Server 6.0** mediante SNMPv2c con comunidad de solo lectura (`Zabbix_Parcial2 RO`).

---

## 6. Evidencias de Configuración y Pruebas (`img/`)

### Router Core (`R1-Core`)

* **`02_r1_dhcp_config` — Configuración de Pool DHCP y Asignaciones Activas (`10.24.12.0/24`):**  
  ![02_r1_dhcp_config](img/02_r1_dhcp_config.jpg)
* **`03_r1_ssh_vty` — Habilitación de SSHv2 y Restricción en Líneas VTY:**  
  ![03_r1_ssh_vty](img/03_r1_ssh_vty.jpg)
* **`04_r1_aaa_config` — Políticas AAA y Grupo RADIUS en Consola/Auxiliar:**  
  ![04_r1_aaa_config](img/04_r1_aaa_config.jpg)
* **`05_r1_consola_radius` — Validación de Inicio de Sesión en Consola con Usuario de Dominio (`admin_red`):**  
  ![05_r1_consola_radius](img/05_r1_consola_radius.jpg)

### Switch de Acceso (`SW-LAN`)

* **`06_sw_ssh_usuarios` — Usuarios Locales Cifrados y Acceso SSHv2 en `SW-LAN`:**  
  ![06_sw_ssh_usuarios](img/06_sw_ssh_usuarios.jpg)
* **`07_sw_port_security_config` — Configuración de Port-Security (Máximo 2 MACs y Acción Shutdown):**  
  ![07_sw_port_security_config](img/07_sw_port_security_config.jpg)
* **`08_sw_port_security_violacion` — Detección de Violación Port-Security y Estado `err-disabled`:**  
  ![08_sw_port_security_violacion](img/08_sw_port_security_violacion.jpg)
* **`09_sw_snmp_config` — Configuración de Comunidad SNMP de Solo Lectura:**  
  ![09_sw_snmp_config](img/09_sw_snmp_config.jpg)

### Servidores y Estaciones de Trabajo (`Windows Server`, `Ubuntu` y `Zabbix`)

* **`10_win_ad_usuario` — Usuario `admin_red` y Grupo `Admins_Red` en Active Directory:**  
  ![10_win_ad_usuario](img/10_win_ad_usuario.jpg)
* **`11_win_nps_politica` — Política de Red en NPS (`Politica_Routers`) con Atributo de Privilegio 15:**  
  ![11_win_nps_politica](img/11_win_nps_politica.jpg)
* **`12_ubuntu_ip_ping` — Asignación IP por DHCP y Conectividad ICMP desde Ubuntu Desktop:**  
  ![12_ubuntu_ip_ping](img/12_ubuntu_ip_ping.jpg)
* **`13_ubuntu_ssh` — Prueba de Acceso SSH Local y Aislamiento del Usuario RADIUS:**  
  ![13_ubuntu_ssh](img/13_ubuntu_ssh.jpg)
* **`14_ubuntu_zabbix` — Disponibilidad SNMP del Host `SW-LAN` en Zabbix Server:**  
  ![14_ubuntu_zabbix](img/14_ubuntu_zabbix.jpg)
* **`15_ubuntu_zabbix_latest_data` — Recolección de Métricas en Tiempo Real (*Latest Data*) en Zabbix:**  
  ![15_ubuntu_zabbix_latest_data](img/15_ubuntu_zabbix_latest_data.jpg)
