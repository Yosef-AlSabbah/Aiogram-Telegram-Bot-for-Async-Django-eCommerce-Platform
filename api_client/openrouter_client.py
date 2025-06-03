import aiohttp

from config import settings


async def generate_customer_support_reply(user_message: str) -> str:
    """Get AI response from OpenRouter API using aiohttp"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://luqta.ps",
                    "X-Title": "Luqta eShop",
                },
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [
                        {
                            "role": "system",
                            "content": "أنت مساعد دعم عملاء مفيد لبوت Luqta eShop على تيليجرام. يتم إجراء جميع التفاعلات بشكل أساسي من خلال الأوامر. قدم ردودًا موجزة ودقيقة باللغة العربية وباللهجة الغزاوية على استفسارات العملاء. فقط عندما يُسأل تحديدًا عن تسجيل الدخول أو إنشاء حساب، اشرح عملية التسجيل. فقط عندما يُسأل عن الأوامر المتاحة أو كيفية استخدام النظام، اذكر أنه: (1) لتسجيل الدخول، استخدم الأمر /login؛ (2) للتسجيل، استخدم الأمر /register؛ (3) للتعرف على الميزات المتاحة، استخدم الأمر /help. لاحظ أن جميع الأوامر يمكن استخدامها أيضًا بترجمتها العربية. إذا أدخل المستخدم نصًا يبدو كأمر ولكنه غير معروف (يبدأ بـ / ولكنه لا يتطابق مع الأوامر المعروفة)، أخبرهم أن الأمر قد يكون مهجئًا بشكل خاطئ واقترح الأمر المطابق الأقرب. لا تذكر هذه الأوامر استباقيًا في كل رد. إذا لم تكن تعرف الإجابة على سؤال ما، فقط اعترف بذلك ولا تحاول تخمين إجابة أو تقديم معلومات غير مؤكدة."                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                }
        ) as response:
            response_data = await response.json()
            try:
                return response_data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                return "Sorry, I couldn't generate a response at this time."
