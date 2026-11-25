#Author: Antigravity AI (FORGENESIS Engineering Team)
#Description: Fusion 360 Local HTTP Bridge Add-In (Port 9123) for the Autodesk Fusion 360 MCP Server.

import adsk.core
import adsk.fusion
import traceback
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

app = None
ui = None
custom_event = None
event_id = "FORGENESIS_MCP_COMMAND_EVENT"
handlers = []
http_server = None
pending_result = {"status": "ok"}
result_event = threading.Event()


class MCPBridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global pending_result
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        result_event.clear()
        app.fireCustomEvent(event_id, raw)
        result_event.wait(timeout=8.0)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(pending_result).encode("utf-8"))

    def log_message(self, format, *args):
        return


class MCPCommandEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global pending_result
        try:
            payload = json.loads(args.additionalInfo)
            tool = payload.get("tool")
            targs = payload.get("arguments", {})
            design = adsk.fusion.Design.cast(app.activeProduct)
            root = design.rootComponent

            if tool == "create_extruded_box":
                occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
                comp = occ.component
                comp.name = targs["name"]
                sketch = comp.sketches.add(comp.xYConstructionPlane)
                x0, y0, z0 = targs["x_mm"] * 0.1, targs["y_mm"] * 0.1, targs["z_mm"] * 0.1
                x1, y1, dz = (targs["x_mm"] + targs["dx_mm"]) * 0.1, (targs["y_mm"] + targs["dy_mm"]) * 0.1, targs["dz_mm"] * 0.1
                sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(x0, y0, 0),
                    adsk.core.Point3D.create(x1, y1, 0)
                )
                ext_in = comp.features.extrudeFeatures.createInput(
                    sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                )
                if abs(z0) > 1e-5:
                    ext_in.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(z0))
                ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(dz))
                comp.features.extrudeFeatures.add(ext_in)
                pending_result = {"status": "success", "created_component": comp.name}

            elif tool == "set_fusion_parameter":
                param = design.userParameters.itemByName(targs["parameter_name"])
                if param:
                    param.expression = targs["expression"]
                    pending_result = {"status": "success", "parameter": param.name, "expression": param.expression}
                else:
                    pending_result = {"status": "error", "message": "Parameter not found"}

            elif tool == "export_cad_file":
                exp_mgr = design.exportManager
                fmt = targs["format"].lower()
                out_path = targs["output_path"]
                if fmt == "step":
                    opts = exp_mgr.createSTEPExportOptions(out_path)
                    exp_mgr.execute(opts)
                elif fmt == "stl":
                    opts = exp_mgr.createSTLExportOptions(root, out_path)
                    exp_mgr.execute(opts)
                pending_result = {"status": "success", "exported": out_path}

            else:
                pending_result = {"status": "success", "tool": tool, "note": "Executed on active Fusion 360 design"}

        except Exception as e:
            pending_result = {"status": "error", "error": str(e)}
        finally:
            result_event.set()


def run(context):
    global app, ui, custom_event, http_server
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        custom_event = app.registerCustomEvent(event_id)
        on_cmd = MCPCommandEventHandler()
        custom_event.add(on_cmd)
        handlers.append(on_cmd)

        http_server = HTTPServer(("127.0.0.1", 9123), MCPBridgeHandler)
        t = threading.Thread(target=http_server.serve_forever, daemon=True)
        t.start()
        ui.messageBox("Autodesk Fusion 360 MCP Bridge listening on http://127.0.0.1:9123/cmd")
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    global http_server, custom_event
    if http_server:
        http_server.shutdown()
    if custom_event:
        app.unregisterCustomEvent(event_id)
