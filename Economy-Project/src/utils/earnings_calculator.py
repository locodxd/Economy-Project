"""
calcular ganancias esto todavia se puede mejorar pero bueno, es algo basico 
"""

import time
import os

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

def print_header():
    print(f"""
{Colors.CYAN}--- CUANTA PLATA VAS A GANAR ---
{Colors.GREEN}Calculadora rapida
{Colors.CYAN}--------------------------------{Colors.ENDC}
    """)

def calculate_earnings():
    clear_screen()
    print_header()
    
    print(f"{Colors.YELLOW} Ingresa tus datos de actividad porfa:{Colors.ENDC}\n")
    
    try:
        messages_per_hour = int(input(f"{Colors.GREEN}¿Cuántos mensajes envías por hora? (promedio): {Colors.ENDC}"))
        
        hours_per_day = float(input(f"{Colors.GREEN} ¿Cuántas horas estás activo al día?: {Colors.ENDC}"))
        
        days_per_week = int(input(f"{Colors.GREEN}📅 ¿Cuántos días a la semana?: {Colors.ENDC}"))
        
        # Configuración basica 
        earning_per_message = 5  
        earning_cooldown = 60  
        
        messages_per_hour_with_cooldown = min(messages_per_hour, 60)  
        earnings_per_hour = messages_per_hour_with_cooldown * earning_per_message
        
        daily_earnings = earnings_per_hour * hours_per_day
        weekly_earnings = daily_earnings * days_per_week
        monthly_earnings = weekly_earnings * 4
        
        daily_bonus = 1000
        daily_with_streak = daily_bonus + (100 * 7)  # Asumiendo rachita de 7 días xd
        weekly_bonus = daily_with_streak * 7
        
    
        work_per_day = (24 / 1) * hours_per_day  
        work_earnings = work_per_day * 450  
        work_daily = work_earnings
        work_weekly = work_daily * days_per_week
        
        total_daily = daily_earnings + daily_with_streak + work_daily
        total_weekly = weekly_earnings + weekly_bonus + work_weekly
        total_monthly = total_weekly * 4
        
        clear_screen()
        print_header()
        
        print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}\n")
        print(f"{Colors.YELLOW} RESULTADOS DE TU ACTIVIDAD:{Colors.ENDC}\n")
        
        print(f"{Colors.GREEN} GANANCIAS POR MENSAJES:{Colors.ENDC}")
        print(f"   └─ Por hora: ${earnings_per_hour:,}")
        print(f"   └─ Por día: ${daily_earnings:,}")
        print(f"   └─ Por semana: ${weekly_earnings:,}")
        print(f"   └─ Por mes: ${monthly_earnings:,}\n")
        
        print(f"{Colors.BLUE} BONOS DAILY:{Colors.ENDC}")
        print(f"   └─ Daily básico: ${daily_bonus:,}")
        print(f"   └─ Con racha (7 días): ${daily_with_streak:,}")
        print(f"   └─ Semanal: ${weekly_bonus:,}\n")
        
        print(f"{Colors.CYAN} GANANCIAS POR WORK:{Colors.ENDC}")
        print(f"   └─ Por día: ${work_daily:,}")
        print(f"   └─ Por semana: ${work_weekly:,}\n")
        
        print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}\n")
        print(f"{Colors.BOLD}{Colors.GREEN} TOTALES:{Colors.ENDC}")
        print(f"   └─ Por día: ${total_daily:,}")
        print(f"   └─ Por semana: ${total_weekly:,}")
        print(f"   └─ Por mes: ${total_monthly:,}")
        print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}\n")
        
        print(f"{Colors.YELLOW} Tips para maximizar ganancias:{Colors.ENDC}")
        print(f"   • Mantén tu racha de daily activa (+100 por día)")
        print(f"   • Usa .work cada hora")
        print(f"   • Envía mensajes constantemente (1 por minuto para ganar)")
        print(f"   • Participa en el casino para multiplicar tus ganancias\n")
        
    except ValueError:
        print(f"\n{Colors.RED} Error: Ingresa solo números válidos{Colors.ENDC}")
        time.sleep(2)
        return
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW} Saliendo...{Colors.ENDC}")
        time.sleep(1)
        return

