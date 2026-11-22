#!/usr/bin/env python3
"""Portable Stdio MCP Server wrapping libarcane_nexus.so (Arcane-Nexus SDK)."""
import ctypes
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_PATH = os.environ.get("ARCANE_NEXUS_LIB", os.path.join(ROOT, "lib", "libarcane_nexus.so"))
SNAP_PATH = os.environ.get("ARCANE_NEXUS_SNAPSHOT", "/tmp/arcane_nexus_mcp_crash.bin")

lib = ctypes.CDLL(LIB_PATH)
lib.InitializeSDK.argtypes = [ctypes.c_char_p]
lib.InitializeSDK.restype = ctypes.c_int
lib.ShutdownSDK.argtypes = []
lib.RecallMemory.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)
]
lib.RecallMemory.restype = ctypes.c_int
lib.StoreMemory.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.StoreMemory.restype = ctypes.c_int
lib.ProcessBatchRelay.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
]
lib.ProcessBatchRelay.restype = ctypes.c_int
lib.DeleteMemory.argtypes = [ctypes.c_char_p]
lib.DeleteMemory.restype = ctypes.c_int


def _init_sdk_quietly() -> int:
    saved_fd = os.dup(1)
    try:
        os.dup2(2, 1)
        return lib.InitializeSDK(SNAP_PATH.encode("utf-8"))
    finally:
        os.dup2(saved_fd, 1)
        os.close(saved_fd)


TOOLS = [
    {
        "name": "recall_memory",
        "description": "Arcane-Nexus Memory-First recall. Always query before answering from model weights.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or topic keywords"},
                "layer": {"type": "string", "description": "Optional layer filter (empty for all)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "store_memory",
        "description": "Store or overwrite a neuron memory node in Arcane-Nexus (in-RAM Zero-Disk).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_key": {"type": "string", "description": "Unique neuron key"},
                "content": {"type": "string", "description": "Distilled memory content"},
                "layer": {"type": "string", "description": "Memory layer/category (default: general)"},
            },
            "required": ["node_key", "content"],
        },
    },
    {
        "name": "process_batch_relay",
        "description": "Process a long-task chunk (up to 10K tokens) via PAUSE/RESUME pool, store, zero-out, and return clean relay context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_key": {"type": "string", "description": "Task neuron identifier"},
                "chunk": {"type": "string", "description": "Batch content to internalize"},
                "layer": {"type": "string", "description": "Layer name (default: task_flow)"},
            },
            "required": ["task_key", "chunk"],
        },
    },
    {
        "name": "delete_memory",
        "description": "Clear and recycle a mutable neuron slot for reuse (Node 0 factory rules are protected).",
        "inputSchema": {
            "type": "object",
            "properties": {"node_key": {"type": "string", "description": "Neuron key to clear"}},
            "required": ["node_key"],
        },
    },
]


def _call_tool(name: str, args: dict) -> str:
    buf = ctypes.create_string_buffer(16384)
    if name == "recall_memory":
        q = str(args.get("query", "")).encode("utf-8")
        layer = str(args.get("layer", "")).encode("utf-8")
        hit = ctypes.c_int(0)
        lib.RecallMemory(q, layer, buf, len(buf), ctypes.byref(hit))
        txt = buf.value.decode("utf-8", errors="replace")
        return f"[hit={hit.value}]\n{txt}" if txt else f"[hit={hit.value}] (no match)"
    if name == "store_memory":
        k = str(args.get("node_key", "")).encode("utf-8")
        c = str(args.get("content", "")).encode("utf-8")
        l = str(args.get("layer", "general")).encode("utf-8")
        return "STORED_OK" if lib.StoreMemory(k, l, c, 0) == 1 else "STORE_DENIED"
    if name == "process_batch_relay":
        tk = str(args.get("task_key", "")).encode("utf-8")
        ch = str(args.get("chunk", "")).encode("utf-8")
        l = str(args.get("layer", "task_flow")).encode("utf-8")
        n = lib.ProcessBatchRelay(tk, l, ch, buf, len(buf))
        return "RELAY_ERROR" if n < 0 else buf.value.decode("utf-8", errors="replace")
    if name == "delete_memory":
        k = str(args.get("node_key", "")).encode("utf-8")
        return "DELETED_AND_RECYCLED" if lib.DeleteMemory(k) == 1 else "DELETE_DENIED"
    return f"UNKNOWN_TOOL: {name}"


def _send(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    if _init_sdk_quietly() != 0:
        sys.stderr.write("[Arcane-Nexus MCP] InitializeSDK failed\n")
        sys.exit(1)
    try:
        for raw in sys.stdin:
            line = raw.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                continue
            req_id, method, params = req.get("id"), req.get("method", ""), req.get("params") or {}
            if method == "initialize":
                _send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "arcane-nexus", "version": "1.0.0"},
                    },
                })
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                _send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
            elif method == "tools/call":
                text = _call_tool(params.get("name", ""), params.get("arguments") or {})
                _send({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}})
            elif req_id is not None:
                _send({"jsonrpc": "2.0", "id": req_id, "result": {}})
    finally:
        lib.ShutdownSDK()


if __name__ == "__main__":
    main()
