"""
Run FastAPI server
"""

import uvicorn
import os

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"Starting Stock Research Tool API on {host}:{port}")
    print(f"\n{'='*60}")
    print("API Server is running!")
    print(f"{'='*60}")
    print(f"Access the API at:")
    print(f"  - Local: http://localhost:{port}")
    print(f"  - Network: http://127.0.0.1:{port}")
    print(f"\nAPI Documentation:")
    print(f"  - Swagger UI: http://localhost:{port}/docs")
    print(f"  - ReDoc: http://localhost:{port}/redoc")
    print(f"\nFrontend:")
    print(f"  - Frontend: http://localhost:{port}/")
    print(f"  - API Info: http://localhost:{port}/api")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

