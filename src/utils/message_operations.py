import discord
from src.entities.user import User

async def get_ai_context_from_message(message: discord.Message) -> str:
    author = message.author
    name = author.name
    content = message.content

    if not author.bot:
        user: User = await User.load(userid=str(author.id))
        pronouns = user.profile.pronouns
        if len(pronouns) > 0:
            username = f"User {name} ({pronouns})"
        else:
            username = f"User {name}"
    else:
        username = f"Bot {name}"

    additional_context = []

    if message.attachments:
        for attachment in message.attachments:
            additional_context.append(f"sent an attachment: {attachment.filename}")

    if message.stickers:
        for sticker in message.stickers:
            additional_context.append(f"sent a sticker: {sticker.name}")

    if message.embeds:
        for embed in message.embeds:
            embed_title = embed.title if embed.title else "No Title"
            embed_description = embed.description if embed.description else "No Description"
            additional_context.append(f"sent an embed: {embed_title}, {embed_description}")

    content_and_context = content if content else ""
    if additional_context:
        content_and_context += " | " + " | ".join(additional_context) if content_and_context else " | ".join(additional_context)
    
    return f"[{username}]: {content_and_context}"