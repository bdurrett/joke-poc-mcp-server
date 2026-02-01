"""Dad Joke MCP Server - Main server implementation."""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)
from pythonjsonlogger import jsonlogger
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from starlette.requests import Request

from .config import settings


# Configure logging
def setup_logging() -> logging.Logger:
    """Set up structured logging with JSON format."""
    logger = logging.getLogger("dad_joke_mcp")
    logger.setLevel(settings.log_level_int)
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level_int)
    
    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger"
            }
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if settings.log_to_file:
        import os
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setLevel(settings.log_level_int)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()


# Dad joke styles and their characteristics
JOKE_STYLES = {
    "pun": "You are an expert comedian specializing in puns and wordplay. Create a clever pun-based dad joke about {topic} that plays on multiple meanings of words. The joke should be groan-worthy but clever, appropriate for all ages.",
    
    "wordplay": "You are a master of linguistic humor and wordplay. Create a dad joke about {topic} that uses creative word combinations, homophones, or unexpected word associations. Keep it family-friendly and punny.",
    
    "observational": "You are a comedian skilled in observational humor. Create a dad joke about {topic} that points out something funny or absurd about everyday situations. Make it relatable and wholesome.",
    
    "anti-humor": "You are a comedian who specializes in anti-humor and anti-jokes. Create a dad joke about {topic} that subverts expectations with an unexpectedly literal or mundane punchline. The humor comes from the lack of a traditional punchline.",
    
    "question-answer": "You are an expert at question-and-answer style dad jokes. Create a dad joke about {topic} in the classic 'Why did the X...? Because...' or 'What do you call...?' format. Make it punny and groan-inducing.",
    
    "one-liner": "You are a master of concise one-liner jokes. Create a short, punchy dad joke about {topic} that delivers the humor in a single sentence. Focus on wordplay or unexpected twists.",
    
    "knock-knock": "You are skilled at creating knock-knock jokes. Create a knock-knock joke about {topic} that uses clever wordplay. Follow the classic format: 'Knock knock. Who's there? [X]. [X] who? [Punchline].'",
    
    "classic": "You are an expert comedian skilled with puns and dad jokes. Create a joke about {topic} that is appropriate for a workplace. Use classic dad joke style with groan-worthy puns and wholesome humor.",
}


# Initialize MCP server
app = Server("dad-joke-mcp-server")


def log_request(request_id: str, request_type: str, data: Any) -> None:
    """Log incoming MCP request with full details."""
    if settings.log_requests:
        logger.info(
            "Incoming MCP request",
            extra={
                "request_id": request_id,
                "request_type": request_type,
                "request_data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


def log_response(request_id: str, request_type: str, response: Any) -> None:
    """Log outgoing MCP response with full details."""
    if settings.log_responses:
        logger.info(
            "Outgoing MCP response",
            extra={
                "request_id": request_id,
                "request_type": request_type,
                "response_data": response,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts."""
    request_id = str(uuid.uuid4())
    log_request(request_id, "list_prompts", {})
    
    prompts = [
        Prompt(
            name="dad_joke",
            description="Generate a dad joke prompt about any topic. Supports multiple joke styles.",
            arguments=[
                PromptArgument(
                    name="topic",
                    description="The topic or subject for the dad joke",
                    required=True,
                ),
                PromptArgument(
                    name="style",
                    description=f"The style of dad joke. Options: {', '.join(JOKE_STYLES.keys())}. Default: classic",
                    required=False,
                ),
            ],
        )
    ]
    
    log_response(request_id, "list_prompts", [p.model_dump() for p in prompts])
    logger.info(
        "Listed available prompts",
        extra={
            "request_id": request_id,
            "prompt_count": len(prompts),
            "prompt_names": [p.name for p in prompts],
        }
    )
    
    return prompts


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt with arguments."""
    request_id = str(uuid.uuid4())
    log_request(
        request_id,
        "get_prompt",
        {"name": name, "arguments": arguments}
    )
    
    if name != "dad_joke":
        error_msg = f"Unknown prompt: {name}"
        logger.error(
            error_msg,
            extra={
                "request_id": request_id,
                "prompt_name": name,
            }
        )
        raise ValueError(error_msg)
    
    if not arguments or "topic" not in arguments:
        error_msg = "Missing required argument: topic"
        logger.error(
            error_msg,
            extra={
                "request_id": request_id,
                "arguments": arguments,
            }
        )
        raise ValueError(error_msg)
    
    topic = arguments["topic"]
    style = arguments.get("style", "classic").lower()
    
    # Validate style
    if style not in JOKE_STYLES:
        logger.warning(
            f"Unknown joke style '{style}', falling back to 'classic'",
            extra={
                "request_id": request_id,
                "requested_style": style,
                "available_styles": list(JOKE_STYLES.keys()),
            }
        )
        style = "classic"
    
    # Generate the prompt text
    prompt_text = JOKE_STYLES[style].format(topic=topic)
    
    result = GetPromptResult(
        description=f"Dad joke prompt about {topic} in {style} style",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=prompt_text,
                ),
            )
        ],
    )
    
    log_response(request_id, "get_prompt", result.model_dump())
    logger.info(
        "Generated dad joke prompt",
        extra={
            "request_id": request_id,
            "topic": topic,
            "style": style,
            "prompt_length": len(prompt_text),
        }
    )
    
    return result


async def run_server():
    """Run the MCP server with SSE transport."""
    logger.info(
        "Starting Dad Joke MCP Server",
        extra={
            "version": "1.0.0",
            "host": settings.host,
            "port": settings.port,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "available_styles": list(JOKE_STYLES.keys()),
        }
    )
    
    # Create SSE transport
    sse = SseServerTransport("/messages")
    
    # Create Starlette app with SSE transport handlers
    from starlette.routing import Route
    
    async def handle_sse(request):
        """Handle SSE GET requests for server-to-client streaming."""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as streams:
            await app.run(
                streams[0],
                streams[1],
                app.create_initialization_options(),
            )
        return Response()
    
    async def handle_messages(request):
        """Handle POST requests for client-to-server messages."""
        await sse.handle_post_message(
            request.scope,
            request.receive,
            request._send,
        )
    
    starlette_app = Starlette(
        debug=settings.log_level == "DEBUG",
        routes=[
            Route("/messages", endpoint=handle_sse, methods=["GET"]),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )
    
    # Run with uvicorn
    import uvicorn
    
    logger.info(
        "Server started successfully",
        extra={
            "endpoint": f"http://{settings.host}:{settings.port}/messages",
            "status": "ready",
        }
    )
    
    config = uvicorn.Config(
        starlette_app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
    
    server = uvicorn.Server(config)
    await server.serve()



def main():
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(
            "Server error",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()
