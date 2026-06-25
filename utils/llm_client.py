import sys
import google.generativeai as genai
import groq as groq_lib


class LLMClient:
    def __init__(self, gemini_api_key: str, groq_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.groq_api_key = groq_api_key

    def generate(self, prompt: str, system: str, temperature: float = 0.1):
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                model = genai.GenerativeModel(
                    "gemini-2.0-flash",
                    system_instruction=system,
                    generation_config=genai.types.GenerationConfig(temperature=temperature),
                )
                response = model.generate_content(prompt, request_options={"timeout": 60})
                return response.text, "gemini"
            except Exception as e:
                print(f"[LLMClient] Gemini failed: {e}", file=sys.stderr)

        if self.groq_api_key:
            try:
                client = groq_lib.Groq(api_key=self.groq_api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    timeout=60,
                )
                return response.choices[0].message.content, "groq"
            except Exception as e:
                print(f"[LLMClient] Groq failed: {e}", file=sys.stderr)

        raise RuntimeError("Both Gemini and Groq failed or no API keys provided.")
