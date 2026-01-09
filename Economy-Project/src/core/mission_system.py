import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Mission:
    """Clase de misión"""
    id: str
    name: str
    description: str
    difficulty: str  # "easy", "medium", "hard", "extreme"
    objectives: List[Dict]  # [{"type": "kill", "target": "goblin", "count": 5}]
    rewards: Dict  # {"coins": 500, "xp": 100, "items": {"wood": 10}}
    duration: int  # segundos
    cooldown: int = 3600
    
    def __post_init__(self):
        self.current_progress = {obj["type"]: 0 for obj in self.objectives}
        self.completed = False
        self.active = False
    
    def update_progress(self, obj_type: str, increment: int = 1):
        """Actualiza progreso de objetivo"""
        if obj_type in self.current_progress:
            self.current_progress[obj_type] += increment
    
    def check_completion(self) -> bool:
        """Verifica si está completada"""
        for obj in self.objectives:
            if self.current_progress.get(obj["type"], 0) < obj["count"]:
                return False
        self.completed = True
        return True
    
    def get_progress_text(self) -> List[str]:
        """Retorna texto de progreso"""
        lines = []
        for obj in self.objectives:
            current = self.current_progress.get(obj["type"], 0)
            total = obj["count"]
            lines.append(f"• {obj.get('description', obj['type'])}: {current}/{total}")
        return lines


class MissionRegistry:
    """Registro de misiones disponibles"""
    
    @staticmethod
    def get_all_missions() -> List[Mission]:
        """Retorna todas las misiones disponibles"""
        return [
            # MISIONES SUPER FACILES
            Mission(
                id="gather_wood",
                name="Recolector de Madera",
                description="Recolecta madera en el bosque",
                difficulty="easy",
                objectives=[
                    {"type": "collect_wood", "count": 10, "description": "Recolectar madera"}
                ],
                rewards={"coins": 200, "xp": 50, "items": {"wood": 5}},
                duration=300,
                cooldown=1800
            ),
            Mission(
                id="goblin_slayer",
                name="Cazador de Goblins",
                description="Elimina goblins en las cuevas",
                difficulty="easy",
                objectives=[
                    {"type": "kill_goblin", "count": 5, "description": "Eliminar goblins"}
                ],
                rewards={"coins": 300, "xp": 75, "items": {"gold_ore": 2}},
                duration=600,
                cooldown=3600
            ),
            Mission(
                id="fishing_contest",
                name="Concurso de Pesca",
                description="Pesca la mayor cantidad de peces",
                difficulty="easy",
                objectives=[
                    {"type": "fish", "count": 15, "description": "Pescar peces"}
                ],
                rewards={"coins": 250, "xp": 60},
                duration=400,
                cooldown=2400
            ),
            
            # MISIONES MEDIAS
            Mission(
                id="bandit_camp",
                name="Campamento Bandido",
                description="Elimina el campamento de bandidos",
                difficulty="medium",
                objectives=[
                    {"type": "kill_bandit", "count": 8, "description": "Eliminar bandidos"},
                    {"type": "destroy_tent", "count": 3, "description": "Destruir tiendas"}
                ],
                rewards={"coins": 800, "xp": 200, "items": {"iron_ore": 5, "gold_ore": 3}},
                duration=900,
                cooldown=7200
            ),
            Mission(
                id="rescue_merchant",
                name="Rescate del Mercader",
                description="Rescata al mercader secuestrado",
                difficulty="medium",
                objectives=[
                    {"type": "find_merchant", "count": 1, "description": "Encontrar al mercader"},
                    {"type": "defeat_captors", "count": 6, "description": "Derrotar captores"}
                ],
                rewards={"coins": 1200, "xp": 300, "items": {"health_potion": 3}},
                duration=1200,
                cooldown=10800
            ),
            Mission(
                id="ancient_artifact",
                name="Artefacto Antiguo",
                description="Encuentra el artefacto en las ruinas",
                difficulty="medium",
                objectives=[
                    {"type": "explore_ruins", "count": 1, "description": "Explorar ruinas"},
                    {"type": "solve_puzzle", "count": 3, "description": "Resolver acertijos"},
                    {"type": "collect_artifact", "count": 1, "description": "Obtener artefacto"}
                ],
                rewards={"coins": 1500, "xp": 400, "gems": 5},
                duration=1800,
                cooldown=14400
            ),
            
            # MISIONES DIFÍCILES
            Mission(
                id="dragon_nest",
                name="Nido del Dragón",
                description="Roba un huevo del nido del dragón",
                difficulty="hard",
                objectives=[
                    {"type": "reach_nest", "count": 1, "description": "Llegar al nido"},
                    {"type": "defeat_guardians", "count": 10, "description": "Derrotar guardianes"},
                    {"type": "steal_egg", "count": 1, "description": "Robar huevo"}
                ],
                rewards={"coins": 3000, "xp": 800, "gems": 15, "items": {"dragon_egg": 1}},
                duration=2400,
                cooldown=21600
            ),
            Mission(
                id="undead_crypt",
                name="Cripta de No-Muertos",
                description="Limpia la cripta de zombies y esqueletos",
                difficulty="hard",
                objectives=[
                    {"type": "kill_zombie", "count": 15, "description": "Eliminar zombies"},
                    {"type": "kill_skeleton", "count": 10, "description": "Eliminar esqueletos"},
                    {"type": "defeat_necromancer", "count": 1, "description": "Derrotar nigromante"}
                ],
                rewards={"coins": 4000, "xp": 1000, "gems": 20, "items": {"steel_sword": 1}},
                duration=3000,
                cooldown=28800
            ),
            
            # MISIONES EXTREMAS
            Mission(
                id="demon_portal",
                name="Portal Demoníaco",
                description="Cierra el portal antes de la invasión",
                difficulty="extreme",
                objectives=[
                    {"type": "kill_demon", "count": 25, "description": "Eliminar demonios"},
                    {"type": "destroy_portal", "count": 3, "description": "Destruir portales"},
                    {"type": "defeat_demon_lord", "count": 1, "description": "Derrotar Señor Demonio"}
                ],
                rewards={"coins": 10000, "xp": 3000, "gems": 50, "items": {"legendary_weapon": 1}},
                duration=3600,
                cooldown=86400
            ),
            Mission(
                id="titan_awakening",
                name="Despertar del Titán",
                description="Derrota al antiguo Titán antes de que despierte",
                difficulty="extreme",
                objectives=[
                    {"type": "gather_seals", "count": 4, "description": "Reunir sellos antiguos"},
                    {"type": "weaken_titan", "count": 1, "description": "Debilitar al Titán"},
                    {"type": "final_strike", "count": 1, "description": "Golpe final"}
                ],
                rewards={"coins": 20000, "xp": 5000, "gems": 100, "items": {"titan_armor": 1}},
                duration=4800,
                cooldown=172800
            )
        ]
    
    @staticmethod
    def get_mission_by_id(mission_id: str) -> Optional[Mission]:
        """Obtiene misión por ID"""
        missions = MissionRegistry.get_all_missions()
        for mission in missions:
            if mission.id == mission_id:
                return mission
        return None
    
    @staticmethod
    def get_missions_by_difficulty(difficulty: str) -> List[Mission]:
        """Filtra misiones por dificultad"""
        return [m for m in MissionRegistry.get_all_missions() if m.difficulty == difficulty]


