import discord
from discord.ext import commands
from discord import app_commands
import logging

from bot.config import ADMIN_USER_IDS, OWNER_ROLE, MODO_PUBLICO

logger = logging.getLogger(__name__)


def _is_id_in_list(user_id, id_list):
    try:
        return str(user_id) in [str(x) for x in (id_list or [])]
    except Exception as e:
        logger.exception("Error checking id in list in _is_id_in_list")
        return False


def is_config_admin():
    """Decorator for text commands. In MODO_PUBLICO only users in ADMIN_USER_IDS can run.
    In private mode, server administrators OR configured admin_user_ids OR owner_role can run.
    """
    async def predicate(ctx):
        # Deny in DMs
        if not ctx.guild:
            return False

        # Public mode: only configured admin_user_ids
        if MODO_PUBLICO:
            return _is_id_in_list(ctx.author.id, ADMIN_USER_IDS)

        # Private mode: allow configured admin_user_ids
        if _is_id_in_list(ctx.author.id, ADMIN_USER_IDS):
            return True

        # Owner role (if configured)
            try:
                if OWNER_ROLE:
                    for role in getattr(ctx.author, 'roles', []):
                        if str(role.id) == str(OWNER_ROLE):
                            return True
            except Exception as e:
                logger.exception("Error checking owner role in is_config_admin")

        # Fallback to server administrator permission
        try:
            return ctx.author.guild_permissions.administrator
        except Exception as e:
            logger.exception("Error checking guild permissions in is_config_admin")
            return False

    return commands.check(predicate)


def is_config_admin_app():
    """Decorator for app commands (interactions). Same semantics as `is_config_admin`."""
    def predicate(interaction: discord.Interaction) -> bool:
        # Deny in DMs (app commands in DMs may have limited data)
        if not interaction.guild:
            return False

        if MODO_PUBLICO:
            return _is_id_in_list(interaction.user.id, ADMIN_USER_IDS)

        # Private mode
        if _is_id_in_list(interaction.user.id, ADMIN_USER_IDS):
            return True

        # Owner role
        try:
            member = interaction.user
            # interaction.user may be a Member in guild context
            roles = [getattr(r, 'id', None) for r in getattr(member, 'roles', [])]
            if OWNER_ROLE and str(OWNER_ROLE) in [str(r) for r in roles if r is not None]:
                return True
        except Exception as e:
            logger.exception("Error checking owner role in is_config_admin_app")

        # Server admin
        try:
            return interaction.user.guild_permissions.administrator
        except Exception as e:
            logger.exception("Error checking guild permissions in is_config_admin_app")
            return False

    return app_commands.check(predicate)
