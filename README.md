# Enawall

**Gestor de Firewall de Windows con interfaz gráfica — estética Matrix/Cyberpunk**

Herramienta de seguridad para Windows que permite gestionar el Firewall de Windows, monitorear tráfico de red en tiempo real, detectar ataques por flags TCP y auditar todas las acciones del sistema.

---

## Descarga

Descarga el ejecutable desde la sección [**Releases**](../../releases/latest) — no requiere instalación.

---

## Características

| Módulo | Descripción |
|--------|-------------|
| **Cuadro de Mando** | Estado global, puntuación de seguridad, métricas clave y feed de eventos en tiempo real |
| **Dashboard** | Gráficas de tráfico TX/RX, top procesos con red activa, estado de interfaces |
| **Tráfico** | Ancho de banda desglosado por proceso |
| **Alertas** | Umbrales en KB/s o MB/s con notificación emergente al superarlos |
| **Reglas** | Gestión completa del Firewall: añadir, eliminar, exportar, limpiar duplicados, restablecer |
| **Scanner** | Escáner de puertos TCP con rango configurable |
| **TCP** | Conexiones TCP/UDP en vivo con log automático |
| **Flags TCP** | Detecta y bloquea ataques: SYN Flood, Xmas Scan, NULL Scan, FIN Scan, RST Flood |
| **Red** | IPs locales, gateway, interfaces, ipconfig completo |
| **Audit** | Log de auditoría completo con backups automáticos antes de cada operación destructiva |

### Seguridad integrada
- Contraseña de acceso con hash SHA-256 (nunca en texto plano)
- Clave de recuperación para resetear contraseña olvidada
- Log de auditoría cronológico en `%APPDATA%\Enawall\audit.log`
- Backup automático de reglas antes de resets o borrados masivos
- Una sola instancia activa (mutex global)
- Requiere y solicita privilegios de administrador automáticamente (UAC)

### Buenas prácticas de seguridad (NIST / CIS)
Indicadores visuales de cumplimiento con puntuación 0–100:
- Bloqueo de puertos peligrosos: RDP (3389), SMB (445), Telnet (23), FTP (21), NetBIOS (139), WinRM (5985), VNC (5900)
- Política inbound por defecto: BLOCK
- Sin reglas ALLOW con IP origen "Any"
- Logging del firewall activo

---

## Requisitos

- Windows 10 / 11 (64 bits)
- Privilegios de administrador (la app lo solicita automáticamente via UAC)
- Sin instalación — ejecutable único `.exe`

---

## Uso

1. Descarga `Enawall.exe` desde [Releases](../../releases/latest)
2. Doble clic → acepta el diálogo UAC
3. Primera vez: establece tu contraseña de acceso y guarda la clave de recuperación
4. Ve a **// REGLAS → Por Defecto** para aplicar las reglas de seguridad recomendadas

---

## Advertencia

> Esta herramienta modifica las reglas del Firewall de Windows.
> Úsala únicamente en equipos de tu propiedad o con autorización explícita.
> El autor no se responsabiliza del uso indebido.

---

## Tecnologías

- Python 3.12 + PyQt5
- pyqtgraph — gráficas en tiempo real
- psutil — monitoreo de procesos y red
- netsh advfirewall — gestión del Firewall de Windows
- Raw TCP sockets — inspección de flags TCP

---

## Licencia

MIT — ver [LICENSE](LICENSE)

Libre para uso personal, educativo y comercial.
