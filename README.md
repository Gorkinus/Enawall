# Firewall Manager v2.0

**Gestor de Firewall de Windows con interfaz gráfica — estética Matrix/Cyberpunk**

Herramienta de seguridad para Windows que permite gestionar el Firewall de Windows, monitorear tráfico de red en tiempo real, detectar ataques por flags TCP y auditar todas las acciones del sistema.

---

## Capturas de pantalla

> Interfaz en modo Matrix — fondo negro, texto verde neón

![Dashboard](Captura%20de%20pantalla%202026-06-25%20185618.png)

---

## Características

| Módulo | Descripción |
|--------|-------------|
| **Cuadro de Mando** | Estado global del sistema, métricas clave, puntuación de seguridad, acciones rápidas y feed de eventos en tiempo real |
| **Dashboard** | Gráficas de tráfico TX/RX en tiempo real, top procesos con red activa, estado de interfaces |
| **Tráfico** | Ancho de banda desglosado por proceso |
| **Alertas** | Define umbrales en KB/s o MB/s — notificación emergente cuando se supera |
| **Reglas** | Gestión completa del Firewall de Windows: añadir, eliminar, exportar, limpiar duplicados, restablecer |
| **Scanner** | Escáner de puertos TCP con rango configurable |
| **TCP** | Conexiones TCP/UDP en vivo con log automático |
| **Flags TCP** | Detecta y bloquea ataques: SYN Flood, Xmas Scan, NULL Scan, FIN Scan, RST Flood |
| **Red** | IPs locales, gateway, interfaces, ipconfig completo |
| **Audit** | Log de auditoría de todas las acciones con backups automáticos |

### Seguridad
- Contraseña de acceso con hash SHA-256 (nunca en texto plano)
- Clave de recuperación para resetear contraseña
- Log de auditoría cronológico en `%APPDATA%\FirewallManager\audit.log`
- Backup automático de reglas antes de operaciones destructivas
- Detección de instancia única (no permite múltiples ventanas)
- Requiere y solicita privilegios de administrador automáticamente (UAC)

### Buenas prácticas integradas
Indicadores visuales de cumplimiento basados en **NIST SP 800-41**, **CIS Benchmarks** y recomendaciones de la comunidad de seguridad:
- Bloqueo de puertos peligrosos: RDP (3389), SMB (445), Telnet (23), FTP (21), NetBIOS (139), WinRM (5985), VNC (5900)
- Política inbound por defecto: BLOCK
- Logging del firewall activo
- Puntuación de seguridad 0–100 calculada por peso (crítico/alto/medio)

---

## Requisitos

- **Windows 10 / 11** (64 bits)
- **Privilegios de administrador** (la app lo solicita automáticamente via UAC)
- No requiere instalación — ejecutable único `.exe`

---

## Instalación y uso

### Opción A — Ejecutable directo (recomendado)

1. Descarga `FirewallManager.exe` desde la sección [Releases](../../releases)
2. Doble clic → acepta el diálogo de UAC (necesario para gestionar el firewall)
3. En el primer arranque, establece una contraseña de acceso

### Opción B — Desde el código fuente

**Requisitos:** Python 3.10+, Windows

```bash
pip install PyQt5 psutil pyqtgraph
python firewall_v2.py
```

**Compilar el ejecutable:**

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --uac-admin --hidden-import pyqtgraph --hidden-import psutil firewall_v2.py
```

---

## Advertencia

> Esta herramienta modifica las reglas del Firewall de Windows del sistema.  
> Úsala únicamente en equipos de tu propiedad o con autorización explícita.  
> El autor no se responsabiliza del uso indebido de esta herramienta.

---

## Tecnologías

- **Python 3.12** + **PyQt5** — interfaz gráfica
- **pyqtgraph** — gráficas de tráfico en tiempo real
- **psutil** — monitoreo de procesos y red
- **netsh advfirewall** — gestión del Firewall de Windows
- **Raw TCP sockets** — inspección de flags TCP (modo admin)
- **PyInstaller** — compilación a ejecutable único

---

## Licencia

MIT License — ver [LICENSE](LICENSE)

Libre para uso personal, educativo y comercial.  
Si mejoras el proyecto, considera hacer un Pull Request.

---

## Contribuir

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Añade nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

*Desarrollado con Python + PyQt5 — interfaz inspirada en la estética cyberpunk/Matrix*
