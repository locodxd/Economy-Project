"""
Launcher principal para iniciar el bot o la calculadora de ganancias
"""

import os
import sys

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
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
║         SISTEMA DE ECONOMÍA DISCORD BOT                   ║
║                                                            ║
║     Bot de economía con sistema JSON local                ║
║     Creado para servidores de Discord                     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """)

def main():
    while True:
        print_banner()
        
        print(f"{Colors.BOLD}OPCIONES:{Colors.ENDC}\n")
        print(f"{Colors.GREEN}1.{Colors.ENDC} Iniciar Discord Bot")
        print(f"{Colors.GREEN}2.{Colors.ENDC} Calculadora de Ganancias (CMD)")
        print(f"{Colors.GREEN}3.{Colors.ENDC} Configuración del Bot")
        print(f"{Colors.GREEN}4.{Colors.ENDC} Salir\n")
        
        choice = input(f"{Colors.CYAN}Elige una opción (1-4): {Colors.ENDC}")
        
        if choice == '1':
            print(f"\n{Colors.YELLOW}Iniciando Discord Bot...{Colors.ENDC}\n")
            print(f"{Colors.CYAN}Asegúrate de tener configurado el bot{Colors.ENDC}")
            print(f"{Colors.CYAN}Presiona Ctrl+C para detener el bot{Colors.ENDC}\n")
            input(f"Presiona ENTER para continuar...")
            os.system('python src/bot/main.py')
        
        elif choice == '2':
            print(f"\n{Colors.YELLOW}Iniciando Calculadora de Ganancias...{Colors.ENDC}\n")
            os.system('python src/utils/earnings_calculator.py')
        
        elif choice == '3':
            print(f"\n{Colors.YELLOW}Iniciando Configurador...{Colors.ENDC}\n")
            os.system('python configurator.py')
        
        elif choice == '4':
            clear_screen()
            print(f"\n{Colors.GREEN}Hasta luego!{Colors.ENDC}\n")
            break
        
        else:
            print(f"\n{Colors.RED}Opción inválida. Por favor elige 1-4{Colors.ENDC}")
            input(f"{Colors.YELLOW}Presiona ENTER para continuar...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Colors.YELLOW}Saliendo...{Colors.ENDC}\n")
        sys.exit(0)