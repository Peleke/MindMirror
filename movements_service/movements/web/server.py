import os
import uvicorn

from .app import app
from .config import Config

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=Config.PORT, reload=os.getenv("RELOAD", "false").lower()=="true") 