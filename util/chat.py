import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import vertexai.preview.generative_models as generative_models
import re
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason, Tool
from util.config import cf
from google import genai
from google.genai import types
import base64
import streamlit as st
from google.oauth2 import service_account

from util.config import cf

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]


def google_gemini_generate_answer(question=''):
    question = f"""
        {question}

        IMPORTANT: Please provide the answer in plain text format, without any Markdown, formatting symbols (like **, _, `), emojis, or extra whitespace.
        """

    # 🔥 Load credentials from Streamlit secrets
    service_account_info = st.secrets["service_account"]
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    client = genai.Client(
        vertexai=True,
        project=cf.get("PROJECT_ID"),
        location="global",
    )

    if cf.get("ENV") != "dev":
        client = genai.Client(
            vertexai=True,
            project=cf.get("PROJECT_ID"),
            location="global",
            credentials=credentials,
        )

    model = "gemini-2.5-pro-preview-05-06"
    contents = [
        types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=question)
        ]
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature = 1,
        top_p = 1,
        seed = 0,
        max_output_tokens = 65535,
        safety_settings = [types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="OFF"
        )],
    )

    result = ""
    for chunk in client.models.generate_content_stream(
        model = model,
        contents = contents,
        config = generate_content_config,
        ):
        result += chunk.text
    return re.sub("\s\s+", " ", result.strip())


def google_gemini_generate_answer_with_grounding(question=''):
    result = ""
    try:
        if not question:
            return
        vertexai.init(project="anfinx-prod", location="us-central1")
        tools = [
            Tool.from_google_search_retrieval(
                google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval()
            ),
        ]
        model = GenerativeModel(
            "gemini-1.5-pro-001",
            tools=tools,
        )
        responses = model.generate_content(
            [question],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )

        for response in responses:
            if response.candidates[0].finish_reason != FinishReason.FINISH_REASON_UNSPECIFIED:
                continue
            result += response.text
        return re.sub("\s\s+", " ", result.strip())
    except Exception as e:
        # print(f'failed to get google_gemini_generate_answer_with_grounding')
        return re.sub("\s\s+", " ", result.strip())
