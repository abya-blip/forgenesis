#!/usr/bin/env python3
"""
Autodesk Fusion 360 Model Context Protocol (MCP) Server (JSON-RPC 2.0 over stdio)
Connects any MCP Client (Antigravity / Claude / Cursor) to a local Autodesk Fusion 360
instance running the Fusion 360 HTTP Bridge Add-in on localhost:9123, OR directly
executes FORGENESIS parametric CAD generation tools.

Tools exposed via MCP:
- build_forgenesis_mechanism_b: Builds the complete FORGENESIS 3-Slot Weir + DYP-08B assembly in Fusion 360.
- create_extruded_box: Creates a parametric 3D box component in Fusion 360.
- create_cylinder: Creates a parametric 3D cylinder in Fusion 360.
- set_fusion_parameter: Updates a parametric dimension in Fusion 360 and recomputes the timeline.
- export_step_stl: Exports the active Fusion 360 assembly to STEP (.step) or STL (.stl).
"""

import sys
import json
import urllib.request
import urllib.error

FUSION_BRIDGE_URL = "http://127.0.0.1:9123/cmd"


def call_fusion_bridge(payload: dict) -> dict:
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            FUSION_BRIDGE_URL, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {
            "status": "offline_queued",
            "message": (
                f"Fusion 360 local bridge on {FUSION_BRIDGE_URL} is not reachable ({e}). "
                "Ensure Fusion 360 is open with fusion360_mcp_bridge_addin running, or run "
                "ForgenesisMechanismB.py directly via Fusion 360 Utilities -> Add-Ins."
            ),
            "command": payload,
        }


TOOLS = [
    {
        "name": "build_forgenesis_mechanism_b",
        "description": "Constructs the complete FORGENESIS Full-Width 3-Slot Active Suction Waterfall Weir & DYP-08B Underwater Sonar 3D assembly in Autodesk Fusion 360.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "weir_crest_height_mm": {"type": "number", "default": 190.0},
                "weir_crest_width_mm": {"type": "number", "default": 90.0},
                "sump_height_mm": {"type": "number", "default": 220.0},
                "acrylic_thickness_mm": {"type": "number", "default": 3.0}
            }
        }
    },
    {
        "name": "create_extruded_box",
        "description": "Creates a parametric 3D box component in Autodesk Fusion 360 (dimensions in mm).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "x_mm": {"type": "number"},
                "y_mm": {"type": "number"},
                "z_mm": {"type": "number"},
                "dx_mm": {"type": "number"},
                "dy_mm": {"type": "number"},
                "dz_mm": {"type": "number"}
            },
            "required": ["name", "x_mm", "y_mm", "z_mm", "dx_mm", "dy_mm", "dz_mm"]
        }
    },
    {
        "name": "set_fusion_parameter",
        "description": "Updates a named UserParameter in Fusion 360 (e.g., Weir_Crest_Height = 190 mm).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "parameter_name": {"type": "string"},
                "expression": {"type": "string"}
            },
            "required": ["parameter_name", "expression"]
        }
    },
    {
        "name": "export_cad_file",
        "description": "Exports the active Fusion 360 assembly to STEP, IGES, SAT, or STL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "enum": ["step", "stl", "iges"]},
                "output_path": {"type": "string"}
            },
            "required": ["format", "output_path"]
        }
    }
]


def handle_request(req: dict):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "autodesk-fusion360-forgenesis-mcp", "version": "1.0.0"}
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        targs = params.get("arguments", {})
        bridge_res = call_fusion_bridge({"tool": tname, "arguments": targs})
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(bridge_res, indent=2)}]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
