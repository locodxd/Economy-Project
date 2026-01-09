"""
Advanced Economy Bot - Ez-Configuration
Sistema de configuración interactivo
"""

import os
import json
from pathlib import Path

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(f"""
{Colors.CYAN}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              {Colors.BOLD}ADVANCED ECONOMY{Colors.ENDC}{Colors.CYAN}                               ║
║              {Colors.BOLD}Ez-Configuration{Colors.ENDC}{Colors.CYAN}                               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """)

def get_input(prompt, optional=False, multiline=False):
    """Obtiene input del usuario"""
    if optional:
        prompt += f" {Colors.YELLOW}(opcional, presiona Enter para omitir){Colors.ENDC}"
    
    if multiline:
        print(f"{Colors.GREEN}{prompt}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Ingresa IDs separados por comas (ej: 123,456,789):{Colors.ENDC}")
    else:
        print(f"{Colors.GREEN}{prompt}{Colors.ENDC}")
    
    value = input("> ").strip()
    
    if multiline and value:
        return [item.strip() for item in value.split(',')]
    
    return value if value else None

def show_tenor_guide():
    """Muestra guía para obtener API key de Tenor"""
    print(f"\n{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.BOLD}Como obtener API Key de Tenor:{Colors.ENDC}")
    print(f"1. Ve a: https://tenor.com/developer/dashboard")
    print(f"2. Inicia sesión o crea una cuenta")
    print(f"3. Crea una nueva aplicación")
    print(f"4. Copia la 'API Key'")
    print(f"{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}\n")

def configure_bot():
    """Proceso de configuración principal"""
    print_banner()
    
    print(f"{Colors.YELLOW}Bienvenido al configurador del bot de economía.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Responde las siguientes preguntas para configurar tu bot.{Colors.ENDC}\n")
    
    # Advertencia importante sobre intents
    print(f"{Colors.RED}╔════════════════════════════════════════════════════════════╗")
    print(f"║                  {Colors.BOLD}⚠️  IMPORTANTE ⚠️{Colors.ENDC}{Colors.RED}                          ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.ENDC}")
    print(f"{Colors.YELLOW}ANTES de iniciar el bot, debes habilitar los Privileged Intents{Colors.ENDC}")
    print(f"{Colors.YELLOW}en el portal de desarrolladores de Discord:{Colors.ENDC}\n")
    print(f"  {Colors.CYAN}1. Ve a: {Colors.BOLD}https://discord.com/developers/applications/{Colors.ENDC}")
    print(f"  {Colors.CYAN}2. Selecciona tu aplicación (bot){Colors.ENDC}")
    print(f"  {Colors.CYAN}3. Ve a la sección 'Bot' en el menú lateral{Colors.ENDC}")
    print(f"  {Colors.CYAN}4. Baja hasta 'Privileged Gateway Intents'{Colors.ENDC}")
    print(f"  {Colors.CYAN}5. Activa estas 3 opciones:{Colors.ENDC}")
    print(f"     {Colors.GREEN}✓ PRESENCE INTENT{Colors.ENDC}")
    print(f"     {Colors.GREEN}✓ SERVER MEMBERS INTENT{Colors.ENDC}")
    print(f"     {Colors.GREEN}✓ MESSAGE CONTENT INTENT {Colors.BOLD}(OBLIGATORIO){Colors.ENDC}")
    print(f"  {Colors.CYAN}6. Guarda los cambios{Colors.ENDC}\n")
    print(f"{Colors.RED}Sin estos permisos, el bot NO funcionará.{Colors.ENDC}\n")
    
    input(f"{Colors.YELLOW}Presiona Enter cuando hayas habilitado los intents...{Colors.ENDC}")
    clear_screen()
    print_banner()
    
    config = {}
    
    # Token de Discord
    print(f"\n{Colors.CYAN}═══ CONFIGURACIÓN BÁSICA ═══{Colors.ENDC}\n")
    config['discord_token'] = get_input("1. Token de Discord Bot")
    
    if not config['discord_token']:
        print(f"\n{Colors.RED}Error: El token de Discord es obligatorio{Colors.ENDC}")
        input("\nPresiona Enter para salir...")
        return None
    
    # Token de Tenor
    show_guide = input(f"\n{Colors.YELLOW}¿Ver guía para obtener Tenor API Key? (s/n): {Colors.ENDC}").lower()
    if show_guide == 's':
        show_tenor_guide()
    
    config['tenor_token'] = get_input("2. Token de Tenor API", optional=True)
    
    # Owner Role
    print(f"\n{Colors.CYAN}═══ ROLES Y PERMISOS ═══{Colors.ENDC}\n")
    config['owner_role'] = get_input("3. ID del Rol de Owner")
    
    # Admin User IDs
    config['admin_user_ids'] = get_input("4. IDs de usuarios administradores", multiline=True)
    
    # Servidores permitidos
    print(f"\n{Colors.CYAN}═══ CONTROL DE SERVIDORES ═══{Colors.ENDC}\n")
    print(f"{Colors.YELLOW}Si el bot se une a un servidor no autorizado, se saldrá automáticamente.{Colors.ENDC}\n")
    config['allowed_servers'] = get_input("5. IDs de servidores permitidos", multiline=True)
    
    # Canales de comandos por servidor
    print(f"\n{Colors.CYAN}═══ CANALES DE COMANDOS (OPCIONAL) ═══{Colors.ENDC}\n")
    print(f"{Colors.YELLOW}Si no configuras esto, los comandos funcionarán en cualquier canal.{Colors.ENDC}\n")
    
    configure_channels = input(f"¿Configurar canales de comandos específicos? (s/n): {Colors.ENDC}").lower()
    
    if configure_channels == 's':
        config['command_channels'] = {}
        if config['allowed_servers']:
            for server_id in config['allowed_servers']:
                print(f"\n{Colors.GREEN}Servidor ID: {server_id}{Colors.ENDC}")
                channels = get_input(f"  IDs de canales de comandos para este servidor", optional=True, multiline=True)
                if channels:
                    config['command_channels'][server_id] = channels
    
    # Guardar configuración
    return config

