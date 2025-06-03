import aiogram.utils.markdown as md
from aiogram.enums import ParseMode
from api_client import UserClient

async def send_user_info(target, user_id: int):
    try:
        user = await UserClient.get_user(user_id)
        user_info = md.text(
            md.hbold("User Information:"),
            md.text(md.hbold("ID:"), user.id),
            md.text(md.hbold("Username:"), f"@{user.username if user.username else 'None'}"),
            md.text(md.hbold("Full Name:"), f"{user.first_name} {user.last_name}"),
            md.text(md.hbold("Phone:"), user.phone),
            md.text(md.hbold("Balance:"), user.balance),
            md.text(md.hbold("Date Joined:"), user.date_joined.strftime('%Y-%m-%d')),
            md.text(md.hbold("Is Active:"), "Yes" if user.is_active else "No"),
            md.text(md.hbold("Is Staff:"), "Yes" if user.is_staff else "No"),
            sep='\n'
        )
        await target.reply(text=user_info, parse_mode=ParseMode.HTML)
    except Exception as e:
        await target.reply(
            text=md.text(
                md.hbold("Error retrieving user:"),
                md.hcode(str(e)),
                sep='\n'
            ),
            parse_mode=ParseMode.HTML
        )