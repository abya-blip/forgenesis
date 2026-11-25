#Author: Antigravity AI (FORGENESIS Engineering Team)
#Description: FORGENESIS Final Prototype — Full-Width 3-Slot Castellated Weir Assembly
#             Pure structural and mechanical assembly in Autodesk Fusion 360 (7000 x 300 x 300 mm Flume).
#             Zero water volumes, zero waterfall cascades, zero bubbles — allowing crystal-clear inspection
#             of all mechanical parts, 3-slot castellated weir, SS304 mesh basket, exact 1:1 DYP-L08B50TW-V3.0
#             sonar with 18-tooth gear locknuts, and decoupled closed-loop plumbing.

import adsk.core
import adsk.fusion
import traceback
import math

CONFIG = {
    "flume_length_mm": 7000.0,
    "flume_width_mm": 300.0,
    "flume_height_mm": 300.0,
    "acrylic_thickness_mm": 3.0,

    # Upstream Closed-Loop Flow-Maker Sparger Bar (0.95m coherent laminar approach)
    "sparger_x_mm": 4900.0,
    "sparger_z_mm": 175.0,
    "sparger_width_mm": 280.0,

    # Zone 1: V-Funnel Concentrator
    "funnel_start_x_mm": 5850.0,
    "funnel_vane_length_mm": 240.0,
    "funnel_throat_width_mm": 140.0,
    "funnel_height_mm": 220.0,

    # Zone 2: Exact 1:1 DYP-L08B50TW-V3.0 (Cylindrical Gray ASA/PVC M19x1.5 body, L=34mm, 2x D28mm 18-Tooth Gear Locknuts)
    "sonar_x_mm": 6200.0,
    "sonar_submerged_z_mm": 180.0,

    # Zone 3: Full-Width Upwelling & Forward-Sweep EPDM Bubble Diffuser Manifold
    "diffuser_x_mm": 6380.0,
    "diffuser_width_mm": 284.0,
    "diffuser_od_mm": 20.0,

    # Zone 4: Full-Width 3-Slot Castellated Waterfall Weir
    "weir_box_x_mm": 6570.0,
    "weir_box_y_mm": -147.0,
    "weir_outer_length_mm": 96.0,
    "weir_outer_width_mm": 294.0,
    "weir_inner_width_mm": 288.0,
    "weir_crest_height_mm": 190.0,
    "weir_tooth_top_mm": 212.0,
    "sump_wall_height_mm": 220.0,
    "basket_rail_z_mm": 120.0,
    "basket_length_mm": 86.0,
    "basket_width_mm": 282.0,
    "basket_height_mm": 40.0,
    "basket_lift_offset_mm": 0.0,
}

APPEARANCE_CACHE = {}

def get_or_create_appearance(app, design, custom_name, library_search_names, rgb_override=None):
    if custom_name in APPEARANCE_CACHE:
        return APPEARANCE_CACHE[custom_name]
    existing = design.appearances.itemByName(custom_name)
    if existing:
        if rgb_override:
            _apply_rgb_to_appearance(existing, rgb_override)
        APPEARANCE_CACHE[custom_name] = existing
        return existing

    base_app = None
    for candidate in library_search_names:
        for lib in app.materialLibraries:
            try:
                base_app = lib.appearances.itemByName(candidate)
                if base_app:
                    break
            except:
                pass
        if base_app:
            break

    if not base_app:
        for candidate in library_search_names:
            kw = candidate.lower()
            for lib in app.materialLibraries:
                try:
                    for a in lib.appearances:
                        if kw in a.name.lower():
                            base_app = a
                            break
                    if base_app:
                        break
                except:
                    pass
            if base_app:
                break

    if not base_app:
        try:
            if design.appearances.count > 0:
                base_app = design.appearances.item(0)
        except:
            pass

    if base_app:
        try:
            cloned = design.appearances.addByCopy(base_app, custom_name)
            if rgb_override:
                _apply_rgb_to_appearance(cloned, rgb_override)
            APPEARANCE_CACHE[custom_name] = cloned
            return cloned
        except:
            if rgb_override:
                _apply_rgb_to_appearance(base_app, rgb_override)
            APPEARANCE_CACHE[custom_name] = base_app
            return base_app
    return None

