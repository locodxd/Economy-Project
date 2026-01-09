"""
Mensajes customizados para el sistema de economía del bot, puedes cambiar los mensajes aquí pero tene cuidado 
"""

import random
from typing import List

class MessageSystem:
    
    # Mensajes de error
    ERROR_MESSAGES = {
        "no_money": [
            " Oye, no tienes suficiente dinero para eso",
            " Tu billetera está más vacía que mi nevera...",
            " Necesitas más dinero para hacer eso, gil",
            " ¿Dinero? No veo dinero por aquí jajaja...",
            " Tu cuenta no tiene fondos suficientes, crack"
        ],
        "invalid_amount": [
            " Esa cantidad no tiene sentido... ¿estás bien?",
            " Número inválido. ¿Sabes contar? 🤔",
            " Pon un número válido, no es tan difícil",
            " Cantidad inválida. Intenta de nuevo, pero bien esta vez"
        ],
        "cooldown": [
            " Calma tigre, espera {} segundos",
            " Muy rápido! Espera {} segundos",
            " Dame {} segundos más, no soy una máquina... bueno, sí lo soy pero igual",
            " Cooldown activo: {} segundos. Ve a hacer algo productivo XD"
        ],
        "self_transfer": [
            " No puedes transferirte dinero a ti mismo, genio",
            " ¿Te vas a pagar a ti mismo? No funciona así",
            " Transferencias a uno mismo están prohibidas, sorry",
            " Nice try, pero no puedes hacerte rico así"
        ],
        "bot_transfer": [
            " Los bots no necesitan dinero, viven de amor",
            " ¿Darle dinero a un bot? No seas inocente",
            " Los bots trabajan gratis, no les pagues",
            " Ese bot no va a apreciar tu generosidad igual si funcionó gracias"
        ]
    }
    
    # Mensajes de éxito
    SUCCESS_MESSAGES = {
        "daily_claimed": [
            " ¡Daily reclamado! Vuelve mañana por más",
            " ¡Cha-ching! Tu daily está en tu bolsillo",
            " Daily cobrado. Gastalo sabiamente... o no",
            " Aquí está tu daily. No lo gastes todo en un lugar... como cierto creador del bot"
        ],
        "work_done": [
            " Trabajo completado! Tu jefe está orgulloso",
            " Buen trabajo! El dinero está en tu cuenta",
            " Trabajo duro paga bien. Literalmente.",
            " Misión cumplida! Cobrado y pagado"
        ],
        "transfer_success": [
            " Transferencia exitosa! Qué generoso eres",
            " Dinero enviado. Espero que lo aprecien",
            " Transfer completado. -2% de impuestos, gracias",
            " Enviado! El gobierno se quedó con el 2%"
        ],
        "deposit_success": [
            " Depositado! Tu dinero está seguro... creo",
            " En el banco! Más seguro que en tu bolsillo",
            " Guardado en el banco. No lo puedo hackear... aún",
            " Seguro en el banco, lejos de las apuestas"
        ],
        "withdraw_success": [
            " Retirado! Gastalo con responsabilidad",
            " Efectivo en mano! Hora de apostar... digo, de ahorrar",
            " Retirado del banco. Intenta no perderlo",
            " Cash out! No vayas directo al casino"
        ]
    }
    
    WIN_MESSAGES = [
        " ¡GANASTE! Eres oficialmente un genio PERO DE LA SUERTE",
        " ¡VICTORIA! La suerte está de tu lado hoy",
        " ¡JACKPOT! Sabía que eras bueno en esto comparte algo con el creador",
        " ¡INCREÍBLE! Vas camino a la riqueza",
        " ¡WOW! Deberías comprar un boleto de lotería",
        " ¡PERFECTO! La fortuna te sonríe"
    ]
    
    LOSE_MESSAGES = [
        " Perdiste... pero hey, siempre hay una próxima, exijo que apuestes más",
        " La casa siempre gana... bueno, casi siempre",
        " Mala suerte. Intenta de nuevo!",
        " No fue tu día. Mañana será mejor",
        " Perdiste, pero no pierdas la esperanza",
        " Se fue tu dinero... como mis esperanzas en ti"
    ]
    
    # Mensajes motivacionales o bueno intento de ellos
    MOTIVATIONAL_MESSAGES = [
        " Sigue así! Estás haciendo un gran trabajo",
        " Cada moneda cuenta! Sigue acumulando",
        " Meta del día: Ser más rico que ayer",
        " El éxito no viene solo, trabaja por él",
        " Hacia el infinito... y más allá de la riqueza!",
        " Recuerda: El dinero no da la felicidad, pero ayuda bastante"
    ]
    
    # Tips aleatorios
    RANDOM_TIPS = [
        " Tip: Mantén tu racha de daily para bonos extras!",
        " Tip: Usa .work cada hora para maximizar ganancias",
        " Tip: Deposita en el banco para mantener tu dinero seguro",
        " Tip: No apuestes todo en el casino, juega inteligente",
        " Tip: Las transferencias tienen un 2% de impuesto",
        " Tip: Envía mensajes regularmente para ganar dinero automático",
        " Tip: El blackjack da 2.5x si sacas 21 con 2 cartas",
        " Tip: Los dados necesitan 10+ para ganar"
    ]
    
    # Mensajes de bienvenida para nuevos usuarios esto está deshabilitado por ahora
    WELCOME_MESSAGES = [
        "¡Bienvenido al sistema de economía! ",
        "¡Hola! Tu aventura económica comienza ahora ",
        "¡Nuevo usuario detectado! Preparando tu cuenta... ",
        "¡Bienvenido a bordo! Usa .help para empezar "
    ]
    
    @staticmethod
    def get_random(category: str) -> str:
        """Obtiene un mensaje aleatorio de una categoría"""
        if category in MessageSystem.ERROR_MESSAGES:
            return random.choice(MessageSystem.ERROR_MESSAGES[category])
        elif category in MessageSystem.SUCCESS_MESSAGES:
            return random.choice(MessageSystem.SUCCESS_MESSAGES[category])
        elif category == "win":
            return random.choice(MessageSystem.WIN_MESSAGES)
        elif category == "lose":
            return random.choice(MessageSystem.LOSE_MESSAGES)
        elif category == "motivational":
            return random.choice(MessageSystem.MOTIVATIONAL_MESSAGES)
        elif category == "tip":
            return random.choice(MessageSystem.RANDOM_TIPS)
        elif category == "welcome":
            return random.choice(MessageSystem.WELCOME_MESSAGES)
        return "Mensaje no encontrado"
    
    @staticmethod
    def get_cooldown_message(seconds: float) -> str:
        msg = random.choice(MessageSystem.ERROR_MESSAGES["cooldown"])
        
        if seconds < 60:
            time_str = f"{seconds:.0f} segundos"
        elif seconds < 3600:
            minutes = seconds / 60
            time_str = f"{minutes:.1f} minutos"
        else:
            hours = seconds / 3600
            time_str = f"{hours:.1f} horas"
        
        return msg.format(time_str)
    
    @staticmethod
    def format_money(amount: int) -> str:
        if amount >= 1000000:
            return f"💎 ${amount:,}"
        elif amount >= 100000:
            return f"💰 ${amount:,}"
        elif amount >= 10000:
            return f"💵 ${amount:,}"
        elif amount >= 1000:
            return f"💸 ${amount:,}"
        else:
            return f"🪙 ${amount:,}"
    
    @staticmethod
    def get_rank_emoji(rank: int) -> str:
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        elif rank <= 10:
            return "🏅"
        else:
            return "📊"
    
    @staticmethod
    def get_level_message(level: int) -> str:
        """Mensaje al subir de nivel"""
        messages = {
            1: " Nivel 1: ¡Bienvenido novato!",
            5: " Nivel 5: Ya no eres tan novato",
            10: " Nivel 10: Estás progresando bien!",
            25: " Nivel 25: Eres un veterano!",
            50: " Nivel 50: ¡LEYENDA VIVIENTE!",
            100: " Nivel 100: ¡REY DE LA ECONOMÍA! o te giveaste???"
        }
        return messages.get(level, f"⭐ Nivel {level}: ¡Sigue así!")

# Instancia global
messages = MessageSystem()
