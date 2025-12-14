import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GroqClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GroqClient, cls).__new__(cls)
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.warning("Chave Groq não configurada. AI features will fail.")
                cls._instance.client = None
            else:
                try:
                    cls._instance.client = Groq(api_key=api_key)
                except Exception as e:
                    logger.error(f"Erro ao inicializar Groq client: {e}")
                    cls._instance.client = None
        return cls._instance

    def _get_client(self):
        return self.client

    def generate_summary(self, texts, lang='pt'):
        client = self._get_client()
        if not client:
            return "Erro: Chave Groq não configurada."

        if not texts:
            return ""

        # Combina textos (trunca para evitar limites potenciais de tokens se necessário, embora o texto puro geralmente caiba)
        combined_text = "\n\n".join(texts)[:15000] # Heurística de limite seguro

        prompt = (
            f"Analise as seguintes notícias e escreva um resumo consolidado em {lang}. "
            "Destaque os pontos principais e a cronologia dos eventos se relevante. "
            "O resumo deve ser jornalístico, direto e neutro.\n\n"
            f"Notícias:\n{combined_text}"
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile", # modelo mais rapido
                temperature=0.5,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            return f"Erro ao gerar resumo: {e}"

    def translate_content(self, text, target_lang='pt'):
        client = self._get_client()
        if not client:
            return "Erro: Chave Groq não configurada."
        
        if not text:
            return ""

        prompt = (
            f"Traduza o seguinte texto para o idioma português (pt-BR). "
            "Mantenha o tom jornalístico e a formatação original se possível.\n\n"
            f"Texto:\n{text}"
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao traduzir: {e}")
            return f"Erro ao traduzir: {e}"

# Helper de instancia global
_client = GroqClient()

def generate_summary(texts):
    return _client.generate_summary(texts)

def translate_content(text):
    return _client.translate_content(text)
