#!/usr/bin/env python
"""
FastAPI Server Launcher
Khởi động server với uvicorn
"""

import uvicorn
import sys

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                 Starting FastAPI Server                        ║
║                                                                ║
║  Server: http://127.0.0.1:8000                                ║
║  API Docs: http://127.0.0.1:8000/api/docs                     ║
║  Chatbot API: http://127.0.0.1:8000/api/chatbot               ║
║                                                                ║
║  Press CTRL+C to stop                                         ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