def save_config(config):
    """Guarda la configuración en archivos"""
    
    # Crear .env
    env_content = f"DISCORD_TOKEN={config['discord_token']}\n"
    if config.get('tenor_token'):
        env_content += f"TENOR_API_KEY={config['tenor_token']}\n"
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    # Crear bot_config.json
    bot_config = {
        "owner_role": config.get('owner_role'),
        "admin_user_ids": config.get('admin_user_ids', []),
        "allowed_servers": config.get('allowed_servers', []),
        "command_channels": config.get('command_channels', {})
    }
    
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / 'bot_config.json', 'w', encoding='utf-8') as f:
        json.dump(bot_config, f, indent=2)
    
    print(f"\n{Colors.GREEN}Configuración guardada exitosamente!{Colors.ENDC}")

def show_summary(config):
    """Muestra resumen de configuración"""
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗")
    print(f"║              RESUMEN DE CONFIGURACIÓN                     ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Token Discord:{Colors.ENDC} {'*' * 20}...{config['discord_token'][-10:]}")
    print(f"{Colors.BOLD}Token Tenor:{Colors.ENDC} {config.get('tenor_token', 'No configurado')[:20]}..." if config.get('tenor_token') else f"{Colors.BOLD}Token Tenor:{Colors.ENDC} No configurado")
    print(f"{Colors.BOLD}Owner Role:{Colors.ENDC} {config.get('owner_role', 'No configurado')}")
    print(f"{Colors.BOLD}Admin Users:{Colors.ENDC} {len(config.get('admin_user_ids', []))} usuario(s)")
    print(f"{Colors.BOLD}Servidores Permitidos:{Colors.ENDC} {len(config.get('allowed_servers', []))} servidor(es)")
    print(f"{Colors.BOLD}Canales Configurados:{Colors.ENDC} {len(config.get('command_channels', {}))} servidor(es)")
    
    print(f"\n{Colors.YELLOW}Archivos creados:{Colors.ENDC}")
    print(f"  - .env")
    print(f"  - config/bot_config.json")

def main():
    try:
        config = configure_bot()
        
        if not config:
            return
        
        # Confirmar
        print(f"\n{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}")
        confirm = input(f"\n{Colors.YELLOW}¿Guardar esta configuración? (s/n): {Colors.ENDC}").lower()
        
        if confirm == 's':
            save_config(config)
            show_summary(config)
            
            print(f"\n{Colors.GREEN}¡Configuración completada!{Colors.ENDC}")
            print(f"\n{Colors.CYAN}Próximos pasos:{Colors.ENDC}")
            print(f"1. Ejecuta launcher.py")
            print(f"2. Selecciona opción 1 para iniciar el bot")
            print(f"3. Usa .help en Discord para ver comandos")
        else:
            print(f"\n{Colors.RED}Configuración cancelada{Colors.ENDC}")
        
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.ENDC}")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Configuración cancelada por el usuario{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.ENDC}")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.ENDC}")

if __name__ == "__main__":
    main()
