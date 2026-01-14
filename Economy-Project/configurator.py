"""
config del bot para no andar editando el .env a mano que es un lio
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
{Colors.CYAN}--- CONFIG DEL BOT ---
{Colors.GREEN}No borres nada raro o se rompe xD
{Colors.CYAN}--- By locodxd ---{Colors.ENDC}
    """)

def get_input(prompt, optional=False, multiline=False):
    """gets input from user"""
    if optional:
        prompt += f" {Colors.YELLOW}(puedes saltarlo con Enter){Colors.ENDC}"
    
    if multiline:
        print(f"{Colors.GREEN}{prompt}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Pon las IDs separadas por comas (ej: 111,222):{Colors.ENDC}")
    else:
        print(f"{Colors.GREEN}{prompt}{Colors.ENDC}")
    
    value = input("> ").strip()
    
    if multiline and value:
        return [item.strip() for item in value.split(',')]
    
    return value if value else None

def show_tenor_guide():
    """guia de tenor"""
    print(f"\n{Colors.CYAN}=== Guia rapida Tenor ==={Colors.ENDC}")
    print(f"1. Ve a la web de Tenor developers")
    print(f"2. Logueate con Google o algo")
    print(f"3. Crea una app cualquiera")
    print(f"4. Copia la key y pegala aca")
    print(f"{Colors.CYAN}========================={Colors.ENDC}\n")

