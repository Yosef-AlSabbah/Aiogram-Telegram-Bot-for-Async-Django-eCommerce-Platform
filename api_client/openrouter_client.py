import aiohttp
import logging
from typing import List, Dict, Any, Optional
import json

from config import settings
from redis_client.conversation_history import ConversationHistoryManager

# Set up logging
logger = logging.getLogger(__name__)


async def generate_customer_support_reply(user_message: str, user_id: int = None) -> str:
    """Get AI response from OpenRouter API using aiohttp

    Args:
        user_message: The message from the user
        user_id: Telegram user ID to maintain conversation history
    """
    # Default system message for the customer support AI
    system_message = {
        "role": "system",
        "content": "أنت مساعد دعم عملاء مفيد لبوت Luqta eShop على تيليجرام. يتم إجراء جميع التفاعلات بشكل أساسي من خلال الأوامر. قدم ردودًا موجزة ودقيقة باللغة العربية وباللهجة الغزاوية على استفسارات العملاء. فقط عندما يُسأل تحديدًا عن تسجيل الدخول أو إنشاء حساب، اشرح عملية التسجيل. فقط عندما يُسأل عن الأوامر المتاحة أو كيفية استخدام النظام، اذكر أنه: (1) لتسجيل الدخول، استخدم الأمر /login؛ (2) للتسجيل، استخدم الأمر /register؛ (3) للتعرف على الميزات المتاحة، استخدم الأمر /help. لاحظ أن جميع الأوامر يمكن استخدامها أيضًا بترجمتها العربية. إذا أدخل المستخدم نصًا يبدو كأمر ولكنه غير معروف (يبدأ بـ / ولكنه لا يتطابق مع الأوامر المعروفة)، أخبرهم أن الأمر قد يكون مهجئًا بشكل خاطئ واقترح الأمر المطابق الأقرب. لا تذكر هذه الأوامر استباقيًا في كل رد. إذا لم تكن تعرف الإجابة على سؤال ما، فقط اعترف بذلك ولا تحاول تخمين إجابة أو تقديم معلومات غير مؤكدة."
    }

    # Create message data with current user message
    user_message_data = {"role": "user", "content": user_message}

    # Initialize messages list
    messages = [system_message]

    # If user_id is provided, use conversation history
    if user_id is not None:
        history_manager = ConversationHistoryManager()

        # Get existing conversation history
        history = await history_manager.get_conversation_history(user_id)

        # If history exists, use it instead of default system message
        if history:
            messages = history

        # Add the current user message to history
        await history_manager.add_message(user_id, user_message_data)

    # Add current user message to the messages list for this request
    if not messages or messages[-1] != user_message_data:
        messages.append(user_message_data)

    # Debug info about API key
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        logger.error("OPENROUTER_API_KEY is not set in environment variables")
        return "عذراً، هناك مشكلة في إعداد المساعد. الرجاء الاتصال بالدعم الفني."

    # Show just the first and last few characters of the API key for security
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
    logger.debug(f"Using OpenRouter API key: {masked_key}")

    logger.debug(f"Sending messages to OpenRouter: {json.dumps(messages, ensure_ascii=False)}")

    # Models to try in order of preference
    models = [
        "deepseek/deepseek-r1:free",  # First choice
        "openai/gpt-3.5-turbo",       # Fallback option
        "meta/llama-3-instruct:1:latest"  # Final fallback
    ]

    last_error = None

    # Try each model until one works
    for model in models:
        try:
            logger.info(f"Attempting to use model: {model}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://luqta.ps",
                        "X-Title": "Luqta eShop",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500,
                    },
                    timeout=30
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error with {model} (status {response.status}): {error_text}")
                        last_error = f"API Error {response.status}: {error_text}"
                        continue  # Try next model

                    response_data = await response.json()
                    logger.debug(f"OpenRouter response from {model}: {json.dumps(response_data, ensure_ascii=False)}")

                    try:
                        assistant_message = response_data["choices"][0]["message"]["content"]

                        # If model worked but wasn't first choice, log that info
                        if model != models[0]:
                            logger.info(f"Successfully used fallback model: {model}")

                        # If user_id is provided, save the assistant's reply to history
                        if user_id is not None:
                            await history_manager.add_message(
                                user_id, {"role": "assistant", "content": assistant_message}
                            )

                        return assistant_message
                    except (KeyError, IndexError) as e:
                        # Log the exact structure that caused the error
                        logger.error(f"Error extracting message from {model} response: {str(e)}. Response data: {json.dumps(response_data, ensure_ascii=False)}")
                        last_error = f"Model {model} returned malformed response: {str(e)}"
                        continue  # Try next model

        except aiohttp.ClientError as e:
            logger.error(f"Network error with OpenRouter API using {model}: {str(e)}")
            last_error = f"Network error with {model}: {str(e)}"
            continue  # Try next model
        except Exception as e:
            logger.exception(f"Unexpected error with {model}: {str(e)}")
            last_error = f"Unexpected error with {model}: {str(e)}"
            continue  # Try next model

    # If we get here, all models failed
    logger.error(f"All models failed. Last error: {last_error}")
    return "عذراً، حدث خطأ في الاتصال بالخادم. الرجاء المحاولة مرة أخرى لاحقاً."


async def clear_user_conversation(user_id: int) -> None:
    """Clear the conversation history for a specific user"""
    history_manager = ConversationHistoryManager()
    await history_manager.clear_history(user_id)


async def test_openrouter_connection() -> Dict[str, Any]:
    """Test connection to OpenRouter API and return status information

    Returns:
        Dictionary with status information and available models
    """
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        return {"status": "error", "message": "API key not configured"}

    try:
        async with aiohttp.ClientSession() as session:
            # First test a basic models list request
            async with session.get(
                url="https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "code": response.status,
                        "message": f"API error: {error_text}"
                    }

                models_data = await response.json()

                # Extract available models that match our preferences
                available_models = []
                for model in models_data.get("data", []):
                    if "deepseek" in model.get("id", "") or "gpt" in model.get("id", ""):
                        available_models.append({
                            "id": model.get("id"),
                            "name": model.get("name"),
                            "context_length": model.get("context_length")
                        })

                return {
                    "status": "success",
                    "message": "Connection successful",
                    "available_models": available_models
                }

    except Exception as e:
        return {"status": "error", "message": f"Connection error: {str(e)}"}
