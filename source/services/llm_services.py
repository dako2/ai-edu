import openai
from openai import OpenAI  # Replace with the actual OpenAI SDK
import os


class OpenAILLM:
    def __init__(self, api_key = None, model="gpt-4o"):
        """
        Initialize the OpenAILLM with an API key and model name.
        
        :param api_key: Your OpenAI API key.
        :param model: The model to use for answering questions.
        """
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.system_prompt="You are a helpful assistant."
        self.client = OpenAI()

    def answer(self, question, temperature=0.7, max_tokens=150):
        """
        Ask a question and receive an answer from the OpenAI language model.
        
        :param question: The question to be answered.
        :param system_prompt: The system instruction to guide the assistant.
        :param temperature: Sampling temperature for creativity.
        :param max_tokens: Maximum tokens in the response.
        :return: The answer text provided by the model.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
 