class MissionManager:
    """Gestor de misiones activas del jugador"""
    
    def __init__(self):
        self.active_mission: Optional[Mission] = None
        self.completed_missions: List[str] = []
        self.mission_cooldowns: Dict[str, float] = {}
    
    def can_start_mission(self, mission_id: str) -> Tuple[bool, str]:
        """Verifica si se puede iniciar misión"""
        if self.active_mission:
            return False, "Ya tienes una misión activa"
        
        import time
        if mission_id in self.mission_cooldowns:
            remaining = self.mission_cooldowns[mission_id] - time.time()
            if remaining > 0:
                mins = int(remaining / 60)
                return False, f"En cooldown. Espera {mins} minutos"
        
        return True, "OK"
    
    def start_mission(self, mission_id: str) -> Tuple[bool, str]:
        """Inicia una misión"""
        can_start, msg = self.can_start_mission(mission_id)
        if not can_start:
            return False, msg
        
        mission = MissionRegistry.get_mission_by_id(mission_id)
        if not mission:
            return False, "Misión no encontrada"
        
        self.active_mission = mission
        self.active_mission.active = True
        return True, f"¡Misión '{mission.name}' iniciada!"
    
    def update_mission(self, obj_type: str, increment: int = 1):
        """Actualiza progreso de misión activa"""
        if self.active_mission:
            self.active_mission.update_progress(obj_type, increment)
    
    def check_mission_completion(self) -> Tuple[bool, Optional[Dict]]:
        """Verifica si misión está completa y retorna recompensas"""
        if not self.active_mission:
            return False, None
        
        if self.active_mission.check_completion():
            rewards = self.active_mission.rewards
            mission_id = self.active_mission.id
            
            if mission_id not in self.completed_missions:
                self.completed_missions.append(mission_id)
            
            import time
            self.mission_cooldowns[mission_id] = time.time() + self.active_mission.cooldown
            
            self.active_mission = None
            
            return True, rewards
        
        return False, None
    
    def cancel_mission(self):
        """Cancela misión activa"""
        self.active_mission = None
    
    def get_available_missions(self) -> List[Mission]:
        """Retorna misiones disponibles (no en cooldown)"""
        import time
        all_missions = MissionRegistry.get_all_missions()
        available = []
        
        for mission in all_missions:
            if mission.id in self.mission_cooldowns:
                if time.time() < self.mission_cooldowns[mission.id]:
                    continue
            available.append(mission)
        
        return available