def _apply_rgb_to_appearance(app_obj, rgb):
    r, g, b = rgb
    color = adsk.core.Color.create(int(r), int(g), int(b), 255)
    for prop_name in ("Color", "color", "opaque_albedo", "albedo", "reflectance", "diffuse"):
        try:
            prop = app_obj.appearanceProperties.itemByName(prop_name)
            if prop and hasattr(prop, "value"):
                prop.value = color
                break
        except:
            pass

def apply_appearance_and_opacity(body, app_obj, opacity=1.0):
    if app_obj:
        try:
            body.appearance = app_obj
        except:
            pass
    if opacity < 0.999:
        try:
            body.opacity = float(opacity)
        except:
            pass

def create_sub_component(parent_comp, name):
    new_occ = parent_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    sub_comp = new_occ.component
    sub_comp.name = name
    return sub_comp

def add_extruded_box_body(target_comp, body_name, x, y, z, dx, dy, dz, app_obj=None, opacity=1.0):
    sketches = target_comp.sketches
    xy_plane = target_comp.xYConstructionPlane
    sketch = sketches.add(xy_plane)

    x_cm = x / 10.0
    y_cm = y / 10.0
    dx_cm = dx / 10.0
    dy_cm = dy / 10.0
    z_cm = z / 10.0
    dz_cm = dz / 10.0

    lines = sketch.sketchCurves.sketchLines
    p0 = adsk.core.Point3D.create(x_cm, y_cm, 0)
    p1 = adsk.core.Point3D.create(x_cm + dx_cm, y_cm, 0)
    p2 = adsk.core.Point3D.create(x_cm + dx_cm, y_cm + dy_cm, 0)
    p3 = adsk.core.Point3D.create(x_cm, y_cm + dy_cm, 0)

    lines.addByTwoPoints(p0, p1)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p0)

    prof = sketch.profiles.item(0)
    extrudes = target_comp.features.extrudeFeatures

    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    dist = adsk.core.ValueInput.createByReal(dz_cm)
    start_offset = adsk.core.ValueInput.createByReal(z_cm)
    ext_input.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext_input.startExtent = adsk.fusion.OffsetStartDefinition.create(start_offset)

    ext = extrudes.add(ext_input)
    body = ext.bodies.item(0)
    body.name = body_name
    apply_appearance_and_opacity(body, app_obj, opacity)
    return body

def add_true_cylinder_body(target_comp, body_name, p_start, p_end, radius_mm, app_obj=None, opacity=1.0):
    p1 = adsk.core.Point3D.create(p_start[0]/10.0, p_start[1]/10.0, p_start[2]/10.0)
    p2 = adsk.core.Point3D.create(p_end[0]/10.0, p_end[1]/10.0, p_end[2]/10.0)
    axis_vec = p1.vectorTo(p2)
    length = axis_vec.length
    if length < 1e-5:
        return None

    planes = target_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByDistanceOnPath(adsk.core.Line3D.create(p1, p2), adsk.core.ValueInput.createByReal(0.0))
    cplane = planes.add(plane_input)

    sketches = target_comp.sketches
    sketch = sketches.add(cplane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), radius_mm / 10.0)

    prof = sketch.profiles.item(0)
    extrudes = target_comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(length)), adsk.fusion.ExtentDirections.PositiveExtentDirection)

    ext = extrudes.add(ext_input)
    body = ext.bodies.item(0)
    body.name = body_name
    apply_appearance_and_opacity(body, app_obj, opacity)
    return body

def create_angled_vane_component(target_comp, name, pts_xy, z_base, z_height, app_obj=None, opacity=1.0):
    sketches = target_comp.sketches
    xy_plane = target_comp.xYConstructionPlane
    sketch = sketches.add(xy_plane)

    lines = sketch.sketchCurves.sketchLines
    for i in range(len(pts_xy)):
        p_a = adsk.core.Point3D.create(pts_xy[i][0]/10.0, pts_xy[i][1]/10.0, 0)
        p_b = adsk.core.Point3D.create(pts_xy[(i+1)%len(pts_xy)][0]/10.0, pts_xy[(i+1)%len(pts_xy)][1]/10.0, 0)
        lines.addByTwoPoints(p_a, p_b)

    prof = sketch.profiles.item(0)
    extrudes = target_comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(z_height / 10.0)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext_input.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(z_base / 10.0))

    ext = extrudes.add(ext_input)
    body = ext.bodies.item(0)
    body.name = name
    apply_appearance_and_opacity(body, app_obj, opacity)
    return body

