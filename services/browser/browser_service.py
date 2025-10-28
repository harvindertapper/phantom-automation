from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import os
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global browser instance
playwright = None
browser = None
page = None

def ensure_browser():
    """Ensure browser is running"""
    global playwright, browser, page
    
    if not playwright:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        print("✅ Browser started")

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'Browser Service'})

@app.route('/execute', methods=['POST'])
def execute_script():
    """
    Execute browser automation script
    """
    data = request.json
    script = data.get('script', {})
    steps = script.get('steps', [])
    
    print(f"\n🌐 Executing {len(steps)} browser steps")
    
    ensure_browser()
    
    results = []
    
    try:
        for i, step in enumerate(steps, 1):
            action = step.get('action')
            print(f"  Step {i}: {action}")
            
            if action == 'navigate':
                page.goto(step['url'], timeout=30000)
                results.append({
                    'step': i,
                    'action': action,
                    'success': True,
                    'result': f"Navigated to {step['url']}"
                })
            
            elif action == 'click':
                page.click(step['selector'], timeout=10000)
                results.append({
                    'step': i,
                    'action': action,
                    'success': True,
                    'result': f"Clicked {step['selector']}"
                })
            
            elif action == 'type':
                page.fill(step['selector'], step['text'])
                results.append({
                    'step': i,
                    'action': action,
                    'success': True,
                    'result': f"Typed into {step['selector']}"
                })
            
            elif action == 'extract':
                selector = step['selector']
                attribute = step.get('attribute', 'text')
                
                if attribute == 'text':
                    text = page.locator(selector).text_content()
                    results.append({
                        'step': i,
                        'action': action,
                        'success': True,
                        'result': text
                    })
                elif attribute == 'href':
                    href = page.locator(selector).get_attribute('href')
                    results.append({
                        'step': i,
                        'action': action,
                        'success': True,
                        'result': href
                    })
            
            elif action == 'screenshot':
                path = step.get('path', 'screenshot.png')
                page.screenshot(path=path)
                results.append({
                    'step': i,
                    'action': action,
                    'success': True,
                    'result': f"Screenshot saved: {path}"
                })
            
            elif action == 'wait':
                duration = step.get('duration', 1000)
                page.wait_for_timeout(duration)
                results.append({
                    'step': i,
                    'action': action,
                    'success': True,
                    'result': f"Waited {duration}ms"
                })
        
        print(f"✅ All steps completed")
        return jsonify({
            'success': True,
            'results': results
        })
    
    except PlaywrightTimeout as e:
        print(f"❌ Timeout: {e}")
        return jsonify({
            'success': False,
            'error': f'Timeout: {str(e)}',
            'results': results
        }), 500
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'results': results
        }), 500

@app.route('/navigate', methods=['POST'])
def navigate():
    """Simple navigation"""
    data = request.json
    url = data.get('url')
    
    ensure_browser()
    
    try:
        page.goto(url, timeout=30000)
        title = page.title()
        return jsonify({
            'success': True,
            'url': url,
            'title': title
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/screenshot', methods=['POST'])
def screenshot():
    """Take screenshot"""
    data = request.json
    path = data.get('path', 'screenshot.png')
    
    ensure_browser()
    
    try:
        page.screenshot(path=path)
        
        # Encode as base64 for API response
        with open(path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        
        return jsonify({
            'success': True,
            'path': path,
            'image_base64': img_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/close', methods=['POST'])
def close_browser():
    """Close browser"""
    global browser, playwright, page
    
    try:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
        browser = None
        playwright = None
        page = None
        
        return jsonify({
            'success': True,
            'message': 'Browser closed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('BROWSER_SERVICE_PORT', 5002))
    print(f"🌐 Browser Service starting on port {port}...")
    app.run(debug=True, host='0.0.0.0', port=port)
