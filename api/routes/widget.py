import os
from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

router = APIRouter()

WIDGET_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "widget"
)


@router.get("/widget/chatbot.js")
async def serve_widget_js():
    path = os.path.join(WIDGET_DIR, "src", "chatbot.js")
    if not os.path.exists(path):
        return Response(content="// Widget not found", media_type="application/javascript")
    return FileResponse(path, media_type="application/javascript")


@router.get("/widget/chatbot.min.js")
async def serve_widget_min_js():
    min_path = os.path.join(WIDGET_DIR, "dist", "chatbot.min.js")
    src_path = os.path.join(WIDGET_DIR, "src", "chatbot.js")
    path = min_path if os.path.exists(min_path) else src_path
    if not os.path.exists(path):
        return Response(content="// Widget not found", media_type="application/javascript")
    return FileResponse(
        path,
        media_type="application/javascript",
        headers={"Cache-Control": "public, max-age=300"},
    )


@router.get("/widget/demo")
async def widget_demo():
    demo_path = os.path.join(WIDGET_DIR, "index.html")
    if not os.path.exists(demo_path):
        return Response(content="<h1>Demo not found</h1>", media_type="text/html")
    return FileResponse(demo_path, media_type="text/html")
