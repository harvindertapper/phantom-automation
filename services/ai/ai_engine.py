from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'AI Engine'})

@app.route('/understand', methods=['POST'])
def understand_task():
    """
    AI understands natural language task and plans execution
    """
    data = request.json
    user_task = data.get('task', '')
    
    print(f"\n🧠 Understanding task: {user_task}")
    
    prompt = f"""
Analyze this automation request and create an execution plan:

Task: {user_task}

Respond with JSON:
{{
    "task_type": "web_automation/code_execution/data_processing/api_call",
    "complexity": "simple/medium/complex",
    "steps": [
        {{
            "action": "navigate/click/type/extract/run_code",
            "target": "what to interact with",
            "value": "value if needed",
            "description": "what this step does"
        }}
    ],
    "estimated_time": "time in seconds",
    "requires_browser": true/false,
    "requires_code": true/false
}}
"""
    
    try:
        response = model.generate_content(prompt)
        plan_text = response.text
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            # Fallback plan
            plan = {
                "task_type": "unknown",
                "complexity": "medium",
                "steps": [{"action": "manual", "description": user_task}],
                "estimated_time": "unknown",
                "requires_browser": False,
                "requires_code": False
            }
        
        print(f"✅ Plan created: {plan['task_type']}")
        return jsonify({
            'success': True,
            'plan': plan
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-code', methods=['POST'])
def generate_code():
    """
    Generate Python code for automation
    """
    data = request.json
    task = data.get('task', '')
    context = data.get('context', '')
    
    print(f"\n💻 Generating code for: {task}")
    
    prompt = f"""
Generate production-ready Python code for this task:

Task: {task}
Context: {context}

Requirements:
- Complete, executable code
- Error handling
- Clear output
- Use only built-in libraries or: os, sys, pathlib, shutil, json

Return ONLY the code:
"""
    
    try:
        response = model.generate_content(prompt)
        code = response.text
        
        # Clean markdown
        if '```
            code = code.split('```python').split('```[1]
        elif '```' in code:
            code = code.split('``````')[0].strip()
        
        print(f"✅ Code generated ({len(code)} chars)")
        return jsonify({
            'success': True,
            'code': code
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-browser-script', methods=['POST'])
def generate_browser_script():
    """
    Generate browser automation script
    """
    data = request.json
    task = data.get('task', '')
    url = data.get('url', '')
    
    print(f"\n🌐 Generating browser script for: {task}")
    
    prompt = f"""
Generate Playwright Python code for this browser automation:

Task: {task}
URL: {url}

Return JSON with steps:
{{
    "steps": [
        {{"action": "navigate", "url": "..."}},
        {{"action": "click", "selector": "..."}},
        {{"action": "type", "selector": "...", "text": "..."}},
        {{"action": "extract", "selector": "...", "attribute": "text/href"}}
    ]
}}
"""
    
    try:
        response = model.generate_content(prompt)
        result = response.text
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            script = json.loads(json_match.group())
        else:
            script = {"steps": []}
        
        print(f"✅ Browser script generated ({len(script['steps'])} steps)")
        return jsonify({
            'success': True,
            'script': script
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('AI_SERVICE_PORT', 5001))
    print(f"🧠 AI Engine starting on port {port}...")
    app.run(debug=True, host='0.0.0.0', port=port)
