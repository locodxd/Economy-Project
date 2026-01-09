# Sistema de Economía Discord Bot

Bot de economía completo para Discord con almacenamiento JSON local y sistema de configuración avanzada.

## Características

### Discord Bot
- **Prefijo de comandos:** `.` (punto)
- Sistema de economía completo con wallet y bank
- Almacenamiento JSON local (no requiere base de datos)
- Ganancias automáticas por mensajes
- Sistema de daily con rachas
- Comandos de trabajo y casino
- Transferencias entre usuarios
- Tienda personalizable por servidor

### Comandos Administrativos (Slash Commands)
- `/aeco_set` - Establecer el dinero de un usuario
- `/aeco_reset` - Resetear completamente a un usuario
- `/aeco_add` - Añadir dinero a un usuario
- `/aeco_remove` - Quitar dinero a un usuario
- `/aeco_tienda` - Añadir items a la tienda del servidor
- `/aeco_info` - Ver información detallada de un usuario

### Configuración Avanzada
- Sistema de configuración interactivo con interfaz elegante
- Control de servidores autorizados
- Restricción de canales de comandos por servidor
- Soporte para Tenor API (GIFs)
- Configuración de roles y permisos

## Instalación

### 1. Requisitos
- Python 
- pip (gestor de paquetes de Python)

### 2. Clonar el repositorio
```bash
git clone https://github.com/locodxd/Economy-Project.git
cd Economy-Project/Economy-Project
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar el bot
```bash
python launcher.py
```

Selecciona la opción **3. Configuración del Bot** y sigue las instrucciones:

1. **Token de Discord**: Tu bot token de Discord Developer Portal
2. **Token de Tenor** (opcional): Para efectos visuales con GIFs
3. **Owner Role ID**: ID del rol de propietario
4. **Admin User IDs**: IDs de usuarios administradores
5. **Allowed Server IDs**: IDs de servidores donde el bot puede operar
6. **Command Channels** (opcional): Canales específicos para comandos

#### Obtener Token de Discord:
1. Ve a https://discord.com/developers/applications
2. Crea una nueva aplicación o selecciona una existente
3. Ve a la sección "Bot"
4. Copia el token

#### Obtener Tenor API Key (opcional):
1. Ve a https://tenor.com/developer/dashboard
2. Crea una cuenta o inicia sesión
3. Crea una nueva aplicación
4. Copia la API Key

### 5. Ejecutar el bot
```bash
python launcher.py
```

Selecciona la opción 1 para iniciar el bot.

## Comandos del Bot

### Comandos Básicos
```
.help              - Muestra todos los comandos
.help <comando>    - Información detallada de un comando
.daily             - Recompensa diaria (24h cooldown)
.work              - Trabaja para ganar dinero (1h cooldown)
.balance           - Ver tu dinero
.beg               - Mendiga dinero (5min cooldown)
.deposit <amount>  - Depositar en el banco
.withdraw <amount> - Retirar del banco
.transfer @user    - Transferir dinero
```

### Casino
```
.coinflip <amount> <cara/cruz> - Cara o cruz
.dice <amount>                  - Lanza los dados
.slots <amount>                 - Máquina tragamonedas
.blackjack <amount>             - Jugar blackjack
```

### Tienda
```
.shop              - Ver la tienda del servidor
.buy <item>        - Comprar un item
.inventory         - Ver tu inventario
```

## Control de Acceso

### Servidores Autorizados
Si configuras servidores permitidos, el bot:
- Solo funcionará en esos servidores
- Se saldrá automáticamente de servidores no autorizados
- Enviará un mensaje explicando el motivo

### Canales de Comandos
Si configuras canales específicos:
- Los comandos solo funcionarán en esos canales
- Los usuarios recibirán un aviso si intentan usar comandos en otros canales

## Estructura de Archivos

```
Economy-Project/
├── launcher.py                      # Launcher principal
├── configurator.py                  # Configurador interactivo
├── requirements.txt                 # Dependencias
├── .env                            # Token del bot (generado)
├── config/
│   └── bot_config.json             # Configuración del bot
├── database/                       # Base de datos JSON
│   ├── users.json                  # Datos de usuarios
│   ├── shop_items.json             # Items de la tienda
│   └── transactions.json           # Registro de transacciones
├── src/
│   ├── bot/
│   │   ├── main.py                 # Bot principal
│   │   ├── config.py               # Configuración
│   │   └── cogs/                   # Comandos del bot
│   ├── core/
│   │   └── database.py             # Sistema de base de datos JSON
│   └── utils/
│       └── earnings_calculator.py  # Calculadora de ganancias
└── modules/                        # Módulos adicionales (referencia)
```

## Configuración

### Editar Recompensas
Archivo: `src/bot/config.py`

```python
ECONOMY_CONFIG = {
    "daily_reward": 1000,
    "earning_per_message": 5,
    "earning_cooldown": 60,
}
```

## Solución de Problemas

### El bot no inicia
- Verifica que tu token esté correcto ejecutando `configurator.py`
- Revisa los logs en `logs/bot.log`

### Los comandos no funcionan
- Verifica que el bot tenga permisos en tu servidor
- Asegúrate de usar el prefijo correcto (`.`)
- Si configuraste canales específicos, usa los comandos solo ahí

### El bot se sale del servidor
- Verifica que el servidor esté en la lista de servidores permitidos
- Ejecuta `configurator.py` para añadir el servidor
###
Sientete libre de modificar todo lo que quieras, total es para practicar!
## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

---

**Desarrollado para fomentar la actividad y participación en servidores de Discord.**

