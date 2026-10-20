import os

with open('backend/app/api/router.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "auth" not in content:
    content = content.replace(
        "from app.api.v1 import predictions, feedback, registry, retraining, deployments, drift, metrics",
        "from app.api.v1 import predictions, feedback, registry, retraining, deployments, drift, metrics, auth"
    )
    content = content.replace(
        "api_router.include_router(predictions.router, prefix=\"/predictions\", tags=[\"predictions\"])",
        "api_router.include_router(auth.router, prefix=\"/auth\", tags=[\"auth\"])\napi_router.include_router(predictions.router, prefix=\"/predictions\", tags=[\"predictions\"])"
    )
    with open('backend/app/api/router.py', 'w', encoding='utf-8') as f:
        f.write(content)
