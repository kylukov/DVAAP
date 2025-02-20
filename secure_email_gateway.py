import asyncio
import logging
import dns.resolver
from aiosmtpd.controller import Controller
from email.message import EmailMessage
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename="email_gateway.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SecureEmailGateway")

class SecureEmailHandler:
    async def handle_DATA(self, server, session, envelope):
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        content = envelope.content.decode('utf-8', errors='replace')

        logger.info(f"Получено письмо от: {mail_from}")
        logger.info(f"Получатели: {rcpt_tos}")

        # Проверка SPF
        spf_result = self.check_spf(mail_from)
        if not spf_result["valid"]:
            logger.warning(f"SPF провалился для {mail_from}: {spf_result['reason']}")
            return "550 SPF check failed"

        # Проверка на спам
        if "spam" in content.lower():
            logger.warning(f"Обнаружен спам в письме от {mail_from}")
            return "550 Spam detected"

        # Проверка вложений (имитация антивирусной проверки)
        if self.has_malicious_attachment(content):
            logger.warning(f"Обнаружено вредоносное вложение в письме от {mail_from}")
            return "550 Malicious attachment detected"

        logger.info("Письмо прошло все проверки.")
        return '250 OK'

    def check_spf(self, sender_email):
        try:
            domain = sender_email.split('@')[-1]
            answers = dns.resolver.resolve(domain, 'TXT')
            for record in answers:
                if record.to_text().startswith('"v=spf1'):
                    logger.info(f"SPF найден для {domain}: {record.to_text()}")
                    return {"valid": True}
        except Exception as e:
            logger.error(f"Ошибка проверки SPF для {sender_email}: {e}")
        return {"valid": False, "reason": "SPF record not found"}

    def has_malicious_attachment(self, content):
        # Имитируем антивирусную проверку
        if "malware" in content.lower():
            return True
        return False

if __name__ == "__main__":
    handler = SecureEmailHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()

    logger.info("Secure Email Gateway запущен. Нажмите Ctrl+C для завершения.")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Secure Email Gateway остановлен.")
    finally:
        controller.stop()