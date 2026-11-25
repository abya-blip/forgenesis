# FORGENESIS — Final Prototype Master Specification

> **Purpose of This Document:**  
> Complete, self-contained engineering handoff and repository guide for the **final FORGENESIS prototype**. It covers the repository structure & CLI usage, finalized mechanical geometry, zero-clash plumbing coordinates, acoustic/bubble-barrier physics, electronics schematic & pinout, firmware state machine, and complete Bill of Materials (BOM).

---

## Repository Structure & CLI Usage

```text
.
├── README.md
├── FORGENESIS_Engineering_Report.pdf
├── FORGENESIS_Autodesk_CAD_and_MCP_Bundle.zip
└── FORGENESIS_Autodesk_CAD_and_MCP_Bundle/
    └── autodesk_cad/
        ├── dxf/                        # 2D laser-cut acrylic & SS304 mesh DXF sheets
        ├── obj/                        # Full assembly .obj / .mtl
        ├── stl/                        # Individual part & full assembly .stl meshes
        ├── fusion360_addin/
        │   └── ForgenesisMechanismB/   # Fusion 360 parametric CAD builder add-in
        └── mcp_server/
            ├── autodesk_fusion_mcp_server.py   # JSON-RPC 2.0 stdio MCP server (CLI-runnable)
            └── fusion360_mcp_bridge_addin.py   # Fusion 360 local HTTP bridge (127.0.0.1:9123)
```

### Running the MCP Server from CLI
`autodesk_fusion_mcp_server.py` uses only the Python 3 standard library (`sys`, `json`, `urllib`). Start it in stdio mode:

```bash
python3 FORGENESIS_Autodesk_CAD_and_MCP_Bundle/autodesk_cad/mcp_server/autodesk_fusion_mcp_server.py
```

Quick CLI smoke test:
```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | python3 FORGENESIS_Autodesk_CAD_and_MCP_Bundle/autodesk_cad/mcp_server/autodesk_fusion_mcp_server.py
```

### Running the Fusion 360 CAD Add-Ins
`ForgenesisMechanismB.py` and `fusion360_mcp_bridge_addin.py` require Autodesk Fusion 360's embedded Python runtime (`adsk.core`, `adsk.fusion`) on Windows or macOS:
1. Open **Autodesk Fusion 360**.
2. Load `FORGENESIS_Autodesk_CAD_and_MCP_Bundle/autodesk_cad/fusion360_addin/ForgenesisMechanismB` and `FORGENESIS_Autodesk_CAD_and_MCP_Bundle/autodesk_cad/mcp_server/fusion360_mcp_bridge_addin.py` via **Utilities → Scripts and Add-Ins**.
3. Connect your MCP client (or CLI) to `autodesk_fusion_mcp_server.py`, which forwards tool calls to `http://127.0.0.1:9123/cmd`.

---

## 1. System Overview & Coordinate Convention

**FORGENESIS** is an autonomous riverine plastic interception prototype scaled for a **$7000 \times 300 \times 300\,\text{mm}$ ($700 \times 30 \times 30\,\text{cm}$, $630\,\text{L}$ gross / $420\,\text{L}$ operating fill) rimless glass flume tank (`T-01`)**. It combines:
1. **Closed-loop artificial river flow** (`P-01` → `R-01` → `R-02` upstream sparger across a $0.95\,\text{m}$ coherent laminar approach reach, or $5.85\,\text{m}$ full open-channel reach when fed by an external laboratory flume pump).
2. **Passive V-funnel debris concentration** (`F-01`, `F-02`).
3. **Submerged underwater ultrasonic detection gate** (`DYP-L08B50TW-V3.0` Controlled-UART sonar).
4. **90° transverse upwelling EPDM micro-porous bubble barrier** (`D-01` + `A-01` compressor) to lift neutrally buoyant submerged plastics.
5. **Full-Width 3-Slot Castellated Waterfall Weir** (`W-01`–`W-08`) with a removable **SS304 mesh basket** (`B-01`).

### Master 3D CAD Coordinate System (Millimeters)
* **$X$-axis (Flow Direction, $0 \to 7000\,\text{mm}$):** Upstream end wall is $X = 0$; downstream end wall is $X = 7000$.
* **$Y$-axis (Channel Width, $-150 \to +150\,\text{mm}$):** Channel centerline is $Y = 0$; Near glass wall is $Y = -150$; Far glass wall is $Y = +150$.
* **$Z$-axis (Elevation, $0 \to 300\,\text{mm}$):** Inner tank glass floor is $Z = 0$; top glass rim is $Z = 300$; static flume waterline is **$Z = 200\,\text{mm}$** ($420\,\text{L}$ fill volume).

