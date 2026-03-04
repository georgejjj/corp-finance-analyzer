"""
公司金融年报分析引擎
支持 PDF 解析、财务指标提取、MD&A 文本分析
"""

import fitz  # PyMuPDF
import re
import json
import dashscope
from dashscope import Generation
from typing import Dict, Optional
import os


class FinanceAnalyzer:
    """公司年报分析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化分析器
        
        Args:
            api_key: 通义千问 API Key，如不传则从环境变量读取
        """
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if self.api_key:
            dashscope.api_key = self.api_key
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从 PDF 提取文本
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            提取的文本内容
        """
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def _find_financial_summary(self, text: str) -> str:
        """Find the financial summary section (主要财务指标) for LLM extraction.

        Skips table-of-contents entries (lines with '...' dot leaders) and
        picks the first real section occurrence.

        Args:
            text: 年报全文

        Returns:
            包含财务摘要的文本片段
        """
        for keyword in ['主要会计数据', '主要财务指标', '财务概要']:
            start = 0
            while True:
                idx = text.find(keyword, start)
                if idx == -1:
                    break
                # Check if this is a TOC entry (has dot leaders nearby)
                context = text[max(0, idx - 50):idx + 100]
                if '...' in context or '…' in context:
                    start = idx + len(keyword)
                    continue
                return text[max(0, idx - 200):idx + 6000]
        # Fallback: first 8000 chars (summary is always near the top)
        return text[:8000]

    def extract_financial_metrics(self, text: str) -> Dict:
        """使用 LLM 提取财务指标

        Args:
            text: 年报文本

        Returns:
            财务指标字典
        """
        null_metrics = {
            'revenue': None,
            'net_profit': None,
            'total_assets': None,
            'total_liabilities': None,
            'operating_cash_flow': None,
            'net_assets': None,
            'roe': None,
            'gross_margin': None,
            'debt_ratio': None,
            'profit_margin': None,
        }

        if not self.api_key:
            return null_metrics

        financial_text = self._find_financial_summary(text)

        prompt = f"""You are a financial data extraction specialist. Extract the following metrics from this Chinese annual report text. Return ONLY valid JSON, no markdown fences, no explanation.

Normalize all monetary values to 亿元 (100 million CNY). Pay attention to the unit stated in the report:
- If the unit is 元, divide by 100,000,000
- If the unit is 千元, divide by 100,000
- If the unit is 百万元, divide by 100
- If the unit is 亿元, use as-is

Return percentage values as plain numbers (e.g., 24.13 not "24.13%").
For negative values (e.g., loss-making companies), return negative numbers.
Return null for any metric you genuinely cannot find in the text.

Required JSON keys:
{{
  "revenue": "<营业收入/营业总收入, in 亿元>",
  "net_profit": "<归属于上市公司/母公司股东的净利润, in 亿元>",
  "total_assets": "<资产总额/总资产, in 亿元>",
  "total_liabilities": "<负债合计/负债总额, in 亿元>",
  "operating_cash_flow": "<经营活动产生的现金流量净额, in 亿元>",
  "net_assets": "<归属于上市公司/母公司股东的净资产/所有者权益, in 亿元>",
  "roe": "<加权平均净资产收益率, number>",
  "gross_margin": "<综合毛利率, number or null if not available (e.g., banks)>",
  "debt_ratio": "<资产负债率, number>",
  "profit_margin": "<净利率 = net_profit/revenue * 100, number>"
}}

