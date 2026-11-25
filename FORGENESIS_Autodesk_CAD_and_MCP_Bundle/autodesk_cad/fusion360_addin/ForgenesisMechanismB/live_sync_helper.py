#Author: Antigravity AI (FORGENESIS Engineering Team)
#Description: Fusion 360 Auto-Reloading Hot-Sync Add-In. Watches ForgenesisMechanismB.py and live-updates your Fusion 360 3D model automatically whenever you prompt Antigravity!

import adsk.core
import adsk.fusion
import traceback
import os

app = None
ui = None


def run_live_update():
    """Rebuilds or updates the FORGENESIS_MechanismB_DYP08B_Assembly in the active document without creating a new tab."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)

    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent

    # Remove old FORGENESIS_MechanismB_DYP08B_Assembly occurrence if it exists so we replace it cleanly in-place!
    for occ in list(root.occurrences):
        if occ.component.name.startswith("FORGENESIS_MechanismB"):
            occ.deleteMe()
            break

    return design, root
