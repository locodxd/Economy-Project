"""
pa arrancar el bot mas facil xd
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
{Colors.CYAN}--- BOT DE ECONOMIA (lo hice yo solo) ---
{Colors.GREEN}=========================================
{Colors.YELLOW}   No le toques nada si no sabes xd
{Colors.GREEN}========================================={Colors.ENDC}
    """)

def main():
    while True:
        print_banner()
        
        print(f"{Colors.BOLD}Dime q quieres hacer:{Colors.ENDC}\n")
        print(f"{Colors.GREEN}1.{Colors.ENDC} Prender el bot")
        print(f"{Colors.GREEN}2.{Colors.ENDC} Calculadora de plata")
        print(f"{Colors.GREEN}3.{Colors.ENDC} Configurar (importante)")
        print(f"{Colors.GREEN}4.{Colors.ENDC} Cerrar esta vaina\n")
        
        choice = input(f"{Colors.CYAN}pon el numero (1-4): {Colors.ENDC}")
        
        if choice == '1':
            print(f"\n{Colors.YELLOW}prendiendo... ojala no pete{Colors.ENDC}\n")
            input(f"dale al ENTER para seguir...")
            os.system('python src/bot/main.py')
        
        elif choice == '2':
            print(f"\n{Colors.YELLOW}abriendo la calculadora...{Colors.ENDC}\n")
            os.system('python src/utils/earnings_calculator.py')
        
        elif choice == '3':
            print(f"\n{Colors.YELLOW}abriendo el configurador q me costo un huevo hacer...{Colors.ENDC}\n")
            os.system('python configurator.py')
        
        elif choice == '4':
            clear_screen()
            print(f"\n{Colors.GREEN}Chaooo!{Colors.ENDC}\n")
            break
        
        else:
            print(f"\n{Colors.RED}nqv, pon del 1 al 4 fiera{Colors.ENDC}")
            input(f"{Colors.YELLOW}dale al ENTER para reintentar...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Colors.YELLOW}Saliendo...{Colors.ENDC}\n")
        sys.exit(0)