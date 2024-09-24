# GPT-4 Vision Prompt for Image and Description Review
gpt_vision_prompt = """
You are tasked with reviewing a listing that contains a title, description, and images. 
Your goal is to determine whether the listing should be flagged based on any inappropriate content or the presence of excluded items. 
Here are the details of the listing:
- Title: {title}
- Description: {description}

Here are the exclusions (words or items that are not allowed in any listing):
{exclusions}

Review the listing details and the provided images carefully. Extrapolate the location or landmark information when possible. 
Provide reasoning about whether the listing should be flagged based on the text and images.
"""