---

## 2. Finalized Mechanical & Hydraulic Architecture

### Zone 0: Glass Flume Tank & Closed-Loop Recirculation (`T-01`, `R-01`, `R-02`)
* **Tank (`T-01`):** $7000 \times 300 \times 300\,\text{mm}$ ($700 \times 30 \times 30\,\text{cm}$) internal dimensions, $6.0\,\text{mm}$ tempered rimless float glass. Zero glass drilling—all brackets clip onto the top $6\,\text{mm}$ rim.
* **Upstream Flow-Maker Sparger (`R-02`):** $\varnothing 20.0\,\text{mm}$ OD Schedule-40 Blue PVC pipe spanning $Y = -140\text{ to }+140\,\text{mm}$ at **$X = 4900.0\,\text{mm}, Z = 175.0\,\text{mm}$**, capped on both ends with EPDM caps, featuring $14\text{--}18\times \varnothing 3.0\,\text{mm}$ horizontal forward-facing jets establishing a coherent $0.95\,\text{m}$ laminar approach reach ($X = 4900.0\text{ to }5850.0\,\text{mm}$) during standalone recirculation (while $X = 0\text{ to }5850.0\,\text{mm}$ serves as the full approach reach under external lab flume flow).
* **Elevated Return Pipe (`R-01`):** $1.85\,\text{m}$ **$\varnothing 20.0\,\text{mm}$ OD thin-wall Blue UPVC pipe ($16.6\,\text{mm}$ ID)** running from the rear sump pump outlet ($X = 6706\,\text{mm}$) along the near glass wall at **$Y = -139.0\,\text{mm}, Z = 32.0\,\text{mm}$** up to the sparger riser at $X = 4900.0\,\text{mm}$ ($< 0.28\,\text{m}$ Darcy-Weisbach friction loss at $800\,\text{L/h}$).
  * Supported by three laser-cut $3.0\,\text{mm}$ acrylic standoff clips (`C-05`–`C-07` at $X = 5150, 5750, 6450\,\text{mm}$).

### Zone 1: V-Funnel Debris Concentrator (`F-01`, `F-02`, `C-08`, `C-09`)
* Twin $3.0\,\text{mm}$ clear cast acrylic vanes ($240 \times 220\,\text{mm}$) starting at $X = 5850.0\,\text{mm}$ ($Y = \pm 150\,\text{mm}$) and converging at $25^\circ$ to $X = 6075.5\,\text{mm}$ with a **$140.0\,\text{mm}$ throat width** ($Y = \pm 70\,\text{mm}$), height $Z = 0\text{--}220\,\text{mm}$.
* Near-wall vane `F-02` includes a **$58 \times 30\,\text{mm}$ clearance notch ($Z = 17\text{--}47\,\text{mm}$)** at its upstream edge so `R-01` passes through with zero collision.
* Locked to the $6\,\text{mm}$ glass rim via top-rim clamps (`C-08`, `C-09` at $X = 5840\text{--}5868\,\text{mm}$) with M4 nylon thumbscrews (`FAST-01`).

### Zone 2: Exact 1:1 Underwater Sonar Gate (`S-01`, `S-02`, `C-01`, `S-05`)
* **Sensor:** Shenzhen Dianyingpu **`DYP-L08B50TW-V3.0`** (DFRobot `SEN0598` form factor) IP68 coaxial cylindrical ultrasonic rangefinder.
  * **Dimensions:** $\varnothing 28.0 \times 34.0\,\text{mm}$ Gray ASA/PVC body, `M19×1.5` external metric thread ($17\,\text{mm}$ span), smooth $\varnothing 18.0\,\text{mm}$ front barrel, two $\varnothing 28.0\,\text{mm}$ 18-tooth gear-knurled locknuts, $\varnothing 23.0 \times 1.5\,\text{mm}$ white silicone sealing gasket, central $\varnothing 4.0\,\text{mm}$ 4-core waterproof cable.
  * **Mounting:** Clamped through a $\varnothing 19.5\,\text{mm}$ hole in the no-drill acrylic drop plate (`C-01`, $72 \times 142\,\text{mm}$) at **$X = 6200.0\,\text{mm}, Z = 180.0\,\text{mm}$** ($20\,\text{mm}$ submerged below the $200\,\text{mm}$ waterline), firing transversely across the channel toward $Y = -125\,\text{mm}$.
  * **Range & Blind Zone:** $8\text{--}800\,\text{cm}$ in water ($80\,\text{mm}$ near-field blind zone; V-funnel keeps debris $> 80\,\text{mm}$ from the transducer face). $50^\circ$ full beam ($25^\circ$ half-angle).
