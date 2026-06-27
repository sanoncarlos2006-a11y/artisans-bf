from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from html import escape

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import BACKEND_DIR, settings
from app.db.session import init_db
from app.routes import auth_router, businesses_router, health_router, ai_router, comments_router, search_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for the Annuaire Geolocalise des Artisans et Petits Commerces du Burkina Faso. "
        "It covers authentication, demo password reset, business ownership, publication and photo uploads."
    ),
    version="0.1.0",
    docs_url=None,
    lifespan=lifespan,
)

# Demo/local frontend ports. Wildcard is only used outside production-like environments.
local_envs = {"local", "demo", "development", "test"}
is_local_env = settings.APP_ENV.lower() in local_envs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if is_local_env else [],
    allow_credentials=False if is_local_env else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = BACKEND_DIR / settings.UPLOAD_DIR
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(businesses_router)
app.include_router(ai_router)
app.include_router(comments_router)
app.include_router(search_router)


@app.get("/docs", include_in_schema=False)
def local_docs() -> HTMLResponse:
    schema = app.openapi()
    rows: list[str] = []
    for path, methods in sorted(schema.get("paths", {}).items()):
        for method, details in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            tags = ", ".join(details.get("tags", []))
            summary = details.get("summary") or details.get("operationId") or ""
            rows.append(
                "<tr>"
                f"<td><span class='method method-{escape(method.lower())}'>{escape(method.upper())}</span></td>"
                f"<td><code>{escape(path)}</code></td>"
                f"<td>{escape(tags)}</td>"
                f"<td>{escape(summary)}</td>"
                "</tr>"
            )

    rows_html = "\n".join(rows)
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{escape(settings.APP_NAME)} - Local API Docs</title>
        <style>
          body {{
            margin: 0;
            font-family: Arial, sans-serif;
            color: #172033;
            background: #f5f7fb;
          }}
          header {{
            padding: 24px 32px;
            background: #ffffff;
            border-bottom: 1px solid #d9e0ea;
          }}
          main {{
            max-width: 1120px;
            margin: 0 auto;
            padding: 24px;
          }}
          h1 {{
            margin: 0 0 8px;
            font-size: 26px;
          }}
          p {{
            margin: 0;
            color: #526071;
          }}
          .links {{
            margin-top: 16px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
          }}
          a {{
            color: #0f5e9c;
            text-decoration: none;
            font-weight: 600;
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border: 1px solid #d9e0ea;
          }}
          th, td {{
            padding: 12px;
            border-bottom: 1px solid #e7ecf3;
            text-align: left;
            vertical-align: top;
          }}
          th {{
            font-size: 13px;
            color: #526071;
            background: #f8fafc;
          }}
          code {{
            font-family: Consolas, monospace;
          }}
          .method {{
            display: inline-block;
            min-width: 58px;
            padding: 4px 8px;
            border-radius: 4px;
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            text-align: center;
          }}
          .method-get {{ background: #1b7f4c; }}
          .method-post {{ background: #0f5e9c; }}
          .method-put {{ background: #9a5b13; }}
          .method-patch {{ background: #7a4eb0; }}
          .method-delete {{ background: #b42318; }}
        </style>
      </head>
      <body>
        <header>
          <h1>{escape(settings.APP_NAME)}</h1>
          <p>Local offline API route list. The backend is running.</p>
          <div class="links">
            <a href="/openapi.json">OpenAPI JSON</a>
            <a href="/businesses">Public businesses JSON</a>
          </div>
        </header>
        <main>
          <table>
            <thead>
              <tr>
                <th>Method</th>
                <th>Path</th>
                <th>Tags</th>
                <th>Operation</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
        </main>
      </body>
    </html>
    """
    return HTMLResponse(html)
