from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import tempfile
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'Task Executor'})

@app.route('/execute-code', methods=['POST'])
def execute_code():
    """
    Execute Python code safely
    """
    data = request.json
    code = data.get('code', '')
    timeout = data.get('timeout', 30)
    
    print(f"\n🔧 Executing code ({len(code)} chars)")
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Execute with timeout
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print(f"✅ Execution successful")
            return jsonify({
                'success': True,
                'output': result.stdout,
                'error': None
            })
        else:
            print(f"❌ Execution failed")
            return jsonify({
                'success': False,
                'output': result.stdout,
                'error': result.stderr
            })
    
    except subprocess.TimeoutExpired:
        os.unlink(temp_file)
        print(f"❌ Timeout")
        return jsonify({
            'success': False,
            'error': f'Execution timeout after {timeout}s'
        }), 500
    
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/system-command', methods=['POST'])
def system_command():
    """
    Execute system command
    """
    data = request.json
    command = data.get('command', '')
    
    print(f"\n⚙️ Executing command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('AUTOMATION_SERVICE_PORT', 5003))
    print(f"🔧 Task Executor starting on port {port}...")
    app.run(debug=True, host='0.0.0.0', port=port)
