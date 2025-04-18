import os
async def check_subscription(user_id: int, bot):
    """Проверка подписки пользователя на канал"""
    try:
        CHANNEL_ID = os.getenv("CHANNEL_ID")
        if not CHANNEL_ID:
            return False
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error in utils: {str(e)}")
        return False