def configure_bot():
    """el menu de config"""
    print_banner()
    
    print(f"{Colors.YELLOW}Aca configuras todo lo del bot.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Si no sabes de donde sacar el token busca un tutorial en youtube xd{Colors.ENDC}\n")
    
    # IMPORTANTE
    print(f"{Colors.RED}!!! OJO !!!{Colors.ENDC}")
    print(f"{Colors.YELLOW}Activa los Intents en el Discord Developer Portal (la parte de 'Bot'){Colors.ENDC}")
    print(f"{Colors.YELLOW}Tienes que marcar las 3 cajitas de abajo o no va a leer los mensajes.{Colors.ENDC}\n")
    
    input(f"{Colors.YELLOW}Presiona Enter cuando lo hayas hecho...{Colors.ENDC}")
    clear_screen()
    print_banner()
    
    config = {}
    
    # Token de Discord
    print(f"\n{Colors.CYAN}--- COSAS BASICAS ---{Colors.ENDC}\n")
    config['discord_token'] = get_input("1. Token del Bot")
    
    if not config['discord_token']:
        print(f"\n{Colors.RED}Sin token no hay bot bro{Colors.ENDC}")
        input("\nEnter para salir...")
        return None
    
    # Token de Tenor
    show_guide = input(f"\n{Colors.YELLOW}¿Ver guía para obtener Tenor API Key? (s/n): {Colors.ENDC}").lower()
    if show_guide == 's':
        show_tenor_guide()
    
    config['tenor_token'] = get_input("2. Token de Tenor API", optional=True)
    
    # Preguntar si es bot publico o privado
    print(f"\n{Colors.CYAN}═══ MODO DEL BOT ═══{Colors.ENDC}\n")
    print(f"{Colors.YELLOW}Bot Publico:{Colors.ENDC} Funciona en cualquier servidor, base de datos separada por servidor")
    print(f"{Colors.YELLOW}Bot Privado:{Colors.ENDC} Solo funciona en servidores específicos, base de datos global")
    modo_publico = input(f"\n¿Tu bot es publico? (s/n): {Colors.ENDC}").lower() == 's'
    config['modo_publico'] = modo_publico
    
    # Owner Role
    print(f"\n{Colors.CYAN}═══ ROLES Y PERMISOS ═══{Colors.ENDC}\n")
    
    if modo_publico:
        print(f"{Colors.YELLOW}Modo publico: Solo necesitas IDs de usuarios admin{Colors.ENDC}\n")
        config['owner_role'] = None
        config['admin_user_ids'] = get_input("3. IDs de usuarios administradores (pueden usar comandos admin)", multiline=True)
        config['allowed_servers'] = None
    else:
        config['owner_role'] = get_input("3. ID del Rol de Owner")
        config['admin_user_ids'] = get_input("4. IDs de usuarios administradores", multiline=True)
        
        # Servidores permitidos solo en modo privado
        print(f"\n{Colors.CYAN}═══ CONTROL DE SERVIDORES ===({Colors.ENDC}\n")
        print(f"{Colors.YELLOW}Si el bot se une a un servidor no autorizado, se saldrá automáticamente.{Colors.ENDC}\n")
        config['allowed_servers'] = get_input("5. IDs de servidores permitidos", multiline=True)
    
    # Tenor keys multiples (opcional)
    print(f"\n{Colors.CYAN}═══ TENOR API AVANZADO (OPCIONAL) ===({Colors.ENDC}\n")
    print(f"{Colors.YELLOW}Puedes agregar múltiples API keys de Tenor para fallback{Colors.ENDC}")
    print(f"{Colors.YELLOW}Si una key falla, usará la siguiente automáticamente{Colors.ENDC}\n")
    extra_tenor = input(f"¿Agregar mas Tenor API keys? (s/n): {Colors.ENDC}").lower()
    
    if extra_tenor == 's':
        tenor_keys = [config['tenor_token']] if config.get('tenor_token') else []
        print(f"\n{Colors.GREEN}Ingresa keys adicionales (presiona Enter sin escribir para terminar){Colors.ENDC}")
        while True:
            extra_key = get_input(f"Tenor API Key #{len(tenor_keys) + 1}", optional=True)
            if not extra_key:
                break
            tenor_keys.append(extra_key)
        config['tenor_keys'] = tenor_keys if len(tenor_keys) > 1 else None
    else:
        config['tenor_keys'] = None
    
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
    
    # Crear .env con soporte para multiples tenor keys
    env_content = f"DISCORD_TOKEN={config['discord_token']}\n"
    
    # si hay multiple tenor keys, guardarlas todas
    if config.get('tenor_keys'):
        for i, key in enumerate(config['tenor_keys']):
            if i == 0:
                env_content += f"TENOR_API_KEY={key}\n"
            else:
                env_content += f"TENOR_API_KEY_{i}={key}\n"
    elif config.get('tenor_token'):
        env_content += f"TENOR_API_KEY={config['tenor_token']}\n"
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    # Crear bot_config.json
    # Normalizar valores para evitar guardar `null` en JSON
    bot_config = {
        "modo_publico": config.get('modo_publico', False),
        "owner_role": config.get('owner_role'),
        "admin_user_ids": config.get('admin_user_ids') or [],
        "allowed_servers": config.get('allowed_servers') or [],
        "command_channels": config.get('command_channels') or {},
        "tenor_fallback_keys": config.get('tenor_keys', []) if config.get('tenor_keys') else None
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
    
    print(f"{Colors.BOLD}Modo:{Colors.ENDC} {'Publico (multi-servidor)' if config.get('modo_publico') else 'Privado (servidores especificos)'}")
    print(f"{Colors.BOLD}Token Discord:{Colors.ENDC} {'*' * 20}...{config['discord_token'][-10:]}")
    
    if config.get('tenor_keys'):
        print(f"{Colors.BOLD}Tenor Keys:{Colors.ENDC} {len(config['tenor_keys'])} keys configuradas (con fallback)")
    elif config.get('tenor_token'):
        print(f"{Colors.BOLD}Token Tenor:{Colors.ENDC} {config.get('tenor_token')[:20]}...")
    else:
        print(f"{Colors.BOLD}Token Tenor:{Colors.ENDC} No configurado")
    
    if not config.get('modo_publico'):
        print(f"{Colors.BOLD}Owner Role:{Colors.ENDC} {config.get('owner_role', 'No configurado')}")
        print(f"{Colors.BOLD}Servidores Permitidos:{Colors.ENDC} {len(config.get('allowed_servers', []))} servidor(es)")
    
    print(f"{Colors.BOLD}Admin Users:{Colors.ENDC} {len(config.get('admin_user_ids', []))} usuario(s)")
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
