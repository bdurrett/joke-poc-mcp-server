# Dad Joke MCP Server 🎭

A Python-based MCP (Model Context Protocol) server that generates creative dad joke prompts. Connect your AI agent to this server and request dad jokes on any topic in various styles!

While this project was entirely vibe slopped, shoutout to [OrenGrinker's Dad Joke MCP Server](https://github.com/OrenGrinker/dad-jokes-mcp-server) for inspiration and possiobly examples for the LLMs.

## Features

- 🎪 **8 Joke Styles**: pun, wordplay, observational, anti-humor, question-answer, one-liner, knock-knock, and classic
- 🛠️ **MCP Tools**: `joke_styles` and `build_dad_joke_prompt` for automated prompt building
- 🌐 **Network Support**: Runs over SSE (Server-Sent Events) transport with standardized endpoints (`/sse` and `/messages`)
- 📝 **Extensive Logging**: Full request/response logging with structured JSON format
- 🐳 **Docker Ready**: Complete Docker configuration for standalone deployment

## How It Works

When you request a dad joke through an MCP client:

1. **User Request**: "Add a dad joke about fish"
2. **MCP Server Returns**: A prompt like "You are an expert comedian skilled with puns. Create a joke about fish that is appropriate for a workplace."
3. **AI Agent Executes**: The prompt and generates the actual joke
4. **Result**: "Why was the fish unsuccessful? He dropped out of school!"

## Installation

### Local Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd joke-poc-mcp-server
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the server**:
   ```bash
   python -m src.server
   ```

The server will start on `http://0.0.0.0:8000` by default.
- SSE Connection: `http://localhost:8000/sse` (or `/messages` for compatibility)
- Message Posting: `http://localhost:8000/messages`

### Docker Installation

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f dad-joke-mcp
   ```

3. **Stop the server**:
   ```bash
   docker-compose down
   ```

Alternatively, use Docker directly:

```bash
# Build the image
docker build -t dad-joke-mcp-server .

# Run the container
docker run -d -p 8000:8000 --name dad-joke-mcp dad-joke-mcp-server

# View logs
docker logs -f dad-joke-mcp
```

## Configuration

Configure the server using environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FORMAT` | `json` | Log format (json or text) |
| `LOG_FILE` | `logs/dad-joke-mcp.log` | Log file path |
| `LOG_TO_FILE` | `false` | Enable file logging |
| `LOG_REQUESTS` | `true` | Log incoming requests |
| `LOG_RESPONSES` | `true` | Log outgoing responses |

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "dad-joke": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Cline (VS Code Extension)

Add to your Cline MCP settings:

```json
{
  "mcpServers": {
    "dad-joke": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## Usage

### Prompts
Use the `dad_joke` prompt to generate a prompt for an LLM:
- Required: `topic`
- Optional: `style` (default: `classic`)

### Tools
The server provides tools for automated interaction:

1. **`joke_styles`**: Returns a list of all available joke styles.
   - *Arguments*: None

2. **`build_dad_joke_prompt`**: Programmatically generates a dad joke prompt.
   - *Arguments*: 
     - `topic` (string, required): The subject of the joke.
     - `style` (string, optional): The style of the joke.

Available styles:
- `pun` - Clever wordplay and multiple meanings
- `wordplay` - Creative word combinations and homophones
- `observational` - Funny observations about everyday situations
- `anti-humor` - Subverted expectations with literal punchlines
- `question-answer` - Classic "Why did..." or "What do you call..." format
- `one-liner` - Short, punchy single-sentence jokes
- `knock-knock` - Traditional knock-knock joke format
- `classic` - Traditional dad joke style (default)

## Examples

### Cursor
`build_dad_joke_prompt( football ) and use the output as a prompt and then append the result of that prompt to the test.txt file. Only append the result, oo not include the call to the tool or the parameters.`
Calls the tool and uses the output as a prompt

`append /dad-joke/dad_joke to the test.txt file`
Uses the prompt (the slash will trigger a dialog asking for the topic and style)


## Logging

The server provides extensive logging with full request/response details:

### JSON Format (Default)

```json
{
  "timestamp": "2026-02-01T20:24:00.123Z",
  "logger": "dad_joke_mcp",
  "level": "INFO",
  "message": "Generated dad joke prompt",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "topic": "fish",
  "style": "classic",
  "prompt_length": 145
}
```

### Text Format

Set `LOG_FORMAT=text` for human-readable logs:

```
2026-02-01 20:24:00,123 - dad_joke_mcp - INFO - Generated dad joke prompt
```

## Architecture

```
┌─────────────────┐
│   MCP Client    │
│ (Claude/Cursor) │
└────────┬────────┘
         │ SSE/HTTP
         ▼
┌─────────────────┐
│  Dad Joke MCP   │
│     Server      │
│                 │
│  ┌───────────┐  │
│  │ Prompts / │  │
│  │   Tools   │  │
│  │ Handlers  │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │  Logger   │  │
│  │ (JSON)    │  │
│  └───────────┘  │
└─────────────────┘
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
djmcp/
├── src/
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration management
│   └── server.py         # Main MCP server
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── pyproject.toml        # Project metadata
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment config
└── README.md            # This file
```

## Troubleshooting

### Server won't start

- Check if port 8000 is already in use: `lsof -i :8000`
- Verify Python version: `python --version` (requires 3.11+)
- Check logs for error messages

### MCP client can't connect

- Ensure server is running: `curl http://localhost:8000/sse`
- Verify firewall settings allow connections on port 8000
- Check client configuration matches server host/port (ensure using `/sse` for GET)

### No logs appearing

- Set `LOG_LEVEL=DEBUG` for verbose logging
- Verify `LOG_REQUESTS=true` and `LOG_RESPONSES=true`
- Check console output or log file if `LOG_TO_FILE=true`

## License

MIT License - feel free to use and modify as needed!

## Contributing

Contributions welcome! Feel free to:
- Add new joke styles
- Improve prompt templates
- Enhance logging capabilities
- Add tests and documentation

---

Made with ❤️ and terrible puns