--- Annual Report Text ---
{financial_text}
"""

        try:
            response = Generation.call(
                model='qwen-plus',
                messages=[
                    {'role': 'system', 'content': 'You extract structured financial data from Chinese annual reports. Return only valid JSON.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=1000,
                temperature=0.1,
                stream=False,
                result_format='message'
            )

            if response.status_code != 200:
                return null_metrics

            raw = response.output.choices[0].message.content.strip()
            # Strip markdown fences if present
            if raw.startswith('```'):
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)

            parsed = json.loads(raw)

            # Validate and build metrics dict with expected keys
            metrics = {}
            for key in null_metrics:
                val = parsed.get(key)
                if val is not None:
                    try:
                        metrics[key] = round(float(val), 4)
                    except (ValueError, TypeError):
                        metrics[key] = None
                else:
                    metrics[key] = None

            return metrics

        except Exception:
            return null_metrics
    
    def extract_mda_section(self, text: str) -> str:
        """提取管理层讨论与分析部分
        
        Args:
            text: 年报文本
            
        Returns:
            MD&A 部分文本
        """
        # 常见 MD&A 标题
        mda_keywords = [
            '管理层讨论与分析',
            '董事会报告',
            '经营情况讨论',
            '公司业务概要',
            'MD&A',
        ]
        
        # 查找 MD&A 部分
        for keyword in mda_keywords:
            pattern = f'{keyword}[:：]?'
            match = re.search(pattern, text)
            if match:
                start = match.end()
                # 截取后续内容（约 5000 字）
                mda_text = text[start:start + 5000]
                return mda_text.strip()
        
        # 如果没找到，返回文本的前 10000 字
        return text[:10000]
    
    def analyze_with_llm(self, metrics: Dict, mda_text: str) -> Dict:
        """使用大模型进行分析
        
        Args:
            metrics: 财务指标
            mda_text: MD&A 文本
            
        Returns:
            分析结果
        """
        if not self.api_key:
            return {
                'error': 'API Key not configured',
                'suggestion': 'Please set DASHSCOPE_API_KEY environment variable'
            }
        
        # Build analysis prompt (in English)
        prompt = f"""You are a professional financial analyst. Please analyze the following corporate annual report data:

## Financial Metrics
{json.dumps(metrics, ensure_ascii=False, indent=2)}

## Management Discussion & Analysis (MD&A)
{mda_text[:3000]}

Please analyze from the following dimensions:

### 1. Financial Health
- Profitability Analysis
- Solvency Analysis
- Operational Efficiency Analysis

### 2. Business Development Prospects
- Industry Trend Assessment
- Company Competitive Advantages
- Potential Risk Factors

### 3. Investment Value Assessment
- Valuation Level Judgment
- Growth Space Analysis
- Investment Recommendations

Please use professional but accessible language, present in bullet points, with each point not exceeding 100 words. Respond in English."""

        try:
            response = Generation.call(
                model='qwen-plus',
                messages=[
                    {'role': 'system', 'content': 'You are a professional financial analyst specializing in corporate financial analysis and investment value assessment.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                stream=False,
                result_format='message'
            )
            
            if response.status_code == 200:
                analysis = response.output.choices[0].message.content
                return {
                    'success': True,
                    'analysis': analysis,
                    'metrics': metrics,
                    'mda_summary': mda_text[:500] + '...' if len(mda_text) > 500 else mda_text
                }
            else:
                return {
                    'error': f'API call failed: {response.message}',
                    'code': response.status_code
                }
                
        except Exception as e:
            return {
                'error': f'Analysis error: {str(e)}'
            }
    
    def analyze_pdf(self, pdf_path: str) -> Dict:
        """完整分析流程
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            完整分析结果
        """
        # 1. 提取文本
        text = self.extract_text_from_pdf(pdf_path)
        
        # 2. 提取财务指标
        metrics = self.extract_financial_metrics(text)
        
        # 3. 提取 MD&A 部分
        mda_text = self.extract_mda_section(text)
        
        # 4. 大模型分析
        analysis = self.analyze_with_llm(metrics, mda_text)
        
        return {
            'file': os.path.basename(pdf_path),
            'text_length': len(text),
            'metrics': metrics,
            'mda_extracted': len(mda_text),
            'analysis': analysis
        }


if __name__ == '__main__':
    # 测试
    analyzer = FinanceAnalyzer()
    print("分析器初始化成功")
