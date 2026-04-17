#!/usr/bin/env python3
"""Standalone TCP client for the blender-mcp addon socket (default port 9876).

Usage:
    python3 mcp_client.py <command> ['<json-params>']

Examples:
    python3 mcp_client.py get_scene_info
    python3 mcp_client.py inspect_addon '{"name":"stablegen"}'
    python3 mcp_client.py call_operator '{"operator":"stablegen.queue_process","params":{}}'

Zero dependencies beyond the Python standard library.
"""
import json
import socket
import sys

HOST = "localhost"
PORT = 9876
RECV_CHUNK = 8192
TIMEOUT = 30


def send(cmd_type, params=None, host=HOST, port=PORT, timeout=TIMEOUT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((host, port))
    payload = json.dumps({"type": cmd_type, "params": params or {}}).encode()
    s.sendall(payload)
    buf = b""
    while True:
        chunk = s.recv(RECV_CHUNK)
        if not chunk:
            break
        buf += chunk
        try:
            json.loads(buf.decode())
            break
        except Exception:
            continue
    s.close()
    return json.loads(buf.decode())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    try:
        result = send(cmd, params)
        print(json.dumps(result, indent=2))
    except ConnectionRefusedError:
        print(json.dumps({
            "error": "ConnectionRefused",
            "hint": "Is Blender running with the blender-mcp addon? "
                    "Press N in viewport → BlenderMCP → Connect to Claude.",
            "endpoint": f"{HOST}:{PORT}",
        }, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()
