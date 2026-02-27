# Version History

## v1.0.0 (2026-02-27) - Initial Release

**Status:** ✅ Production Ready

### Features
- 📤 PDF annual report upload (drag & drop support)
- 📊 Automatic financial metrics extraction
  - Revenue, Net Profit, Total Assets, Total Liabilities
  - Operating Cash Flow, Net Assets
  - Gross Margin, Net Profit Margin, ROE, Debt-to-Asset Ratio
- 🤖 AI-powered analysis using Qwen LLM (qwen-max)
- 📈 Interactive charts with Chart.js
- 🌐 Full English UI and analysis output

### Tech Stack
- **Backend:** Flask + Gunicorn (production WSGI server)
- **Frontend:** TailwindCSS + Chart.js
- **AI:** Alibaba Cloud DashScope API (Qwen-max model)
- **PDF Processing:** PyMuPDF

### Deployment
- **Development:** `python app.py`
- **Production:** `gunicorn --workers 3 --threads 2 --timeout 120 --bind 0.0.0.0:5000 app:app`
- **Quick Restart:** `./restart.sh`

### Configuration
1. Set API Key in `.env` file:
   ```
   DASHSCOPE_API_KEY=sk-your-api-key-here
   ```

2. Open firewall port 5000 for external access

### Known Issues
- None currently

### Future Enhancements
- [ ] Multi-year comparison
- [ ] Industry benchmark comparison
- [ ] Export analysis as PDF report
- [ ] User authentication and history
- [ ] Support for Excel/CSV formats
- [ ] Additional language support

---

**Repository:** `/root/.openclaw/workspace/corp-finance-analyzer`
**Branch:** main
**Latest Commit:** See `git log` for details