def add_gear_locknut_body(target_comp, name, sx, sz, y_start, y_end, r_inner, r_root, r_tip, num_teeth, app_obj=None):
    sketches = target_comp.sketches
    xz_plane = target_comp.xZConstructionPlane
    sketch = sketches.add(xz_plane)

    cx = sx / 10.0
    cz = sz / 10.0
    r_in = r_inner / 10.0
    r_rt = r_root / 10.0
    r_tp = r_tip / 10.0

    lines = sketch.sketchCurves.sketchLines
    pts = []
    n = num_teeth
    for i in range(n):
        ang_base = (2.0 * math.pi * i) / n
        step = (2.0 * math.pi) / n
        a0 = ang_base
        a1 = ang_base + 0.28 * step
        a2 = ang_base + 0.44 * step
        a3 = ang_base + 0.72 * step

        pts.append(adsk.core.Point3D.create(cx + r_rt * math.cos(a0), cz + r_rt * math.sin(a0), 0))
        pts.append(adsk.core.Point3D.create(cx + r_tp * math.cos(a1), cz + r_tp * math.sin(a1), 0))
        pts.append(adsk.core.Point3D.create(cx + r_tp * math.cos(a2), cz + r_tp * math.sin(a2), 0))
        pts.append(adsk.core.Point3D.create(cx + r_rt * math.cos(a3), cz + r_rt * math.sin(a3), 0))

    for k in range(len(pts)):
        lines.addByTwoPoints(pts[k], pts[(k + 1) % len(pts)])

    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cx, cz, 0), r_in)

    prof = None
    for p in sketch.profiles:
        if p.profileLoops.count >= 2:
            prof = p
            break
    if not prof:
        prof = sketch.profiles.item(0)

    extrudes = target_comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    length = (y_end - y_start) / 10.0
    ext_input.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(length)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext_input.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(y_start / 10.0))

    ext = extrudes.add(ext_input)
    body = ext.bodies.item(0)
    body.name = name
    apply_appearance_and_opacity(body, app_obj, 1.0)
    return body

