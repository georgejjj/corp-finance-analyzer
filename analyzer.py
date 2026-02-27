"""
公司金融年报分析引擎
支持 PDF 解析、财务指标提取、MD&A 文本分析
"""

import fitz  # PyMuPDF
import re
import json
import dashscope
from dashscope import Generation
from typing import Dict, List, Optional
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
    
    def extract_financial_metrics(self, text: str) -> Dict:
        """提取财务指标
        
        Args:
            text: 年报文本
            
        Returns:
            财务指标字典
        """
        metrics = {
            'revenue': None,  # 营业收入
            'net_profit': None,  # 净利润
            'total_assets': None,  # 总资产
            'total_liabilities': None,  # 总负债
            'operating_cash_flow': None,  # 经营现金流
            'net_assets': None,  # 净资产
            'roe': None,  # 净资产收益率
            'gross_margin': None,  # 毛利率
            'debt_ratio': None,  # 资产负债率
            'profit_margin': None,  # 净利率
        }
        
        # 提取函数 - 支持表格格式（数字在文字下一行）
        def extract_table_value(key_pattern, text, unit_multiplier=1.0):
            # 先找关键字位置
            idx = re.search(key_pattern, text)
            if idx:
                # 从关键字位置往后找数字
                start = idx.end()
                snippet = text[start:start+200]
                # 匹配数字（支持千分位逗号）
                num_match = re.search(r'([\d,]+\.?\d*)', snippet)
                if num_match:
                    value = num_match.group(1).replace(',', '')
                    return float(value) * unit_multiplier
            return None
        
        # 千元单位需要除以 10000 转换为亿元（注意 PDF 提取后括号可能是全角或半角）
        metrics['revenue'] = extract_table_value(r'营业收入.*千元', text, unit_multiplier=0.0001)
        metrics['net_profit'] = extract_table_value(r'归属于上市公司股东的净利润.*千元', text, unit_multiplier=0.0001)
        metrics['operating_cash_flow'] = extract_table_value(r'经营活动产生的现金流量净额.*千元', text, unit_multiplier=0.0001)
        
        # 传统正则匹配（备用）- 支持多种格式
        if not metrics['revenue']:
            revenue_patterns = [
                r'营业总收入 [：:]\s*([\d,\.]+)\s*(?:亿|亿元)',
                r'营业收入 [：:]\s*([\d,\.]+)\s*(?:亿|亿元)',
                r'营业收入\s*([\d,\.]+)',  # 简化版
            ]
            for pattern in revenue_patterns:
                match = re.search(pattern, text)
                if match:
                    val = float(match.group(1).replace(',', ''))
                    # 如果数字很大（>10000），可能是千元单位
                    if val > 10000:
                        val = val * 0.0001
                    metrics['revenue'] = val
                    break
        
        if not metrics['net_profit']:
            profit_patterns = [
                r'净利润 [：:]\s*([\d,\.]+)\s*(?:亿|亿元)',
                r'归母净利润 [：:]\s*([\d,\.]+)\s*(?:亿|亿元)',
                r'净利润\s*([\d,\.]+)',  # 简化版
            ]
            for pattern in profit_patterns:
                match = re.search(pattern, text)
                if match:
                    val = float(match.group(1).replace(',', ''))
                    if val > 10000:
                        val = val * 0.0001
                    metrics['net_profit'] = val
                    break
        
        if not metrics['operating_cash_flow']:
            cashflow_patterns = [
                r'经营活动现金流.*?\s*([\d,\.]+)',
            ]
            for pattern in cashflow_patterns:
                match = re.search(pattern, text)
                if match:
                    val = float(match.group(1).replace(',', ''))
                    if val > 10000:
                        val = val * 0.0001
                    metrics['operating_cash_flow'] = val
                    break
        
        # 提取总资产、总负债、净资产、毛利率等
        # 使用更灵活的正则，支持数字在下一行
        
        # 资产总额
        assets_match = re.search(r'资产总额.*?千元.*?\n\s*([\d,]+)', text)
        if assets_match:
            metrics['total_assets'] = float(assets_match.group(1).replace(',', '')) * 0.0001
        
        # 负债合计
        liabilities_match = re.search(r'负债合计.*?千元.*?\n\s*([\d,]+)', text)
        if liabilities_match:
            metrics['total_liabilities'] = float(liabilities_match.group(1).replace(',', '')) * 0.0001
        
        # 净资产
        equity_match = re.search(r'归属于上市公司股东的净资产.*?\n\s*([\d,]+)', text)
        if equity_match:
            metrics['net_assets'] = float(equity_match.group(1).replace(',', '')) * 0.0001
        
        # 毛利率（百分比）- 支持表格格式，数据可能在多行之后
        # 使用 [\s\S] 匹配包括换行在内的所有字符
        margin_search = re.search(r'毛利率[\s\S]{50,500}?([\d\.]+)\s*%', text)
        if margin_search:
            metrics['gross_margin'] = float(margin_search.group(1))
        
        # 如果找不到负债合计，用 资产 - 净资产 推算
        if metrics['total_assets'] and metrics['net_assets'] and not metrics['total_liabilities']:
            metrics['total_liabilities'] = round(metrics['total_assets'] - metrics['net_assets'], 2)
        
        # 计算资产负债率
        if metrics['total_assets'] and metrics['total_liabilities']:
            metrics['debt_ratio'] = round(
                metrics['total_liabilities'] / metrics['total_assets'] * 100, 2
            )
        
        # 计算资产负债率
        if metrics['total_assets'] and metrics['total_liabilities']:
            metrics['debt_ratio'] = round(
                metrics['total_liabilities'] / metrics['total_assets'] * 100, 2
            )
        
        # 计算 ROE（净资产收益率）
        if metrics['net_assets'] and metrics['net_profit']:
            metrics['roe'] = round(
                metrics['net_profit'] / metrics['net_assets'] * 100, 2
            )
        
        # 计算衍生指标
        if metrics['revenue'] and metrics['net_profit']:
            metrics['profit_margin'] = round(
                metrics['net_profit'] / metrics['revenue'] * 100, 2
            )
        
        return metrics
    
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
            # Use qwen-max model
            response = Generation.call(
                model='qwen-max',
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
