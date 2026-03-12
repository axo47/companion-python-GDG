from flask import Flask, render_template, request, jsonify
from google.adk.runners import InMemoryRunner
from google.genai import types
import asyncio
import os
from PyPDF2 import PdfReader

app = Flask(__name__)


runner = None
character_exists = os.path.exists('character_cv.py')

if character_exists:
    import character_cv
    runner = InMemoryRunner(
        agent=character_cv.root_agent,
        app_name="Demo App",
    )

adk_session = None
session_lock = asyncio.Lock()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
async def chat():
    user_message = request.json.get('message')

    if not character_exists:
        return jsonify({'response': user_message})

    global adk_session
    if adk_session is None:
        async with session_lock:
            if adk_session is None:
                adk_session = await runner.session_service.create_session(
                    app_name=runner.app_name, user_id="inapp_user"
                )

    content = types.Content(parts=[types.Part(text=user_message)])
    response_text = ""
    async for event in runner.run_async(
        user_id=adk_session.user_id,
        session_id=adk_session.id,
        new_message=content,
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            response_text += event.content.parts[0].text

    return jsonify({'response': response_text})

@app.route('/upload_cv', methods=['POST'])
async def upload_cv():
    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'PDF requis'}), 400

    reader = PdfReader(file)
    cv_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if not cv_text:
        return jsonify({'error': 'Impossible d\'extraire le texte du PDF'}), 400

    global adk_session
    if adk_session is None:
        async with session_lock:
            if adk_session is None:
                adk_session = await runner.session_service.create_session(
                    app_name=runner.app_name, user_id="inapp_user"
                )

    prompt = f"Please screen the following candidate CV:\n\n{cv_text}"
    content = types.Content(parts=[types.Part(text=prompt)])
    response_text = ""
    async for event in runner.run_async(
        user_id=adk_session.user_id,
        session_id=adk_session.id,
        new_message=content,
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            response_text += event.content.parts[0].text

    return jsonify({'response': response_text})


if __name__ == '__main__':
    app.run(debug=True)