def show_menu():
    while True:
        clear_screen()
        print_header()
        
        print(f"{Colors.BOLD}OPCIONES:{Colors.ENDC}\n")
        print(f"{Colors.GREEN}1.{Colors.ENDC}  Calcular ganancias por tiempo")
        print(f"{Colors.GREEN}2.{Colors.ENDC}  Ver estadísticas de comandos")
        print(f"{Colors.GREEN}3.{Colors.ENDC}  Tips y guía")
        print(f"{Colors.GREEN}4.{Colors.ENDC}  Salir\n")
        
        choice = input(f"{Colors.CYAN}Elige una opción (1-4): {Colors.ENDC}")
        
        if choice == "1":
            calculate_earnings()
            input(f"\n{Colors.YELLOW}Presiona ENTER para continuar...{Colors.ENDC}")
        
        elif choice == "2":
            show_command_stats()
            input(f"\n{Colors.YELLOW}Presiona ENTER para continuar...{Colors.ENDC}")
        
        elif choice == "3":
            show_tips()
            input(f"\n{Colors.YELLOW}Presiona ENTER para continuar...{Colors.ENDC}")
        
        elif choice == "4":
            clear_screen()
            print(f"\n{Colors.GREEN} ¡Gracias por usar la calculadora! de verdad me apoyas hasta pronto{Colors.ENDC}\n")
            time.sleep(1)
            break
        
        else:
            print(f"\n{Colors.RED} Opción inválida{Colors.ENDC}")
            time.sleep(1)

def show_command_stats():
    clear_screen()
    print_header()
    
    print(f"{Colors.BOLD}{Colors.CYAN} ESTADÍSTICAS DE COMANDOS{Colors.ENDC}\n")
    
    commands = [
        {"name": ".daily", "cooldown": "24 horas", "ganancia": "1,000-1,700", "por_semana": "7,000-11,900"},
        {"name": ".work", "cooldown": "1 hora", "ganancia": "200-800", "por_semana": "33,600-134,400"},
        {"name": ".beg", "cooldown": "5 minutos", "ganancia": "5-100", "por_semana": "14,400-288,000"},
        {"name": ".coinflip", "cooldown": "30 segundos", "ganancia": "Variable", "por_semana": "Variable"},
        {"name": "Mensajes", "cooldown": "1 minuto", "ganancia": "5", "por_semana": "50,400"},
    ]
    
    for cmd in commands:
        print(f"{Colors.GREEN}{cmd['name']}{Colors.ENDC}")
        print(f"   └─ Cooldown: {cmd['cooldown']}")
        print(f"   └─ Ganancia: ${cmd['ganancia']}")
        print(f"   └─ Potencial semanal: ${cmd['por_semana']}\n")

def show_tips():
    """Muestra tips basicos y guía, favor no tocar o rompe algo xd"""
    clear_screen()
    print_header()
    
    print(f"{Colors.BOLD}{Colors.CYAN} TIPS Y GUÍA{Colors.ENDC}\n")
    
    tips = [
        (" Daily Streak", "Reclama tu .daily todos los días para mantener tu racha y ganar bonos"),
        (" Work Regular", "Usa .work cada hora para maximizar ganancias"),
        (" Mensajes", "Envía al menos 1 mensaje por minuto para ganar 5 monedas"),
        (" Bank Security", "Deposita tu dinero en el banco para mantenerlo seguro"),
        (" Casino Smart", "No apuestes todo tu dinero, juega de forma inteligente"),
        (" Transferencias", "Recuerda que las transferencias tienen un impuesto del 2%"),
        (" Tienda", "Revisa la tienda regularmente para ver nuevos items"),
        (" Leaderboard", "Compite por estar en el top del leaderboard"),
    ]
    
    for i, (title, desc) in enumerate(tips, 1):
        print(f"{Colors.GREEN}{i}. {title}{Colors.ENDC}")
        print(f"   └─ {desc}\n")

if __name__ == "__main__":
    try:
        show_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW} Saliendo...{Colors.ENDC}")
        time.sleep(1)