* **Acoustic Stop Baffle (`S-05`):** $110 \times 215 \times 18\,\text{mm}$ pad of **30 PPI open-cell reticulated polyurethane foam** mounted on an acrylic backplate at **$X = 6200.0\,\text{mm}, Y = -125\,\text{mm}$** to absorb acoustic backscatter and eliminate false wall echoes.

### Zone 3: 90° Transverse EPDM Bubble Barrier (`D-01`, `D-02`, `A-01`)
* **Position & Orientation:** Placed at **$X = 6380.0\,\text{mm}, Z = 12.0\,\text{mm}$**, oriented **90° transverse** across the channel ($Y = -115.0\text{ to }+140.0\,\text{mm}$, $255\,\text{mm}$ active span) so it aligns parallel with the full-width 3-slot weir.
* **Zero-Clash Plumbing Decoupling (`D-01` vs. `R-01`):**
  * Blue return pipe `R-01` ($\varnothing 20.0\,\text{mm}$ OD) is at $Y = -139.0\,\text{mm}, Z = 32.0\,\text{mm}$ (bottom edge $Z = 22.0\,\text{mm}$, inner wall $Y = -129.0\,\text{mm}$).
  * EPDM diffuser `D-01` sits on silicone saddle feet at $Z = 12.0\,\text{mm}$ and terminates at $Y = -115.0\,\text{mm}$ with an EPDM dome endcap (`Y = -120.0 mm` tip).
  * **Guaranteed Clearances:** **$24.0\,\text{mm}$ lateral / $20.0\,\text{mm}$ vertical centerline offset** (**$11.2\,\text{mm}$ diagonal / $9.0\,\text{mm}$ lateral net air gap**).
* **EPDM Membrane Physics (Zero Water Ingress on Shutoff):**
  * Uses a **$\varnothing 20\,\text{mm} \times 250\,\text{mm}$ EPDM micro-porous diffuser tube** with elastic laser-punched micro-slits.
  * At $188\,\text{mm}$ water depth above the diffuser, hydrostatic pressure is **$1.84\,\text{kPa}$**. EPDM slit cracking pressure is **$\sim 2.0\,\text{kPa}$** (total needed $\approx 4.34\,\text{kPa}$).
  * When `A-01` is switched OFF by the MCU, elastic slit memory snaps shut—preventing water ingress without relying on orifice sizing.
  * Far end ($Y = +142\,\text{mm}$) routes up via `D-02` silicone airline over the tank rim ($Z = 315\,\text{mm}$) through an **inline one-way check valve** to air compressor `A-01`.

### Zone 4: Full-Width 3-Slot Castellated Waterfall Weir & Sump (`W-01`–`W-08`, `B-01`, `P-01`)
* **Weir Footprint:** $X = 6570.0\text{ to }6666.0\,\text{mm}$ ($96.0\,\text{mm}$ long), $Y = -147.0\text{ to }+147.0\,\text{mm}$ (**$294.0\,\text{mm}$ full-width**), $3.0\,\text{mm}$ clear/cyan cast acrylic bonded with `Weld-On #4` and sealed to glass with aquarium silicone.
* **Front Castellated Weir Plate (`W-01`):**
  * **3 Waterfall Intake Gates** at crest **$Z = 190.0\,\text{mm}$** ($10.0\,\text{mm}$ below the $200.0\,\text{mm}$ static waterline, matching the $H_w = 10.4\,\text{mm}$ Poleni overflow equilibrium at $800\,\text{L/h}$ without sump drowning): **Right $55.0\,\text{mm}$**, **Center $54.0\,\text{mm}$**, **Left $55.0\,\text{mm}$** ($164\,\text{mm}$ total open crest).
  * **4 Castellated Baffle Teeth** rising $22.0\,\text{mm}$ to **$Z = 212.0\,\text{mm}$** (widths: $24, 38, 38, 24\,\text{mm}$).
