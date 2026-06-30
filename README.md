# Enawall

**Gestor de Firewall de Windows con interfaz gráfica**

Herramienta de seguridad para Windows que permite gestionar el Firewall de Windows, monitorear tráfico de red en tiempo real, analizar paquetes TCP/UDP y auditar todas las acciones del sistema.

---

## Descarga

Descarga el ejecutable desde la sección [**Releases**](../../releases/latest) — no requiere instalación.

---

## Módulos

| Pestaña | Descripción |
|---------|-------------|
| **// MANDO** | Cuadro de mando central: puntuación de seguridad NIST/CIS, métricas en tiempo real, acciones rápidas y feed de eventos |
| **// DASHBOARD** | Gráficas de tráfico TX/RX en tiempo real, top procesos con red activa, estado de interfaces |
| **// TRAFICO** | Ancho de banda desglosado por proceso |
| **// ALERTAS** | Define umbrales en KB/s o MB/s — notificación emergente al superarlos |
| **// REGLAS** | Gestión completa del Firewall de Windows: añadir por puerto o por programa, eliminar, exportar, limpiar duplicados, restablecer |
| **// SCANNER** | Escáner de puertos TCP con rango configurable |
| **// TCP** | Conexiones TCP/UDP en vivo con log automático |
| **// FLAGS** | Detecta y bloquea ataques por flags TCP: SYN Flood, Xmas Scan, NULL Scan, FIN Scan, RST Flood |
| **// SNIFFER** | Captura de paquetes raw, detector ARP spoof (MITM), monitor DNS, cabeceras binarias por octetos |
| **// RED** | IPs locales, gateway, interfaces y configuración completa de red |
| **// AUDIT** | Log de auditoría cronológico con backups automáticos antes de cada operación destructiva |

---

## Seguridad

- Contraseña de acceso con hash SHA-256 (nunca en texto plano)
- Clave de recuperación para resetear contraseña olvidada
- Log de auditoría en `%APPDATA%\FirewallManager\audit.log`
- Backup automático de reglas antes de resets o borrados masivos
- Una sola instancia activa (mutex global)
- Requiere y solicita privilegios de administrador automáticamente (UAC)

---

## Buenas prácticas integradas (NIST / CIS)

Indicadores visuales con puntuación 0–100:

- Bloqueo de puertos peligrosos: RDP (3389), SMB (445), Telnet (23), FTP (21), NetBIOS (139), WinRM (5985), VNC (5900)
- Política inbound por defecto: BLOCK
- Sin reglas ALLOW con IP origen "Any"
- Logging del firewall activo

---

## Requisitos

- Windows 10 / 11 (64 bits)
- Sin instalación — ejecutable único `.exe`
- Privilegios de administrador (se solicitan automáticamente via UAC)

---

## Uso

1. Descarga `Enawall.exe` desde [Releases](../../releases/latest)
2. Doble clic → acepta el diálogo UAC
3. Primera vez: establece tu contraseña y guarda la clave de recuperación
4. Ve a **// REGLAS → Por Defecto** para aplicar las reglas de seguridad recomendadas

---

## Advertencia

> Esta herramienta modifica las reglas del Firewall de Windows.
> Úsala únicamente en equipos de tu propiedad o con autorización explícita.
> El autor no se responsabiliza del uso indebido.

---

## Licencia

Apache 2.0 — ver [LICENSE](LICENSE)

Libre para uso personal, educativo y comercial. Incluye protección de patentes.