def build_dry_model(master_comp, app, design):
    """Builds the complete physical assembly WITHOUT water."""
    app_glass = get_or_create_appearance(app, design, "Engineering_Clear_Float_Glass", ["Clear", "Glass - Clear", "Glass"], (225, 245, 255))
    app_acrylic_clear = get_or_create_appearance(app, design, "Engineering_Clear_Cast_Acrylic", ["Acrylic - Clear", "Plastic - Transparent", "Clear"], (240, 249, 255))
    app_acrylic_cyan = get_or_create_appearance(app, design, "Engineering_Cyan_Cast_Acrylic", ["Acrylic - Clear", "Plastic - Transparent", "Clear"], (6, 182, 212))
    app_ss304 = get_or_create_appearance(app, design, "Engineering_SS304_Satin_Perforated", ["Stainless Steel - Satin", "Steel - Satin", "Metal"], (218, 224, 232))
    app_alum_gold = get_or_create_appearance(app, design, "Engineering_Yellow_Anodized_Alum", ["Aluminum - Anodized Glossy (Yellow)", "Gold", "Brass"], (234, 179, 8))
    app_sonar_gray_asa = get_or_create_appearance(app, design, "Engineering_Matte_Gray_ASA_PVC", ["Plastic - Matte (Gray)", "ABS (White)", "Plastic"], (148, 156, 168))
    app_sonar_nut_asa = get_or_create_appearance(app, design, "Engineering_Knurled_DarkGray_ASA", ["Plastic - Matte (Dark Gray)", "Nylon 6-6 (White)", "Plastic"], (100, 116, 139))
    app_white_washer = get_or_create_appearance(app, design, "Engineering_White_Silicone_Washer", ["Silicone - White", "Rubber - White", "White"], (248, 250, 252))
    app_epdm_rubber = get_or_create_appearance(app, design, "Engineering_Black_EPDM_Rubber", ["Rubber - Soft", "Rubber", "Black"], (24, 28, 36))
    app_pvc_orange = get_or_create_appearance(app, design, "Engineering_Orange_Sch40_PVC", ["Plastic - Glossy (Orange)", "ABS (White)", "Plastic"], (249, 115, 22))
    app_pvc_blue = get_or_create_appearance(app, design, "Engineering_Blue_Sch40_PVC", ["Plastic - Glossy (Blue)", "ABS (White)", "Plastic"], (2, 132, 199))
    app_foam_baffle = get_or_create_appearance(app, design, "Engineering_Acoustic_30PPI_Foam", ["Polyurethane - Foam", "Foam", "Rubber"], (30, 41, 59))

    L = CONFIG["flume_length_mm"]
    W = CONFIG["flume_width_mm"]
    H = CONFIG["flume_height_mm"]
    t = CONFIG["acrylic_thickness_mm"]
    t_glass = 6.0

    # 1. Glass Fish Tank (Empty / Dry)
    tank_comp = create_sub_component(master_comp, "Zone0_Glass_FishTank_Flume")
    add_extruded_box_body(tank_comp, "Tank_Floor_Glass_6mm", 0, -W/2 - t_glass, -t_glass, L, W + 2*t_glass, t_glass, app_glass, opacity=0.88)
    add_extruded_box_body(tank_comp, "Tank_Right_Wall_Glass_6mm", 0, -W/2 - t_glass, 0, L, t_glass, H, app_glass, opacity=0.22)
    add_extruded_box_body(tank_comp, "Tank_Left_Wall_Glass_6mm", 0, W/2, 0, L, t_glass, H, app_glass, opacity=0.22)
    add_extruded_box_body(tank_comp, "Tank_Upstream_EndWall_6mm", -t_glass, -W/2, 0, t_glass, W, H, app_glass, opacity=0.35)
    add_extruded_box_body(tank_comp, "Tank_Downstream_EndWall_6mm", L, -W/2, 0, t_glass, W, H, app_glass, opacity=0.35)

    # 2. Closed-Loop Recirculation Pipe (R-01 D20mm OD UPVC Elevated at Y=-139, Z=32mm) & Sparger Bar (R-02)
    recirc_comp = create_sub_component(master_comp, "Zone0_ClosedLoop_Recirculation_Sparger")
    spx = CONFIG["sparger_x_mm"]
    add_true_cylinder_body(recirc_comp, "R02_Upstream_FlowMaker_Sparger_Bar_D20mm", (spx, -140, 175), (spx, 140, 175), 10.0, app_pvc_blue, opacity=1.0)
    add_true_cylinder_body(recirc_comp, "R02_Sparger_Left_EndCap", (spx, 140, 175), (spx, 145, 175), 11.5, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(recirc_comp, "R02_Sparger_Right_EndCap", (spx, -145, 175), (spx, -140, 175), 11.5, app_epdm_rubber, opacity=1.0)
    for ny in range(-120, 121, 30):
        add_true_cylinder_body(recirc_comp, f"R02_Jet_Nozzle_Y{ny}", (spx, ny, 175), (spx + 13, ny, 175), 2.5, app_ss304, opacity=1.0)
    
    wx_r = CONFIG["weir_box_x_mm"] + CONFIG["weir_outer_length_mm"]
    add_true_cylinder_body(recirc_comp, "R01_Rear_Pump_Outlet_Stub_D20mm", (wx_r - 20, 0, 33), (wx_r + 40, 0, 33), 10.0, app_pvc_blue, opacity=1.0)
    add_true_cylinder_body(recirc_comp, "R01_Rear_Transverse_Header_D20mm", (wx_r + 40, 0, 33), (wx_r + 40, -139, 32), 10.0, app_pvc_blue, opacity=1.0)
    add_true_cylinder_body(recirc_comp, "R01_Elevated_Return_Pipe_D20mm", (wx_r + 40, -139, 32), (spx, -139, 32), 10.0, app_pvc_blue, opacity=1.0)
    add_true_cylinder_body(recirc_comp, "R01_Upstream_Vertical_Riser_D20mm", (spx, -139, 32), (spx, -139, 175), 10.0, app_pvc_blue, opacity=1.0)
    for clip_x in (5150, 5750, 6450):
        add_extruded_box_body(recirc_comp, f"C05_Pipe_StandOff_Clip_X{clip_x}", clip_x - 12, -149, 0, 24, 20, 44, app_acrylic_clear, opacity=0.75)

    # 3. Zone 1: V-Funnel Concentrator (F-01 & F-02 with R-01 clearance notch)
    funnel_comp = create_sub_component(master_comp, "Zone1_VFunnel_Concentrator")
    fx = CONFIG["funnel_start_x_mm"]
    dx_f = 225.5
    ty = CONFIG["funnel_throat_width_mm"] / 2.0
    fh = CONFIG["funnel_height_mm"]
    create_angled_vane_component(funnel_comp, "F01_Left_Funnel_Vane_3mm_Acrylic", [(fx, W/2), (fx + dx_f, ty), (fx + dx_f, ty - t), (fx, W/2 - t)], 0, fh, app_acrylic_clear, opacity=0.68)
    # Notched F-02 right vane clearing D20mm R-01 return pipe (Z=17..47 near upstream X=5850..5908)
    f02_mid_x = fx + 58.0
    f02_mid_y_out = -W/2 + (58.0 / dx_f) * (W/2 - ty)
    f02_mid_y_in = f02_mid_y_out + t
    create_angled_vane_component(funnel_comp, "F02_Right_Funnel_Vane_LowerTab", [(fx, -W/2 + t), (f02_mid_x, f02_mid_y_in), (f02_mid_x, f02_mid_y_out), (fx, -W/2)], 0, 17.0, app_acrylic_clear, opacity=0.68)
    create_angled_vane_component(funnel_comp, "F02_Right_Funnel_Vane_UpperSpan", [(fx, -W/2 + t), (f02_mid_x, f02_mid_y_in), (f02_mid_x, f02_mid_y_out), (fx, -W/2)], 47.0, fh - 47.0, app_acrylic_clear, opacity=0.68)
    create_angled_vane_component(funnel_comp, "F02_Right_Funnel_Vane_Downstream", [(f02_mid_x, f02_mid_y_in), (fx + dx_f, -ty + t), (fx + dx_f, -ty), (f02_mid_x, f02_mid_y_out)], 0, fh, app_acrylic_clear, opacity=0.68)

    # 4. Zone 2: Exact 1:1 DYP-L08B50TW-V3.0 Sonar & Gate
    sonar_comp = create_sub_component(master_comp, "Zone2_DYPL08B50TW_V3_1to1_Cylindrical_Sonar")
    sx = CONFIG["sonar_x_mm"]
    sz = CONFIG["sonar_submerged_z_mm"]
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Front_Acoustic_Nose_Bevel", (sx, 115.0, sz), (sx, 115.8, sz), 8.6, app_sonar_gray_asa, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Front_Smooth_Barrel_D18mm", (sx, 115.8, sz), (sx, 125.5, sz), 9.0, app_sonar_gray_asa, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_M19x15_Thread_Root_Shaft", (sx, 125.5, sz), (sx, 142.0, sz), 8.8, app_sonar_gray_asa, opacity=1.0)
    for k_th in range(10):
        ty_th = 126.2 + 1.5 * k_th
        add_true_cylinder_body(sonar_comp, f"DYPL08B50TW_V3_M19_Thread_Crest_{k_th+1}", (sx, ty_th, sz), (sx, ty_th + 0.75, sz), 9.5, app_sonar_nut_asa, opacity=1.0)
    add_gear_locknut_body(sonar_comp, "DYPL08B50TW_V3_Front_18Tooth_Gear_Locknut_D28mm", sx, sz, 126.0, 130.5, 9.5, 12.3, 14.0, 18, app_sonar_nut_asa)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_White_Silicone_Sealing_Washer", (sx, 130.5, sz), (sx, 132.0, sz), 11.5, app_white_washer, opacity=1.0)
    add_gear_locknut_body(sonar_comp, "DYPL08B50TW_V3_Rear_18Tooth_Gear_Locknut_D28mm", sx, sz, 137.0, 141.5, 9.5, 12.3, 14.0, 18, app_sonar_nut_asa)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Rear_Step_Collar_D18mm", (sx, 142.0, sz), (sx, 144.0, sz), 9.0, app_sonar_nut_asa, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Rear_Endcap_D16_5mm", (sx, 144.0, sz), (sx, 149.0, sz), 8.25, app_sonar_gray_asa, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Rear_Left_Spanner_Indent", (sx - 4.6, 148.6, sz), (sx - 4.6, 149.2, sz), 1.6, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Rear_Right_Spanner_Indent", (sx + 4.6, 148.6, sz), (sx + 4.6, 149.2, sz), 1.6, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Central_Cable_Boss_D6_4mm", (sx, 148.8, sz), (sx, 150.2, sz), 3.2, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Axial_Cable_Exit_D4mm", (sx, 150.0, sz), (sx, 154.5, sz), 2.0, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(sonar_comp, "DYPL08B50TW_V3_Vertical_UART_Umbilical_D4mm", (sx, 154.5, sz), (sx, 154.5, 302.0), 2.0, app_epdm_rubber, opacity=1.0)

    # C-01 Suspension Bracket (with TRUE D19.5 mm hole in XZ sketch) & Acoustic Stop
    c01_sketch = sonar_comp.sketches.add(sonar_comp.xZConstructionPlane)
    c01_lines = c01_sketch.sketchCurves.sketchLines
    cp0 = adsk.core.Point3D.create((sx - 36)/10.0, 15.8, 0)
    cp1 = adsk.core.Point3D.create((sx + 36)/10.0, 15.8, 0)
    cp2 = adsk.core.Point3D.create((sx + 36)/10.0, 30.0, 0)
    cp3 = adsk.core.Point3D.create((sx - 36)/10.0, 30.0, 0)
    c01_lines.addByTwoPoints(cp0, cp1)
    c01_lines.addByTwoPoints(cp1, cp2)
    c01_lines.addByTwoPoints(cp2, cp3)
    c01_lines.addByTwoPoints(cp3, cp0)
    c01_sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(sx/10.0, sz/10.0, 0), 0.975)
    c01_prof = None
    for p in c01_sketch.profiles:
        if p.profileLoops.count >= 2:
            c01_prof = p
            break
    if not c01_prof:
        c01_prof = c01_sketch.profiles.item(0)
    c01_ext = sonar_comp.features.extrudeFeatures.createInput(c01_prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    c01_ext.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(0.35)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    c01_ext.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(13.35))
    c01_body = sonar_comp.features.extrudeFeatures.add(c01_ext).bodies.item(0)
    c01_body.name = "C01_NoDrill_Glass_Rim_Drop_Plate_D19_5mm"
    apply_appearance_and_opacity(c01_body, app_acrylic_clear, 0.65)

    add_extruded_box_body(sonar_comp, "C01_NoDrill_Glass_Rim_Top_Bridge", sx - 36, 133.5, 300, 72, 28.5, 4, app_acrylic_clear, opacity=0.82)
    add_extruded_box_body(sonar_comp, "C01_NoDrill_Glass_Rim_Outer_Jaw", sx - 36, 156, 268, 72, 6, 32, app_acrylic_clear, opacity=0.82)
    add_extruded_box_body(sonar_comp, "Acoustic_Stop_Acrylic_Backplate", sx - 55, -128, 0, 110, 3, 220, app_acrylic_clear, opacity=0.78)
    add_extruded_box_body(sonar_comp, "Acoustic_Stop_30PPI_Polyurethane_Foam", sx - 55, -125, 0, 110, 18, 215, app_foam_baffle, opacity=0.96)
    add_extruded_box_body(sonar_comp, "S05_Rim_Hanger_Drop", sx - 16, -135, 220, 32, 10, 80, app_acrylic_clear, opacity=0.82)
    add_extruded_box_body(sonar_comp, "S05_Rim_Hanger_Top", sx - 16, -159, 300, 32, 34, 4, app_acrylic_clear, opacity=0.82)
    add_extruded_box_body(sonar_comp, "S05_Rim_Hanger_OuterJaw", sx - 16, -159, 276, 32, 3, 24, app_acrylic_clear, opacity=0.82)

    # 5. Zone 3: EPDM Diffuser Manifold (D-01 Decoupled, Z=12mm) + A-01 Air Compressor
    diff_comp = create_sub_component(master_comp, "Zone3_FullWidth_Upwelling_Bubble_Diffuser")
    dx_m = CONFIG["diffuser_x_mm"]
    add_true_cylinder_body(diff_comp, "D01_EPDM_MicroPorous_Diffuser_D20mm", (dx_m, -115, 12), (dx_m, 140, 12), 10.0, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(diff_comp, "D01_Near_Sealed_Dome_EndCap", (dx_m, -120, 12), (dx_m, -115, 12), 10.8, app_epdm_rubber, opacity=1.0)
    add_true_cylinder_body(diff_comp, "D01_Far_Inlet_Coupling_Tee", (dx_m, 140, 12), (dx_m, 145, 12), 11.2, app_pvc_orange, opacity=1.0)
    for foot_y in (-105, 130):
        add_extruded_box_body(diff_comp, f"D01_Floor_Saddle_Foot_Y{foot_y}", dx_m - 12, foot_y - 8, 0, 24, 16, 6, app_epdm_rubber, opacity=0.95)
    add_true_cylinder_body(diff_comp, "D02_AntiSiphon_Air_Riser_Tube", (dx_m, 142, 12), (dx_m, 142, 315), 4.0, app_pvc_orange, opacity=0.95)
    add_true_cylinder_body(diff_comp, "D02_TopRim_OneWay_Check_Valve", (dx_m, 142, 315), (dx_m, 168, 315), 6.5, app_ss304, opacity=1.0)
    add_extruded_box_body(diff_comp, "A01_Air_Compressor_Head", dx_m - 15, 200, 2, 30, 14, 30, app_epdm_rubber, opacity=0.98)
    add_true_cylinder_body(diff_comp, "A01_370_Motor_Body", (dx_m, 212, 16), (dx_m, 246, 16), 14.0, app_ss304, opacity=1.0)

    # 6. Zone 4: Full-Width 3-Slot Castellated Waterfall Weir (Crest Z=190mm, Teeth Z=212mm)
    weir_comp = create_sub_component(master_comp, "Zone4_FullWidth_3Slot_Castellated_Weir")
    wx = CONFIG["weir_box_x_mm"]
    wy = CONFIG["weir_box_y_mm"]
    wz = 0.0
    wl = CONFIG["weir_outer_length_mm"]
    ww = CONFIG["weir_outer_width_mm"]
    cw = CONFIG["weir_inner_width_mm"]
    tooth_h = CONFIG["weir_tooth_top_mm"] - CONFIG["weir_crest_height_mm"]

    add_extruded_box_body(weir_comp, "W05_FullWidth_Sump_Base_Plate", wx, wy, wz, wl, ww, t, app_acrylic_clear, opacity=0.85)
    add_extruded_box_body(weir_comp, "W03_Sump_Left_Side_Wall", wx, wy + ww - t, wz + t, wl, t, CONFIG["sump_wall_height_mm"], app_acrylic_clear, opacity=0.45)
    add_extruded_box_body(weir_comp, "W04_Sump_Right_Side_Wall", wx, wy, wz + t, wl, t, CONFIG["sump_wall_height_mm"], app_acrylic_clear, opacity=0.45)
    add_extruded_box_body(weir_comp, "W02_FullWidth_Rear_Sump_Wall", wx + wl - t, wy + t, wz + t, t, cw, CONFIG["sump_wall_height_mm"], app_acrylic_clear, opacity=0.62)

    add_extruded_box_body(weir_comp, "W01_FullWidth_Base_Weir_Wall_Z190", wx, wy + t, wz + t, t, cw, CONFIG["weir_crest_height_mm"] - t, app_acrylic_cyan, opacity=0.82)
    add_extruded_box_body(weir_comp, "W01_Tooth1_Right_Shoulder_24mm", wx, wy + t, CONFIG["weir_crest_height_mm"], t, 24, tooth_h, app_acrylic_cyan, opacity=0.92)
    add_extruded_box_body(weir_comp, "W01_Tooth2_MidRight_Baffle_38mm", wx, wy + t + 79, CONFIG["weir_crest_height_mm"], t, 38, tooth_h, app_acrylic_cyan, opacity=0.92)
    add_extruded_box_body(weir_comp, "W01_Tooth3_MidLeft_Baffle_38mm", wx, wy + t + 171, CONFIG["weir_crest_height_mm"], t, 38, tooth_h, app_acrylic_cyan, opacity=0.92)
    add_extruded_box_body(weir_comp, "W01_Tooth4_Left_Shoulder_24mm", wx, wy + t + 264, CONFIG["weir_crest_height_mm"], t, 24, tooth_h, app_acrylic_cyan, opacity=0.92)

    add_extruded_box_body(weir_comp, "W06_Basket_Rail_Right", wx + t, wy + t, CONFIG["basket_rail_z_mm"], wl - 2*t, 8, t, app_acrylic_clear, opacity=0.95)
    add_extruded_box_body(weir_comp, "W07_Basket_Rail_Left", wx + t, wy + ww - t - 8, CONFIG["basket_rail_z_mm"], wl - 2*t, 8, t, app_acrylic_clear, opacity=0.95)
    add_extruded_box_body(weir_comp, "W08_Center_AntiSag_Support_Rib", wx + t, wy + ww/2.0 - 4, CONFIG["basket_rail_z_mm"], wl - 2*t, 8, t, app_acrylic_clear, opacity=0.95)

    bx = wx + 5.0
    by = wy + 6.0
    bz = CONFIG["basket_rail_z_mm"] + t + CONFIG["basket_lift_offset_mm"]
    bl = CONFIG["basket_length_mm"]
    bw = CONFIG["basket_width_mm"]
    bh = CONFIG["basket_height_mm"]
    add_extruded_box_body(weir_comp, "B01_Basket_Perforated_SS304_Floor", bx, by, bz, bl, bw, 1.5, app_ss304, opacity=0.88)
    add_extruded_box_body(weir_comp, "B01_Basket_Perforated_Front_Lip", bx, by, bz + 1.5, 1.5, bw, bh - 1.5, app_ss304, opacity=0.88)
    add_extruded_box_body(weir_comp, "B01_Basket_Perforated_Rear_Wall", bx + bl - 1.5, by, bz + 1.5, 1.5, bw, bh - 1.5, app_ss304, opacity=0.88)
    add_extruded_box_body(weir_comp, "B01_Basket_Perforated_Right_Wall", bx + 1.5, by, bz + 1.5, bl - 3.0, 1.5, bh - 1.5, app_ss304, opacity=0.88)
    add_extruded_box_body(weir_comp, "B01_Basket_Perforated_Left_Wall", bx + 1.5, by + bw - 1.5, bz + 1.5, bl - 3.0, 1.5, bh - 1.5, app_ss304, opacity=0.88)

    for h_y, h_name in ((by + 65.0, "Right"), (by + bw - 65.0, "Left")):
        add_true_cylinder_body(weir_comp, f"B02_{h_name}_Handle_Stem", (bx + bl/2.0, h_y, bz + bh), (bx + bl/2.0, h_y, 235.0), 2.5, app_alum_gold, opacity=1.0)
        add_true_cylinder_body(weir_comp, f"B02_{h_name}_Handle_TGrip", (bx + bl/2.0 - 15.0, h_y, 235.0), (bx + bl/2.0 + 15.0, h_y, 235.0), 3.5, app_alum_gold, opacity=1.0)

    px = wx + wl/2.0 - 24.0
    py = wy + ww/2.0 - 18.0
    add_extruded_box_body(weir_comp, "P01_Submersible_Pump_Body_800Lh", px, py, wz + t, 48.0, 36.0, 52.0, app_epdm_rubber, opacity=0.98)
    add_true_cylinder_body(weir_comp, "P01_Discharge_Nozzle_D20mm", (px + 48.0, py + 18.0, wz + 33.0), (wx + wl - t, py + 18.0, wz + 33.0), 10.0, app_pvc_blue, opacity=1.0)
    add_extruded_box_body(weir_comp, "P01_AntiVortex_Baffle_Plate_40x40mm", px + 4.0, -20.0, 61.0, 40.0, 40.0, 2.0, app_ss304, opacity=0.88)

    # 7. Zone 5: External IP65 Electronics Box
    elec_comp = create_sub_component(master_comp, "Zone5_External_IP65_Electronics_Box")
    add_extruded_box_body(elec_comp, "E01_Enclosure_ABS_Base", 6120, 156, 170, 160, 60, 90, app_sonar_nut_asa, opacity=0.98)
    add_extruded_box_body(elec_comp, "E01_Clear_Polycarbonate_Lid", 6118, 216, 168, 164, 4, 94, app_acrylic_clear, opacity=0.75)
    for pg_x in (6160, 6200, 6240):
        add_true_cylinder_body(elec_comp, f"E01_PG7_Gland_X{pg_x}", (pg_x, 156, 185), (pg_x, 146, 185), 6.0, app_epdm_rubber, opacity=1.0)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.activeDocument
        design = doc.products.itemByProductType('DesignProductType')
        if not design:
            ui.messageBox('Please switch to a Modeling/Design document before running.')
            return

        root_comp = design.rootComponent
        occ_name = "FORGENESIS_Final_Prototype"
        for occ in list(root_comp.occurrences):
            if occ.name.startswith(occ_name) or occ_name in occ.name:
                try:
                    occ.deleteMe()
                except:
                    pass

        master_occ = root_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        master_comp = master_occ.component
        master_comp.name = occ_name

        build_dry_model(master_comp, app, design)

        ui.messageBox(
            "FORGENESIS Final Prototype (7000x300x300 mm Flume) Built!\n\n"
            "• Zero-clash R-01 D20mm return pipe (Y=-139, Z=32mm) & notched F-02 V-funnel\n"
            "• D-01 EPDM micro-porous diffuser (X=6380mm) & A-01 compressor\n"
            "• 1:1 DYP-L08B50TW-V3.0 M19x1.5 Sonar (X=6200mm, bored C-01 D19.5mm)\n"
            "• Full-Width 3-Slot Castellated Weir (X=6570mm, Crest Z=190mm)"
        )
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass
