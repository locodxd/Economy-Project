from discord.ext import commands
import random

class Jobs(commands.Cog):
    """comandos relacionados con trabajos para ganar ingresos."""

    def __init__(self, bot):
        self.bot = bot
        self.jobs = [
            {"name": "Tester de videojuegos", "min": 200, "max": 500},
            {"name": "Repartidor de pizzas", "min": 180, "max": 450},
            {"name": "Traductor freelance", "min": 250, "max": 600},
            {"name": "Limpiador de ventanas", "min": 150, "max": 400},
            {"name": "Vendedor de libros usados", "min": 170, "max": 420},
            {"name": "Profesor particular", "min": 300, "max": 700},
            {"name": "DJ en fiestas", "min": 280, "max": 650},
            {"name": "Artista callejero", "min": 190, "max": 480},
            {"name": "Técnico de computadoras", "min": 320, "max": 750},
            {"name": "Paseador de perros", "min": 140, "max": 380},
            {"name": "Bartender", "min": 220, "max": 550},
            {"name": "Operador de call center", "min": 160, "max": 400},
            {"name": "Fotógrafo de eventos", "min": 290, "max": 680},
            {"name": "Streamer por un día", "min": 200, "max": 500},
            {"name": "Guardia de seguridad", "min": 180, "max": 450},
            {"name": "Jardinero", "min": 150, "max": 390},
            {"name": "Electricista de emergencia", "min": 310, "max": 720},
            {"name": "Plomero a domicilio", "min": 300, "max": 700},
            {"name": "Chef privado", "min": 350, "max": 800},
            {"name": "FlavorTown coder", "min": 210, "max": 520},
            {"name": "Mesero en restaurante", "min": 170, "max": 430},
            {"name": "Editor de videos", "min": 270, "max": 630},
            {"name": "Diseñador gráfico", "min": 280, "max": 650},
            {"name": "Community manager", "min": 240, "max": 580},
            {"name": "Modelo freelance", "min": 260, "max": 610},
            {"name": "Mecánico de autos", "min": 290, "max": 680},
            {"name": "Entrenador personal", "min": 270, "max": 640},
            {"name": "Tatuador temporal", "min": 250, "max": 600},
            {"name": "Barbero/peluquero", "min": 200, "max": 500},
            {"name": "Vendedor ambulante", "min": 160, "max": 410},
            {"name": "Guía turístico", "min": 230, "max": 560},
            {"name": "Asistente virtual", "min": 220, "max": 540},
            {"name": "Transcriptor de audio", "min": 190, "max": 470},
            {"name": "Probador de comida", "min": 180, "max": 450},
            {"name": "Repartidor de delivery", "min": 170, "max": 430},
            {"name": "Animador de eventos", "min": 260, "max": 610},
            {"name": "Maquillador profesional", "min": 240, "max": 580},
            {"name": "Músico callejero", "min": 200, "max": 500},
            {"name": "Vendedor de autos", "min": 320, "max": 750},
            {"name": "Contador freelance", "min": 330, "max": 770},
            {"name": "Abogado consultor", "min": 380, "max": 850},
            {"name": "Médico de guardia", "min": 400, "max": 900},
            {"name": "Desarrollador web", "min": 350, "max": 820},
            {"name": "Hacker ético", "min": 370, "max": 840},
            {"name": "Arquitecto freelance", "min": 340, "max": 790},
            {"name": "Consultor empresarial", "min": 360, "max": 830},
            {"name": "Agente inmobiliario", "min": 310, "max": 730},
            {"name": "Investigador privado", "min": 300, "max": 710},
            {"name": "Ingeniero freelance", "min": 370, "max": 850},
            {"name": "Científico de datos", "min": 390, "max": 870},
        ]

    @commands.command(name="findjob", aliases=["buscarjob"])
    async def find_job(self, ctx):
        """🔍 Encuentra un trabajo para ganar dinero."""
        job = random.choice(self.jobs)
        await ctx.send(f"Has encontrado un trabajo como **{job['name']}**. Puedes ganar entre ${job['min']} y ${job['max']} por trabajo.")

    @commands.command(name="joblist", aliases=["listajobs", "trabajos"])
    async def job_list(self, ctx):
        """💼 Muestra la lista de trabajos disponibles."""
        job_list = "\n".join([f"**{job['name']}**: ${job['min']} - ${job['max']}" for job in self.jobs])
        await ctx.send(f"📋 **Trabajos Disponibles:**\n{job_list}")

async def setup(bot):
    await bot.add_cog(Jobs(bot))