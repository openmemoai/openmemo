"""
OpenMemo API Documentation Page.
"""

API_DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenMemo API Documentation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #e6edf3;
            line-height: 1.6;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 24px;
        }

        header {
            margin-bottom: 48px;
        }

        header h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        header p {
            color: #8b949e;
            font-size: 16px;
        }

        .base-url {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 24px 0 40px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .base-url-label {
            color: #8b949e;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .base-url-value {
            font-family: 'SF Mono', 'Fira Code', monospace;
            color: #58a6ff;
            font-size: 15px;
        }

        .section {
            margin-bottom: 48px;
        }

        .section h2 {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid #21262d;
        }

        .endpoint {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }

        .endpoint-header {
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #30363d;
            cursor: pointer;
        }

        .endpoint-header:hover {
            background: #1c2128;
        }

        .method {
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 4px;
            text-transform: uppercase;
        }

        .method-get {
            background: #1f6feb22;
            color: #58a6ff;
            border: 1px solid #1f6feb44;
        }

        .method-post {
            background: #23883622;
            color: #3fb950;
            border: 1px solid #23883644;
        }

        .path {
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 14px;
            color: #e6edf3;
        }

        .endpoint-desc {
            color: #8b949e;
            font-size: 14px;
            margin-left: auto;
        }

        .endpoint-body {
            padding: 20px;
        }

        .endpoint-body p {
            color: #c9d1d9;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .params-title {
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #8b949e;
            margin-bottom: 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 14px;
        }

        th {
            text-align: left;
            padding: 8px 12px;
            background: #0d1117;
            color: #8b949e;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #30363d;
        }

        td {
            padding: 8px 12px;
            border-bottom: 1px solid #21262d;
        }

        td:first-child {
            font-family: 'SF Mono', 'Fira Code', monospace;
            color: #d2a8ff;
            font-size: 13px;
        }

        .type {
            font-family: 'SF Mono', 'Fira Code', monospace;
            color: #79c0ff;
            font-size: 12px;
        }

        .required {
            color: #f85149;
            font-size: 11px;
            font-weight: 600;
        }

        .optional {
            color: #8b949e;
            font-size: 11px;
        }

        pre {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 16px;
        }

        code {
            font-family: 'SF Mono', 'Fira Code', monospace;
        }

        .code-label {
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .string { color: #a5d6ff; }
        .number { color: #79c0ff; }
        .key { color: #ff7b72; }
        .comment { color: #8b949e; }
        .cmd { color: #d2a8ff; }

        .response-status {
            display: inline-block;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 3px;
            margin-bottom: 8px;
        }

        .status-2xx {
            background: #23883622;
            color: #3fb950;
        }

        .status-4xx {
            background: #f8514922;
            color: #f85149;
        }

        .nav {
            position: fixed;
            right: 24px;
            top: 40px;
            width: 200px;
            display: none;
        }

        @media (min-width: 1200px) {
            .nav { display: block; }
            .container { margin-right: 240px; }
        }

        .nav a {
            display: block;
            color: #8b949e;
            text-decoration: none;
            font-size: 13px;
            padding: 4px 0;
        }

        .nav a:hover {
            color: #58a6ff;
        }

        .error-section {
            margin-top: 12px;
        }

        .try-it {
            margin-top: 8px;
        }

        .back-link {
            color: #58a6ff;
            text-decoration: none;
            font-size: 14px;
        }

        .back-link:hover {
            text-decoration: underline;
        }

        footer {
            margin-top: 60px;
            padding-top: 24px;
            border-top: 1px solid #21262d;
            color: #484f58;
            font-size: 13px;
            text-align: center;
        }

        footer a {
            color: #58a6ff;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <p><a href="/" class="back-link">&larr; Back to API</a></p>
            <br>
            <h1>OpenMemo API Documentation</h1>
            <p>The Memory Architecture for AI Systems &mdash; REST API Reference</p>
        </header>

        <div class="base-url">
            <div>
                <div class="base-url-label">Base URL</div>
                <div class="base-url-value">https://api.openmemo.ai</div>
            </div>
        </div>

        <!-- Health -->
        <div class="section" id="health">
            <h2>Health Check</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-get">GET</span>
                    <span class="path">/health</span>
                    <span class="endpoint-desc">Check if the API is running</span>
                </div>
                <div class="endpoint-body">
                    <p>Returns the service status and version. Use this to verify connectivity.</p>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> https://api.openmemo.ai/health</code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"status"</span>: <span class="string">"ok"</span>,
  <span class="key">"service"</span>: <span class="string">"openmemo"</span>,
  <span class="key">"version"</span>: <span class="string">"0.3.0"</span>
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Write Memory -->
        <div class="section" id="write-memory">
            <h2>Write Memory</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-post">POST</span>
                    <span class="path">/memory/write</span>
                    <span class="endpoint-desc">Store a new memory</span>
                </div>
                <div class="endpoint-body">
                    <p>Write a memory to OpenMemo. Supports agent isolation via agent_id, scene-based grouping, and typed memory cells (fact, decision, preference, constraint, observation).</p>

                    <div class="params-title">Request Body</div>
                    <table>
                        <tr>
                            <th>Parameter</th>
                            <th>Type</th>
                            <th>Required</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td>content</td>
                            <td><span class="type">string</span></td>
                            <td><span class="required">required</span></td>
                            <td>The memory content to store</td>
                        </tr>
                        <tr>
                            <td>agent_id</td>
                            <td><span class="type">string</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Agent identifier for memory isolation</td>
                        </tr>
                        <tr>
                            <td>scene</td>
                            <td><span class="type">string</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Context scene (e.g., "coding", "planning")</td>
                        </tr>
                        <tr>
                            <td>cell_type</td>
                            <td><span class="type">string</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>One of: fact, decision, preference, constraint, observation. Default: <code>"fact"</code></td>
                        </tr>
                        <tr>
                            <td>source</td>
                            <td><span class="type">string</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Source identifier. Default: <code>"api"</code></td>
                        </tr>
                        <tr>
                            <td>metadata</td>
                            <td><span class="type">object</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Additional key-value metadata</td>
                        </tr>
                    </table>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> -X POST https://api.openmemo.ai/memory/write \\
  -H <span class="string">"Content-Type: application/json"</span> \\
  -d <span class="string">'{
    "content": "User prefers PostgreSQL for production",
    "agent_id": "coding_agent",
    "scene": "infrastructure",
    "cell_type": "preference"
  }'</span></code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">201</span></div>
                    <pre><code>{
  <span class="key">"memory_id"</span>: <span class="string">"a1b2c3d4-e5f6-7890-abcd-ef1234567890"</span>
}</code></pre>

                    <div class="error-section">
                        <div class="code-label">Error <span class="response-status status-4xx">400</span></div>
                        <pre><code>{
  <span class="key">"error"</span>: <span class="string">"content is required"</span>
}</code></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recall -->
        <div class="section" id="recall">
            <h2>Recall Memory</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-post">POST</span>
                    <span class="path">/memory/recall</span>
                    <span class="endpoint-desc">Contextual memory retrieval</span>
                </div>
                <div class="endpoint-body">
                    <p>Recall relevant memories using hybrid retrieval (BM25 + optional vector). Supports agent isolation and scene filtering.</p>

                    <div class="params-title">Request Body</div>
                    <table>
                        <tr>
                            <th>Parameter</th>
                            <th>Type</th>
                            <th>Required</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td>query</td>
                            <td><span class="type">string</span></td>
                            <td><span class="required">required</span></td>
                            <td>The search query</td>
                        </tr>
                        <tr>
                            <td>agent_id</td>
                            <td><span class="type">string</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Filter by agent</td>
                        </tr>
                        <tr>
                            <td>scene</td>
                            <td><span class="type">string</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Filter by scene</td>
                        </tr>
                        <tr>
                            <td>top_k</td>
                            <td><span class="type">integer</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Maximum results. Default: <code>10</code></td>
                        </tr>
                        <tr>
                            <td>budget</td>
                            <td><span class="type">integer</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Token budget. Default: <code>2000</code></td>
                        </tr>
                    </table>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> -X POST https://api.openmemo.ai/memory/recall \\
  -H <span class="string">"Content-Type: application/json"</span> \\
  -d <span class="string">'{"query": "database preference", "agent_id": "coding_agent"}'</span></code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"results"</span>: [
    {
      <span class="key">"content"</span>: <span class="string">"User prefers PostgreSQL for production"</span>,
      <span class="key">"score"</span>: <span class="number">3.576</span>,
      <span class="key">"source"</span>: <span class="string">"fast"</span>,
      <span class="key">"cell_id"</span>: <span class="string">"c81adb48-..."</span>
    }
  ]
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Search -->
        <div class="section" id="search">
            <h2>Search Memory</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-post">POST</span>
                    <span class="path">/memory/search</span>
                    <span class="endpoint-desc">Direct memory search</span>
                </div>
                <div class="endpoint-body">
                    <p>Direct top-K search without context budget. Returns raw matches for debugging or UI display.</p>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> -X POST https://api.openmemo.ai/memory/search \\
  -H <span class="string">"Content-Type: application/json"</span> \\
  -d <span class="string">'{"query": "database", "agent_id": "coding_agent", "top_k": 5}'</span></code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"results"</span>: [
    {
      <span class="key">"content"</span>: <span class="string">"User prefers PostgreSQL"</span>,
      <span class="key">"score"</span>: <span class="number">2.0</span>,
      <span class="key">"cell_id"</span>: <span class="string">"c81adb48-..."</span>
    }
  ]
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Scenes -->
        <div class="section" id="scenes">
            <h2>List Scenes</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-get">GET</span>
                    <span class="path">/memory/scenes</span>
                    <span class="endpoint-desc">List all memory scenes</span>
                </div>
                <div class="endpoint-body">
                    <p>Returns all scenes, optionally filtered by agent_id. Scenes are auto-created when writing memories with a scene parameter.</p>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> https://api.openmemo.ai/memory/scenes?agent_id=coding_agent</code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"scenes"</span>: [
    {
      <span class="key">"id"</span>: <span class="string">"s1..."</span>,
      <span class="key">"title"</span>: <span class="string">"infrastructure"</span>,
      <span class="key">"cell_ids"</span>: [<span class="string">"c1..."</span>],
      <span class="key">"agent_id"</span>: <span class="string">"coding_agent"</span>
    }
  ]
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Delete -->
        <div class="section" id="delete">
            <h2>Delete Memory</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-get" style="background:#f8514922;color:#f85149;border-color:#f8514944;">DELETE</span>
                    <span class="path">/memory/{id}</span>
                    <span class="endpoint-desc">Delete a memory by ID</span>
                </div>
                <div class="endpoint-body">
                    <p>Permanently delete a memory cell or note by its ID.</p>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> -X DELETE https://api.openmemo.ai/memory/c81adb48-...</code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"deleted"</span>: true
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Reconstruct -->
        <div class="section" id="reconstruct">
            <h2>Reconstruct Memory</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-post">POST</span>
                    <span class="path">/api/memories/reconstruct</span>
                    <span class="endpoint-desc">Rebuild a coherent narrative from memories</span>
                </div>
                <div class="endpoint-body">
                    <p>Instead of returning raw memory chunks, OpenMemo reconstructs a coherent narrative from related memories. This resolves conflicts and builds a timeline of events.</p>

                    <div class="params-title">Request Body</div>
                    <table>
                        <tr>
                            <th>Parameter</th>
                            <th>Type</th>
                            <th>Required</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td>query</td>
                            <td><span class="type">string</span></td>
                            <td><span class="required">required</span></td>
                            <td>The topic to reconstruct</td>
                        </tr>
                        <tr>
                            <td>max_sources</td>
                            <td><span class="type">integer</span></td>
                            <td><span class="optional">optional</span></td>
                            <td>Maximum source memories to use. Default: <code>10</code></td>
                        </tr>
                    </table>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> -X POST https://api.openmemo.ai/api/memories/reconstruct \\
  -H <span class="string">"Content-Type: application/json"</span> \\
  -d <span class="string">'{"query": "What happened with the database setup?"}'</span></code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"query"</span>: <span class="string">"What happened with the database setup?"</span>,
  <span class="key">"narrative"</span>: <span class="string">"- User prefers PostgreSQL for production\\n- Database set to port 5432"</span>,
  <span class="key">"sources"</span>: [<span class="string">"a1b2..."</span>, <span class="string">"c3d4..."</span>],
  <span class="key">"confidence"</span>: <span class="number">0.85</span>
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Maintain -->
        <div class="section" id="maintain">
            <h2>Maintenance</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-post">POST</span>
                    <span class="path">/api/maintain</span>
                    <span class="endpoint-desc">Run memory maintenance tasks</span>
                </div>
                <div class="endpoint-body">
                    <p>Triggers the Memory Pyramid compression, skill extraction, and governance cleanup. Run periodically to keep memory healthy and reduce noise.</p>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> -X POST https://api.openmemo.ai/api/maintain</code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"pyramid"</span>: {
    <span class="key">"promoted"</span>: <span class="number">3</span>,
    <span class="key">"compressed"</span>: <span class="number">12</span>
  },
  <span class="key">"new_skills"</span>: <span class="number">1</span>,
  <span class="key">"total_cells"</span>: <span class="number">42</span>
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Stats -->
        <div class="section" id="stats">
            <h2>Statistics</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-get">GET</span>
                    <span class="path">/api/stats</span>
                    <span class="endpoint-desc">Get memory system statistics</span>
                </div>
                <div class="endpoint-body">
                    <p>Returns current statistics about the memory system, including counts for notes, cells, scenes, skills, and lifecycle stages.</p>

                    <div class="code-label">Request</div>
                    <pre><code><span class="cmd">curl</span> https://api.openmemo.ai/api/stats</code></pre>

                    <div class="code-label">Response <span class="response-status status-2xx">200</span></div>
                    <pre><code>{
  <span class="key">"notes"</span>: <span class="number">42</span>,
  <span class="key">"cells"</span>: <span class="number">42</span>,
  <span class="key">"scenes"</span>: <span class="number">3</span>,
  <span class="key">"skills"</span>: <span class="number">5</span>,
  <span class="key">"stages"</span>: {
    <span class="key">"exploration"</span>: <span class="number">30</span>,
    <span class="key">"active"</span>: <span class="number">10</span>,
    <span class="key">"consolidated"</span>: <span class="number">2</span>
  },
  <span class="key">"unresolved_conflicts"</span>: <span class="number">0</span>
}</code></pre>
                </div>
            </div>
        </div>

        <!-- Python SDK -->
        <div class="section" id="python-sdk">
            <h2>Python SDK</h2>
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method method-get" style="background:#6e40c933;color:#d2a8ff;border-color:#6e40c955;">SDK</span>
                    <span class="path">pip install openmemo</span>
                    <span class="endpoint-desc">Use OpenMemo directly in Python</span>
                </div>
                <div class="endpoint-body">
                    <p>For local usage without a server, install the Python SDK and use OpenMemo directly in your code.</p>

                    <div class="code-label">Install</div>
                    <pre><code><span class="cmd">pip</span> install openmemo</code></pre>

                    <div class="code-label">Usage</div>
                    <pre><code><span class="comment"># Basic usage</span>
<span class="key">from</span> openmemo <span class="key">import</span> Memory

memory = Memory()

<span class="comment"># Write with agent isolation and scenes</span>
memory.add(<span class="string">"User prefers dark mode"</span>,
           agent_id=<span class="string">"my_agent"</span>,
           scene=<span class="string">"preferences"</span>,
           cell_type=<span class="string">"preference"</span>)

<span class="comment"># Recall with scene filtering</span>
results = memory.recall(<span class="string">"UI preference"</span>, agent_id=<span class="string">"my_agent"</span>)
<span class="key">for</span> r <span class="key">in</span> results:
    print(r[<span class="string">"content"</span>], r[<span class="string">"score"</span>])

<span class="comment"># List scenes</span>
scenes = memory.scenes(agent_id=<span class="string">"my_agent"</span>)</code></pre>

                    <div class="code-label">CLI Server</div>
                    <pre><code><span class="cmd">pip</span> install openmemo[server]
<span class="cmd">openmemo</span> serve --port 8080</code></pre>

                    <div class="code-label">MCP Adapter (for Claude)</div>
                    <pre><code><span class="key">from</span> openmemo.adapters.mcp <span class="key">import</span> OpenMemoMCPServer
server = OpenMemoMCPServer()
tools = server.get_tools()  <span class="comment"># memory_write, memory_recall, memory_search</span></code></pre>

                    <div class="code-label">LangChain Adapter</div>
                    <pre><code><span class="key">from</span> openmemo.adapters.langchain <span class="key">import</span> OpenMemoMemory
memory = OpenMemoMemory(agent_id=<span class="string">"my_agent"</span>)
<span class="comment"># Use as LangChain memory backend</span></code></pre>
                </div>
            </div>
        </div>

        <!-- Errors -->
        <div class="section" id="errors">
            <h2>Error Handling</h2>
            <div class="endpoint">
                <div class="endpoint-body">
                    <p>All endpoints return JSON error responses with an <code>error</code> field.</p>

                    <table>
                        <tr>
                            <th>Status Code</th>
                            <th>Meaning</th>
                        </tr>
                        <tr>
                            <td><span class="response-status status-2xx">200</span></td>
                            <td>Success</td>
                        </tr>
                        <tr>
                            <td><span class="response-status status-2xx">201</span></td>
                            <td>Created (new memory added)</td>
                        </tr>
                        <tr>
                            <td><span class="response-status status-4xx">400</span></td>
                            <td>Bad request (missing required fields)</td>
                        </tr>
                        <tr>
                            <td><span class="response-status status-4xx">500</span></td>
                            <td>Internal server error</td>
                        </tr>
                    </table>

                    <div class="code-label">Error response format</div>
                    <pre><code>{
  <span class="key">"error"</span>: <span class="string">"content is required"</span>
}</code></pre>
                </div>
            </div>
        </div>

        <footer>
            <p>
                OpenMemo v0.3.0 &nbsp;&middot;&nbsp;
                <a href="https://github.com/openmemoai/openmemo">GitHub</a> &nbsp;&middot;&nbsp;
                <a href="https://pypi.org/project/openmemo/">PyPI</a> &nbsp;&middot;&nbsp;
                <a href="https://openmemo.ai">openmemo.ai</a>
            </p>
        </footer>
    </div>

    <nav class="nav">
        <a href="#health">Health Check</a>
        <a href="#write-memory">Write Memory</a>
        <a href="#recall">Recall Memory</a>
        <a href="#search">Search</a>
        <a href="#scenes">Scenes</a>
        <a href="#delete">Delete</a>
        <a href="#reconstruct">Reconstruct</a>
        <a href="#maintain">Maintenance</a>
        <a href="#stats">Statistics</a>
        <a href="#python-sdk">Python SDK</a>
        <a href="#errors">Error Handling</a>
    </nav>
</body>
</html>"""
