import os
import base64
from typing import Optional, Union, List
from dotenv import load_dotenv
from logging import getLogger
from pydantic import BaseModel
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from backend.src.firebase_utils import db
from backend.src.moderator.prompts import gpt_vision_prompt

# Load environment variables
load_dotenv()

# Initialize logger
logger = getLogger(__name__)

# Ensure OpenAI API key is set
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logger.error("OpenAI API Key is missing.")
    raise ValueError("OpenAI API Key not found. Make sure it's set in the environment variables.")


# Pydantic model for the output result
class ModerationResult(BaseModel):
    action: bool


def get_rules() -> str:
    """
    Fetches the list of rules for the moderation task from Firebase.
    Returns a string of rules joined with newline characters.
    """
    try:
        rules = db.collection("rules").get()
        rules_content = [rule.to_dict()["content"] for rule in rules]
        return "\n".join(rules_content)
    except Exception as e:
        logger.error(f"Failed to retrieve rules: {e}")
        raise


def process_listing_step_1(description: str, title: str, image_binary: bytes, rules: str) -> str:
    """
    Step 1: Use GPT-4 API to analyze the listing's title, description, and image.
    Returns the reasoning as a string.

    Args:
        - description (str): The listing's description.
        - title (str): The listing's title.
        - image_binary (bytes): The image in binary format.
        - rules (str): Moderation rules fetched from the database.

    Returns:
        - str: The reasoning from GPT-4 on whether the listing should be flagged.
    """
    try:
        # Convert the image to base64 format
        base64_image = base64.b64encode(image_binary).decode("utf-8")

        # Fill the prompt using the PromptTemplate
        prompt_template = PromptTemplate.from_template(gpt_vision_prompt)
        prompt_filled = prompt_template.format(
            title=title,
            description=description,
            exclusions=rules
        )

        prompt_message = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_filled
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ]

        # Call OpenAI's GPT-4 to process the image and text
        params = {
            "model": "gpt-4o",
            "messages": prompt_message,
            "max_tokens": 4096,
        }
        client = OpenAI(api_key=API_KEY)
        result = client.chat.completions.create(**params)
        return result.choices[0].message.content

    except Exception as e:
        logger.error(f"Failed to process the listing with GPT-4: {e}")
        raise


def process_listing(title: str, description: Optional[str], image_bytes: bytes) -> Union[dict, None]:
    """
    Moderates a listing by analyzing the title, description, and image.
    Returns a JSON response with reasoning and flag action (True/False).

    Args:
        - title (str): The listing's title.
        - description (Optional[str]): The listing's description.
        - image_bytes (bytes): The image in binary format.
        - rules (str): The moderation rules.

    Returns:
        - dict: A dictionary with `reasoning` and `action` (True/False).
    """

    try:
        rules = get_rules()

    except Exception as e:
        logger.error(f"Failed to retrieve rules: {e}")
        return None

    try:
        # Step 1: Get reasoning from GPT-4 API
        reasoning = process_listing_step_1(description, title, image_bytes, rules)
        logger.info(f"Reasoning: {reasoning}")

        # Initialize the output parser and model
        parser = JsonOutputParser(pydantic_object=ModerationResult)
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=API_KEY)

        # Prompt template for moderation decision
        moderation_prompt = PromptTemplate(
            input_variables=["reasoning", "title", "description", "exclusions"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            template="""
            You are a content moderator. Review the listing and decide if it should be flagged.
            Respond 'True' for flagging, 'False' otherwise.

            Listing details:
            - Title: {title}
            - Description: {description}

            Reasoning:
            {reasoning}

            {format_instructions}
            """
        )

        # Run the chain to get the final moderation response
        moderation_chain = moderation_prompt | model | parser
        moderation_response = moderation_chain.invoke({
            "reasoning": reasoning,
            "title": title,
            "description": description or "No description provided.",
            "exclusions": rules
        })

        logger.info(f"Moderation response: {moderation_response}")

        return {
            "reasoning": reasoning,
            "action": moderation_response["action"]
        }

    except Exception as e:
        logger.error(f"Failed to moderate listing: {e}")
        return None


if __name__ == "__main__":
    # Test moderation with a sample image
    try:
        with open("backend/src/moderator/test/rolex.jpg", "rb") as f:
            image_bytes = f.read()

        title = "Rolex Watch"
        description = "A Rolex watch in excellent condition."

        response = process_listing(title, description, image_bytes)
        print(response)

    except Exception as e:
        logger.error(f"Failed to test the moderation task: {e}")
