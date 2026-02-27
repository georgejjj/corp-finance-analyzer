"""
公司金融年报分析系统 - Flask Web 应用
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from analyzer import FinanceAnalyzer
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 配置
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 限制
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化分析器
analyzer = FinanceAnalyzer(api_key=os.getenv('DASHSCOPE_API_KEY'))


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传并分析 PDF 文件"""
    
    # Check file
    if 'file' not in request.files:
        return jsonify({'error': 'No file found'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are supported'}), 400
    
    try:
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 分析文件
        result = analyzer.analyze_pdf(filepath)
        
        # 返回结果
        return jsonify({
            'success': True,
            'filename': filename,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """直接分析文本（用于测试）"""
    
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text content'}), 400
    
    text = data['text']
    
    try:
        # 提取财务指标
        metrics = analyzer.extract_financial_metrics(text)
        
        # 提取 MD&A
        mda_text = analyzer.extract_mda_section(text)
        
        # 大模型分析
        analysis = analyzer.analyze_with_llm(metrics, mda_text)
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/status')
def status():
    """检查服务状态"""
    return jsonify({
        'status': 'running',
        'api_configured': bool(os.getenv('DASHSCOPE_API_KEY')),
        'version': '1.0.0'
    })


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    print("=" * 50)
    print("📊 Corporate Financial Report Analyzer")
    print("=" * 50)
    print(f"📁 Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print(f"🔑 API Configured: {'✓ Yes' if os.getenv('DASHSCOPE_API_KEY') else '✗ No'}")
    print("=" * 50)
    print("🌐 URL: http://localhost:5000")
    print("=" * 50)
    
    # Use gunicorn in production, not debug mode
    app.run(host='0.0.0.0', port=5000, debug=False)