* **Internal Sump Hydraulics:**
  * Operational drawdown level inside sump: **$Z = 165.0\,\text{mm}$** ($25\,\text{mm}$ free waterfall plunge below the $190.0\,\text{mm}$ crest; $35\,\text{mm}$ total drop from the $200\,\text{mm}$ main channel).
  * **Basket Guide Rails (`W-06`, `W-07`, `W-08`):** Mounted at $Z = 120.0\,\text{mm}$ (including center anti-sag rib `W-08`).
* **Removable Debris Basket (`B-01`, `B-02`):** $282.0 \times 86.0 \times 40.0\,\text{mm}$ folded **SS304 perforated/woven mesh** ($2.0\,\text{mm}$ aperture) resting on the rails at $Z = 123.0\,\text{mm}$, with dual yellow-anodized T-grip pull handles (`B-02`).
* **Submersible Water Pump (`P-01`):** Positioned at the sump floor ($Z = 3\text{--}55\,\text{mm}$) beneath a $40 \times 40\,\text{mm}$ perforated **anti-vortex baffle plate** ($Z = 61\,\text{mm}$).
  * **Target Hydraulic Spec:** $12\,\text{V DC}$ brushless submersible pump, **$800\,\text{L/h}$** ($13.3\,\text{L/min}$), $5\,\text{m}$ head:
    * *Idle Mode (35% PWM / $280\,\text{L/h}$):* Maintains steady $\sim 8.0\,\text{cm/s}$ artificial river current.
    * *Surge Mode (100% PWM / $800\,\text{L/h}$):* Pulls $45.2\,\text{cm/s}$ waterfall intake across all 3 slots.
  * *(Bench Note: If testing initially with a smaller $240\,\text{L/h}$ pump, temporarily block the Left and Right weir slots so only the Center $54\,\text{mm}$ slot flows, preserving nappe thickness and intake velocity.)*

---

## 3. Finalized Electronics, Power & Pinout Architecture

### Power Distribution
1. **Main Supply (`PSU-01a`):** $12\,\text{V DC}, 4.2\,\text{A}$ ($50.4\,\text{W}$) SMPS → `5.5×2.1 mm` DC barrel jack → **`2A`–`4A` Time-Delay Fuse** (`2A` for $240\,\text{L/h}$ pump; `3A`–`4A` for $800\,\text{L/h}$ pump) → **SPST Rocker Switch** → `$12\,\text{V}$ Main Bus`.
2. **Bulk Capacitance:** **$1000\,\mu\text{F} / 16\,\text{V}$ Electrolytic Capacitor** across `+12V` and `GND` near the motor MOSFETs to absorb pump/compressor inrush spikes.
3. **Logic Rail (`PSU-01b`):** **`LM2596` (or `MP1584EN`) DC-DC Buck Converter** stepping `12V` down to **`5.00V DC`** → feeds **ESP32 `VIN/5V`** and **Sonar `VCC` (`5.0V`)**. *(Never connect `12V` directly to ESP32 or Sonar!)*

### Microcontroller & Level Shifting
* **MCU (`U-01`):** **`ESP32-WROVER-E` CH340 DevKitC**.
  * **CRITICAL `WROVER-E` PINOUT RULE:** `GPIO16` and `GPIO17` are internally wired to **PSRAM** on `WROVER-E` modules. **Do NOT use `GPIO16/17` for UART2!**
  * **Assigned Safe GPIOs:**
    * `GPIO25` → **Sonar `TX`** (via `TXS0108E` channel 1)
    * `GPIO26` → **Sonar `RX/Trig`** (via `TXS0108E` channel 2)
    * `GPIO27` → **Water Pump `P-01` MOSFET Gate** (`LEDC` PWM Channel 0, **`250–500 Hz`**)
    * `GPIO14` → **Air Compressor `A-01` MOSFET Gate** (Digital ON/OFF)
    * `GPIO32` → **Override Push Button (`12×12×12 mm` tactile)** (`INPUT_PULLUP` to `GND`)
    * `GPIO33` → **Status Red DIP LED** (via `220 Ω` series resistor to `GND`)
    * `GPIO4` *(Optional)* → **`DS18B20` 1-Wire Temp Probe** (with **`4.7 kΩ`** pull-up to `3.3V` — *never `4.7 Ω`!*)
