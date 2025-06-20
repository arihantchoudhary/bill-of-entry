import os
import asyncio
from openai import AsyncOpenAI
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class GPT:
    def __init__(self, api_key: Optional[str] = None, 
                 default_model: str = "gpt-4o", 
                 default_temperature: float = 0.7, 
                 default_max_tokens: int = 1000, 
                 default_frequency_penalty: float = 0.0):
        """
        Initialize the GPT class with default parameters.

        Args:
            api_key (str): Your OpenAI API key.
            default_model (str): Default model to use for API calls.
            default_temperature (float): Default sampling temperature for the model.
            default_max_tokens (int): Default maximum tokens to generate.
            default_frequency_penalty (float): Default frequency penalty for the model.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables or provided as a parameter.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.default_frequency_penalty = default_frequency_penalty
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

    async def call(self, 
                       system_prompt: str, 
                       user_prompt: str, 
                       dynamic_inputs: Optional[Dict[str, Any]] = None, 
                       model: Optional[str] = None, 
                       temperature: Optional[float] = None, 
                       max_tokens: Optional[int] = None, 
                       frequency_penalty: Optional[float] = None) -> str:
        """
        Asynchronously call the OpenAI GPT API with dynamic and static prompts.

        Args:
            system_prompt (str): The system prompt for context.
            user_prompt (str): The user prompt to guide the response.
            dynamic_inputs (dict): Key-value pairs to dynamically populate the user prompt.
            model (str): Model to use (optional, defaults to class default).
            temperature (float): Sampling temperature (optional, defaults to class default).
            max_tokens (int): Maximum number of tokens to generate (optional, defaults to class default).
            frequency_penalty (float): Frequency penalty (optional, defaults to class default).

        Returns:
            str: The assistant's response.
        """
        async with self.semaphore:  # Limit concurrency
            try:
                # Use defaults if specific values are not provided
                model = model or self.default_model
                temperature = temperature if temperature is not None else self.default_temperature
                max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
                frequency_penalty = frequency_penalty if frequency_penalty is not None else self.default_frequency_penalty

                # Format the user prompt with dynamic inputs if provided
                if dynamic_inputs and isinstance(dynamic_inputs, dict):
                    user_prompt = user_prompt.format(**dynamic_inputs)

                # Make the async API call
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    frequency_penalty=frequency_penalty
                )

                # Extract and return the assistant's response
                return response.choices[0].message.content

            except Exception as e:
                print(f"Error calling OpenAI API: {str(e)}")
                raise
# Example call to async API
async def main():
    gpt = GPT()
    gpt_response = await gpt.call(
        system_prompt="You are a helpful assistant.",
        user_prompt="Tell me a fun fact about space."
    )
    print(gpt_response)

if __name__ == "__main__":
    asyncio.run(main())

# # Initialize the Gemini class
# gemini = Gemini(api_key=os.getenv("GEMINI_API_KEY"))
# gemini_response = gemini.call(prompt="Tell me a fun fact about space.")

# # Initialize the Anthropic class
# anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# anthropic_response = anthropic.call(prompt="Tell me a fun fact about space.")