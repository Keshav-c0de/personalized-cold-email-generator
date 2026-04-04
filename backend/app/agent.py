import os
from openai import AsyncOpenAI
from ollama import AsyncClient
from dotenv import load_dotenv

load_dotenv()

CLIENT = AsyncOpenAI(api_key=os.getenv("API_KEY"),
                        base_url="https://models.inference.ai.azure.com"),
# Ensure your GEMINI_API_KEY is set in your environment variables

async def get_pointers(raw_html: any):
    PROMPT = f"""You are an email assistant. Your task is to extract relevant information from the provided raw HTML content of a webpage to create personalized pointers that can be used to generate a professional and concise email response. Please analyze the content and identify key details such as the recipient's name, their role or title, any recent activities or posts they have made, and any other relevant information that can help personalize the email response. The extracted pointers should be concise and directly related to the recipient, providing valuable context for crafting an engaging and relevant email. Please return the extracted pointers in a structured format that can be easily utilized for email generation. also do a DISC analysis with the post share in content
    Here is the raw HTML content to analyze: {raw_html}"""
    
    response = await CLIENT.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        top_p=0.95,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return response.choices[0].message.content

async def get_email_response(prompt: str, pointers: str):
    PROMPT = f"""You are an email assistant. Your task is to generate a professional and concise email response based on the following prompt: "{prompt}". Please ensure that the response is clear, polite, and addresses the main points of the prompt effectively. You can use the pointers, these pointer contain personal info about the recipient use them with care , dont share too much: {pointers} to make the email personalized and relevant. The email should be structured with a greeting, body, and closing. Please keep the response under 200 words and maintain a friendly yet professional tone throughout. Three main things to keep in mind is 1. Be concise and to the point, avoiding unnecessary details. 2. write in a way that the reader find it vaulable and engaging. 3. Always end with a call to action or a closing statement that encourages further communication if needed. there will be a DISC analysis of the recipient in the pointer, use that to write the email in a way that resonates with the recipient's communication style. Please generate the email response based on these guidelines and ensure it is well-crafted and effective in addressing the prompt. dont use posts in pointers to write eamil it is just for disc analysis and understand the tone which the recipient uses in their communication."""

    # Stream is set to True here
    response = await CLIENT.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        top_p=0.95,
        stream=True, 
        messages=[{"role": "user", "content": PROMPT}],
    )
    return response

async def check_email_response(email_response: str, pointers: str):
    PROMPT= f"""You are an email assistant. Your task is to evaluate the quality of the generated email response based on the following criteria: 1. Relevance: Does the response directly address the main points of the prompt? 2. Clarity: Is the response clear and easy to understand? 3. Tone: Does the response maintain a polite and professional tone? 4. Conciseness: Is the response concise and to the point, avoiding unnecessary details? 5. Engagement: Does the response provide value to the reader and encourage further communication if needed? 6. Personalization: Does the response effectively utilize the provided pointers to make the email personalized and relevant? Please evaluate the draft and give back a clear feedback to improve the email response based on these criteria. If the response meets all the criteria, please confirm that it is a well-crafted email response. If there are areas for improvement, please provide specific feedback on how to enhance the response to better meet the criteria.  the email response to evaluate is: "{email_response}" i am also sharing the pointers again for your reference: {pointers}"""

    response = await AsyncClient().chat(model="llama3.2", messages=[{"role": "user", "content": PROMPT}])
    
    # Extract the clean text string from Ollama's dictionary response
    feedback_text = response['message']['content']
    print(f"\n--- Ollama Evaluation Feedback ---\n{feedback_text}\n----------------------------------\n")
    return feedback_text

async def finalemail(feedback: str, email_response: str, pointers: str):
    PROMPT = f"""You are an email assistant. Your task is to refine the generated email response based on the provided feedback. The feedback is as follows: "{feedback}". Please use this feedback to enhance the email response, ensuring that it better meets the criteria of relevance, clarity, tone, conciseness, engagement, and personalization. The original email response is: "{email_response}". Please make necessary adjustments to improve the quality of the email while maintaining a professional and polite tone. Ensure that the refined email effectively addresses the main points of the prompt and provides value to the reader. Please generate the final version of the email response based on this feedback and ensure it is well-crafted and effective in addressing the prompt.I am also sharing the personal information pointers again for your reference: {pointers}. what not to do 1. dont return improvement use the email"""

    response = await CLIENT.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        top_p=0.95,
        stream=False,
        messages=[{"role": "user", "content": PROMPT}],
    )

    # Extract the final string
    final_text = response.choices[0].message.content
    print(f"\n--- Final Refined Email ---\n{final_text}\n---------------------------\n")
    return final_text


async def generate_email(prompt: str, raw_html: any):
    print("Extracting pointers with Gemini...")
    pointers = await get_pointers(raw_html)
    
    print("\nGenerating draft email (Streaming)...")
    email_stream = await get_email_response(prompt, pointers)
    
    # Accumulate the stream chunks into a complete string to pass to Ollama
    draft_email_text = ""
    async for chunk in email_stream:
        # Standard handling for choices[0].delta.content
        if chunk.choices and chunk.choices[0].delta.content:
            text_piece = chunk.choices[0].delta.content
            draft_email_text += text_piece
            print(text_piece, end="", flush=True)
    
    print("\n\nEvaluating draft with local Llama 3.2...")
    feedback = await check_email_response(draft_email_text, pointers)
    
    print("Generating final refined email with Gemini...")
    final_email = await finalemail(feedback, draft_email_text, pointers)

    return final_email