* **Bidirectional Level Shifter (`TXS0108E`):**
  * `VCCA` = `3.3V` (from ESP32 `3V3` pin)
  * `VCCB` = `5.0V` (from Buck Converter)
  * `OE` = tied to `3.3V` (`VCCA`)
  * `GND` = Common Ground (shared between `12V` SMPS, `5V` Buck, ESP32, and Sonar)

### Dual Low-Side Power MOSFET Drivers (2 Identical Channels)
For **both** `P-01` (Water Pump) and `A-01` (Air Compressor):
* **MOSFET:** **`IRLZ44PBF`** logic-level N-Channel MOSFET ($V_{\text{GS(th)}} \approx 1\text{--}2\,\text{V}$).
* **Gate Drive:** ESP32 GPIO → **`220 Ω`** series resistor → MOSFET Gate, plus **`10 kΩ`** pull-down resistor from Gate to `GND`.
* **Load Wiring:** `+12V` → Motor `+` | Motor `-` → MOSFET Drain | MOSFET Source → `GND`.
* **Flyback Protection:** **`1N4007`** (or fast Schottky `1N5822` for PWM pump) wired in reverse-parallel directly across Motor `+` and Motor `-` (cathode stripe to `+12V`). Keep pump PWM at **`250–500 Hz`** if using `1N4007`.

---

## 4. Firmware Control & `DYP-L08B50TW-V3.0` UART Protocol

### Sonar Controlled-UART Protocol (`9600 bps, 8N1`)
1. ESP32 sends trigger byte **`0xFF`** on `GPIO26` (`RX/Trig`) every $100\,\text{ms}$.
2. Sonar replies with a **4-byte frame** within $\le 18\,\text{ms}$:
   `[0xFF, Data_H, Data_L, SUM]`
3. Verify checksum: `SUM == (0xFF + Data_H + Data_L) & 0xFF`.
4. Compute raw distance:
   $$D_{\text{mm}} = (\text{Data\_H} \ll 8) \mid \text{Data\_L}$$
5. *(Optional Temperature Compensation via `DS18B20`):*
   $$c(T) = 1402.7 + 4.88\,T - 0.0482\,T^2$$
   $$D_{\text{cal}} = D_{\text{mm}} \times \frac{c(T_{\text{water}})}{1482.0}$$

### Autonomous State Machine
* **Baseline Acoustic Gate:** Clear channel distance to the 30 PPI foam stop is **$\approx 245\text{--}250\,\text{mm}$**.
* **Debounced Trigger Threshold:** $3$ consecutive valid readings with **$85\,\text{mm} < D_{\text{cal}} < 225\,\text{mm}$** indicates plastic debris crossing the V-funnel throat.
* **States:**
  1. **`IDLE_MONITORING`**: Pump `P-01` at `35%` PWM (`280 L/h`), Air Compressor `A-01` `OFF`, LED slow heartbeat.
  2. **`SURGE_INTERCEPT`** (triggered on debris detection):
     * Ramp Pump `P-01` to **`100%` PWM** (`800 L/h` surge).
     * Turn Air Compressor `A-01` **`ON`** (activates `D-01` EPDM bubble curtain to lift submerged plastics into the 3 weir slots).
     * Hold surge for **$T_{\text{surge}} = 12\,\text{s}$** (extends if additional debris passes through the sonar gate).
  3. **`COOLDOWN_RETURN`**: Turn `A-01` `OFF` (EPDM slits snap shut), ramp `P-01` smoothly back to `35%` PWM, return to `IDLE_MONITORING`.
  4. **`MANUAL_OVERRIDE`**: Tactile button toggles continuous `100%` surge + bubble barrier for priming/testing.

---

## 5. Complete Final Prototype Bill of Materials (BOM)

### A. 2D Fabricated Parts (From Project DXF Files)
* `W-01`–`W-08`: $3.0\,\text{mm}$ Clear/Cyan Cast Acrylic Full-Width 3-Slot Weir & Rails (`forgenesis_laser_cut_sheet_3mm_acrylic.dxf`)
* `F-01`, `F-02`: $3.0\,\text{mm}$ Clear Cast Acrylic V-Funnel Vanes
* `C-01`–`C-09`: $3.0\,\text{mm}$ Clear Cast Acrylic No-Drill Rim Brackets & Pipe Standoffs
* `B-01`: $282 \times 86 \times 40\,\text{mm}$ Folded SS304 Mesh Basket, $2.0\,\text{mm}$ aperture (`forgenesis_ss304_mesh_basket_pattern.dxf`)

