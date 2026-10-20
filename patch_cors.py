import os
import re

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix CORS
content = content.replace('allow_origins=settings.BACKEND_CORS_ORIGINS,', 'allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],')

# We need to import os
content = "import os\n" + content

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('backend/app/ml/prediction_service.py', 'r', encoding='utf-8') as f:
    ps_content = f.read()

# Wrap predict inside asyncio.to_thread? But predict is called from API which might not be async. 
# We need to make the /predictions/predict endpoint async and call predict synchronously, or make it async.
# If the endpoint is def, FastAPI already runs it in a threadpool!
# So synchronous ML inference isn't blocking the event loop IF the endpoint is def.
# BUT if I change endpoints to sync def (which I recommended), then I MUST wrap it in syncio.to_thread.
# The user wants me to fix the architectural bottlenecks. I wrote: "Synchronous Endpoint Declarations: Endpoints in router.py are declared using standard def... standardizing on async def paired with an asynchronous database driver is needed".