### B. Commercial Off-The-Shelf (COTS) Hardware & Electronics

| ID | Part | Key Spec / MPN | Qty |
| :--- | :--- | :--- | :---: |
| **`T-01`** | Rimless Glass Flume Tank | $7000 \times 300 \times 300\,\text{mm}$ ($700 \times 30 \times 30\,\text{cm}$), $6\,\text{mm}$ glass ($630\,\text{L}$ gross / $420\,\text{L}$ fill) | 1 |
| **`S-01`/`S-02`** | Underwater Ultrasonic Sonar | `DYP-L08B50TW-V3.0` (`SEN0598`), `M19×1.5` + locknuts & gasket | 1 |
| **`S-05`** | Acoustic Absorber Pad | `30 PPI` reticulated polyurethane foam ($110 \times 215 \times 18\,\text{mm}$) | 1 |
| **`P-01`** | Submersible Water Pump | $12\,\text{V DC}$ Brushless Centrifugal, **`800 L/h`** (`JT-550` / `DC40C-1230`) | 1 |
| **`A-01`** | Micro Diaphragm Air Compressor | $12\,\text{V DC}$ Single-Head Air Pump (`SP ELECTRON` / `370`-frame, $\ge 50\,\text{kPa}$) | 1 |
| **`D-01`** | EPDM Bubble Diffuser Tube | $\varnothing 20 \times 250\,\text{mm}$ EPDM micro-porous sleeve + EPDM dome endcap | 1 |
| **`D-02`** | Silicone Airline & Check Valve | $\varnothing 4\text{--}5\,\text{mm}$ ID silicone tube ($1.5\,\text{m}$) + inline 1-way check valve | 1 set |
| **`R-01`/`R-02`** | PVC Return & Sparger Piping | $\varnothing 20\,\text{mm}$ Blue UPVC ($2\,\text{m}$) + $3\times 90^\circ$ elbows + $\varnothing 20\,\text{mm}$ sparger | 1 set |
| **`U-01`** | Microcontroller Board | `ESP32-WROVER-E` CH340 DevKitC | 1 |
| **`PSU-01a`** | Main Power Adapter | $12\,\text{V DC}, 4.2\,\text{A}$ ($50.4\,\text{W}$) SMPS + `5.5×2.1 mm` barrel jack | 1 |
| **`PSU-01b`** | Buck Converter (`12V → 5V`) | `LM2596` or `MP1584EN` adjusted to `5.00V` | 1 |
| **`LV-01`** | Logic Level Shifter | `TXS0108E` 8-Channel Bidirectional ($3.3\,\text{V} \leftrightarrow 5.0\,\text{V}$) | 1 |
| **`Q1, Q2`** | Power MOSFETs | `IRLZ44PBF` Logic-Level N-Channel ($55/60\,\text{V}$) | 2 |
| **`D1, D2`** | Flyback Diodes | `1N4007GT` (or `1N5822` Schottky for PWM pump) | 2 |
| **`R1–R5`** | Metal Film Resistors (`0.25W`) | $2\times 220\,\Omega$ (gates) + $1\times 220\,\Omega$ (LED) + $2\times 10\,\text{k}\Omega$ (pull-downs) | 5 |
| **`C1`** | Bulk Decoupling Capacitor | `1000 µF / 16V` Electrolytic (`E210M016E125HY`) | 1 |
| **`F1, SW1`** | Fuse & Main Switch | $5\times 20\,\text{mm}$ `2A` (or `3A–4A` for $800\,\text{L/h}$) time-delay fuse + holder + SPST rocker switch | 1 set |
| **`UI`** | LED, Button & Perfboard | $5\,\text{mm}$ Red LED, $12\times 12\times 12\,\text{mm}$ tactile button, proto PCB, screw terminals, headers, `18–20 AWG` wire | 1 set |
| **`E-01`–`E-03`** | Enclosure & Sealants | IP65 box (`~158×90×60 mm`), `PG7` glands, `Weld-On #4` acrylic glue, aquarium silicone, zip ties, foam pad | 1 set |
