# UI/UX Design System & Wireframe Specification
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Design Tokens System (Dark-Mode Centric & Accessible)

Our tokens adhere to the **WCAG 2.1 AA** accessibility standard, ensuring a minimum contrast ratio of **4.5:1** for normal text and **3:1** for large text against background layers.

### 1.1 Color Palette (Tailwind HSL Map)
The application leverages a premium, nature-inspired dark palette accented by vibrant greens and alerts to highlight anomalies.

| Token Name | HSL Value | Tailwind Class Equivalent | Purpose / Application |
| :--- | :--- | :--- | :--- |
| **Brand Primary (Deep Green)** | `hsl(142, 70%, 45%)` | `bg-emerald-500` / `text-emerald-500` | Main CTA buttons, active state indicators, branding. |
| **Brand Secondary (Eco Mint)** | `hsl(158, 64%, 52%)` | `bg-mint-400` | Focus states, secondary badges, visual highlights. |
| **Background Dark (Base)** | `hsl(222, 47%, 11%)` | `bg-slate-900` | Core background color for dark mode view. |
| **Surface Dark (Elevated)** | `hsl(217, 33%, 17%)` | `bg-slate-800` | Card wrappers, modals, navigation containers. |
| **Text Primary (High Contrast)**| `hsl(210, 40%, 98%)` | `text-slate-50` | Primary headers and core content text. |
| **Text Secondary (Medium)** | `hsl(215, 20%, 65%)` | `text-slate-400` | Descriptive subtitles, metadata labels, helper text. |
| **Alert Success** | `hsl(142, 76%, 36%)` | `bg-green-600` | Healthy crop status indicators, completed operations. |
| **Alert Warning** | `hsl(38, 92%, 50%)` | `bg-amber-500` | Moderate disease detection, offline warning banners. |
| **Alert Error / Danger** | `hsl(0, 84%, 60%)` | `bg-red-500` | High-severity pathogens, failed uploads, sync errors. |

### 1.2 Typography & Scale
*   **Font Family:** `Outfit`, sans-serif (Google Fonts) – clean geometric features, legible at small viewports.
*   **Scale Map:**
    *   `text-xs`: `0.75rem` ($12\text{px}$) – Metadata, timestamp indicators.
    *   `text-sm`: `0.875rem` ($14\text{px}$) – Standard body copy, button text.
    *   `text-base`: `1rem` ($16\text{px}$) – Active text, input fields.
    *   `text-lg`: `1.125rem` ($18\text{px}$) – Subheadings, card titles.
    *   `text-xl`: `1.25rem` ($20\text{px}$) – Modal headers.
    *   `text-2xl`: `1.5rem` ($24\text{px}$) – Screen titles.
    *   `text-3xl`: `1.875rem` ($30\text{px}$) – Landing metrics, splash text.

### 1.3 Border Radius & Shadows (Glassmorphism Tokens)
*   **Rounded Tokens:** `rounded-lg` ($8\text{px}$ for buttons), `rounded-2xl` ($16\text{px}$ for cards/sheets).
*   **Glassmorphism Surface Class:**
    ```css
    .glass-surface {
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    ```

---

## 2. Global Navigation & Screen Hierarchy

### 2.1 Information Architecture & Navigation Rules
*   **Mobile Layout:** Persistent bottom navigation bar containing 4 primary anchors. Persistent top bar with notification and settings shortcuts.
*   **Desktop/Tablet Layout:** Left sidebar column (docked/retractable) with page links. Main viewport updates as a Single Page Application (SPA).

```
                             [Global Viewport]
                                    |
            +-----------------------+-----------------------+
            | (Mobile)                                      | (Desktop / Tablet)
     [Persistent Top Bar]                            [Left Sidebar Navigation]
     ├── Brand Logo & Sync Status                    ├── Logo & User Identity
     ├── Notification Bell                           ├── 1. Dashboard (Default)
     └── Settings Gear                               ├── 2. Upload / Scanner
            |                                        ├── 3. History Logs
     [Primary Screen Area]                           ├── 4. Spatial Analytics
            |                                        ├── 5. Admin Panel (Conditional)
     [Persistent Bottom Bar]                         ├── 6. Settings Config
     ├── 1. Home / Dashboard                         └── 7. Notifications
     ├── 2. Upload Scanner
     ├── 3. History Logs
     └── 4. Spatial Analytics
```

---

## 3. UI Page Wireframes & Layout Grid

### Page 1: Home (Marketing Landing Page)
*   **Objective:** Introduce user value propositions, allow login routing, and download edge model assets.
*   **Aesthetics:** Dynamic diagonal vector graphics, prominent CTAs.

```
+-------------------------------------------------------------+
| [Logo] AgroVision AI                           [Sign In]    |
+-------------------------------------------------------------+
|                                                             |
|   PROTECT YOUR CROPS.                                       |
|   SAVE YOUR YIELD.                                          |
|                                                             |
|   AI-Powered disease diagnostics that work in the           |
|   palm of your hand—even completely offline.                |
|                                                             |
|   [Start Free Scan] (Primary Green Button)                 |
|                                                             |
+-------------------------------------------------------------+
| [ Metric Card ]          [ Metric Card ]          [ Metric ]|
| Active Farmers           Diseases Cataloged       Crops Safe|
| 12,000+                  85+ Species              98.2%     |
+-------------------------------------------------------------+
| Footer: MIT License                                         |
+-------------------------------------------------------------+
```

---

### Page 2: Login Screen
*   **Objective:** Authenticate users via phone OTP (optimized for rural areas) or credential login. Accessible labels.

```
+-------------------------------------------------------------+
| [<- Back]                                                   |
+-------------------------------------------------------------+
|                                                             |
|   Welcome to AgroVision AI                                  |
|   Enter credentials to access dashboards.                   |
|                                                             |
|   [Phone Number Field]                                      |
|   e.g. +91 98765 43210 (Accessible label: "Phone Input")    |
|                                                             |
|   [Password Field]                                          |
|   ******** (Show/Hide toggle)                               |
|                                                             |
|   [x] Keep me logged in (Offline access)                    |
|                                                             |
|   [      SIGN IN      ] (Primary CTA, focus outline ring)   |
|                                                             |
|   - OR -                                                    |
|   [Request SMS OTP Login]                                   |
|                                                             |
+-------------------------------------------------------------+
```

---

### Page 3: Main Dashboard
*   **Objective:** Provide quick status widgets: recent scans, regional outbreak alerts, weather indicators, and sync metrics.

```
+-------------------------------------------------------------+
| [Logo] AgroVision AI                  [Sync: OK]  [BellIcon]|
+-------------------------------------------------------------+
| Welcome Back, Suresh!                                       |
| Location: Bangalore North, IN (12.97, 77.59)                |
+-------------------------------------------------------------+
| [ Weather Widget ]           [ Sync Queue Status ]          |
| 32°C | Humidity 78%          2 offline scans pending sync   |
| Risk of Late Blight: HIGH    [Sync Now]                     |
+-------------------------------------------------------------+
| Quick Scan Trigger:                                         |
| +---------------------------------------------------------+ |
| | [Camera Icon] TAP TO SCAN CROP LEAF                     | |
| +---------------------------------------------------------+ |
+-------------------------------------------------------------+
| Recent Scans (last 3):                                      |
| * Tomato Leaf - Late Blight (Confidence 94%)      [12m ago] |
| * Coffee Leaf - Rust (Confidence 89%)             [2d ago]  |
| * Tomato Leaf - Healthy                           [3d ago]  |
+-------------------------------------------------------------+
```

---

### Page 4: Upload Image (Live Scanner Overlay)
*   **Objective:** Use custom camera view screen overlays to ensure parallel capture, alignment, and light limits.

```
+-------------------------------------------------------------+
| [ Cancel / Close ]                                          |
+-------------------------------------------------------------+
|                                                             |
|           +-----------------------------------+             |
|           |       CAMERA VIEWPORT AREA        |             |
|           |                                   |             |
|           |        Leaf Alignment Grid        |             |
|           |               [   ]               |             |
|           |                                   |             |
|           |                                   |             |
|           +-----------------------------------+             |
|                                                             |
|  [Warning: Shadow Detected - Adjust position]              |
|                                                             |
|  [Image Gallery Upload Button]    ( SHUTTER )    [Flash:Off]|
|                                                             |
+-------------------------------------------------------------+
```

---

### Page 5: Detection Result Page
*   **Objective:** Showcase diagnosis, Grad-CAM heatmap, toggle remedies, and escalation.

```
+-------------------------------------------------------------+
| [<- Dashboard]                         Share Result [PDF]   |
+-------------------------------------------------------------+
| Crop: Tomato | Leaf Diagnostic Report                       |
+-------------------------------------------------------------+
|                                                             |
|   +-------------------+   Diagnosis:                        |
|   |                   |   Phytophthora Late Blight          |
|   |   Grad-CAM        |   Confidence: 94.2%                 |
|   |   Heatmap Image   |   Severity: 24.5% Leaf Coverage     |
|   |                   |                                     |
|   +-------------------+   [Toggle Heatmap Overlay]          |
|                                                             |
+-------------------------------------------------------------+
| Treatment Protocols:                                        |
|   (o) Organic / Preventative      ( ) Chemical Option       |
|                                                             |
|   * Prune infected bottom leaves to increase airflow.       |
|   * Spray copper octanoate solution on affected areas.      |
|                                                             |
+-------------------------------------------------------------+
| Unsure about this result?                                   |
| [ Escalate to Agronomist ] -> (Opens chat workflow)        |
+-------------------------------------------------------------+
```

---

### Page 6: Disease History Log
*   **Objective:** Search, filter, and paginated logs of diagnostic history.

```
+-------------------------------------------------------------+
| Disease History Logs                                        |
+-------------------------------------------------------------+
| [ Search crops or diseases... ]                             |
| Filter: [All Crops v]  [All Severity v]  [Synced Status v]   |
+-------------------------------------------------------------+
| [!] 2 Scans Synced | [x] 1 Scan Pending Sync                |
+-------------------------------------------------------------+
| * Tomato Leaf - Blight      (Offline Saved)       [1h ago]  |
|   Severity: 24.5% | [View Report]                           |
|                                                             |
| * Coffee Leaf - Rust        (Synced)              [2d ago]  |
|   Severity: 12.0% | [View Report]                           |
|                                                             |
| * Rice Leaf - Brown Spot    (Synced)              [5d ago]  |
|   Severity: 45.2% | [View Report]                           |
+-------------------------------------------------------------+
|                                        [ Page 1 of 5 ] [Next]|
+-------------------------------------------------------------+
```

---

### Page 7: Spatial Analytics Dashboard
*   **Objective:** Render spatial outbreak metrics using PostGIS coordinates, disease expansion graphs, and charts.

```
+-------------------------------------------------------------+
| Spatial Outbreak Analytics                                  |
+-------------------------------------------------------------+
| Map View:                                                   |
| +---------------------------------------------------------+ |
| |  [+] [  PostGIS Heatmap Coordinates Visualization  ]   | |
| |  [-] [  Tomato Blight Hotspots (Red Clusters)       ]   | |
| +---------------------------------------------------------+ |
+-------------------------------------------------------------+
| Outbreak Velocity (Last 30 Days):                           |
|   Count (Scans)                                             |
|    50 |     /\_                                             |
|    25 |  __/   \__                                          |
|     0 +------------                                         |
|        May 1   May 15   June 1                              |
+-------------------------------------------------------------+
```

---

### Page 8: Admin Control Panel
*   **Objective:** Manage global configurations, load updated model versions, and audit user logs.

```
+-------------------------------------------------------------+
| Admin Control Panel                                         |
+-------------------------------------------------------------+
| Quick Tabs: [Models Setup]  [User Roles]  [Infection Limits]|
+-------------------------------------------------------------+
| Active ML Models:                                           |
| * Crop Classifier v2.1.4 (TFLite & PyTorch FP32) [Active]   |
|   - Image validation threshold: 70%                         |
|   - Cloud Precision (Top-1): 95.4%                          |
|   [Upload New Model Weights (.mar/.tflite)]                 |
+-------------------------------------------------------------+
| System Outbreak Threshold Limits:                          |
| * Alert radius: [ 50 km ]                                   |
| * Critical count trigger: [ 5 reports ]                     |
|                                                             |
| [ SAVE CONFIGURATIONS ]                                     |
+-------------------------------------------------------------+
```

---

### Page 9: System Settings Screen
*   **Objective:** Adjust global configurations, language translations, local cache size, and voice options.

```
+-------------------------------------------------------------+
| Application Settings                                        |
+-------------------------------------------------------------+
| System Localization:                                        |
| Language: [ Kannada (ಕನ್ನಡ) v ]                             |
| Voice Audio Assist: [x] Enable Text-To-Speech (TTS)         |
+-------------------------------------------------------------+
| Data Storage & Local Cache:                                 |
| * Offline database size: 45.2 MB                            |
| * Model weights size: 14.8 MB                               |
| [ Clear Diagnostic Images Cache ]                           |
+-------------------------------------------------------------+
| Sync Configurations:                                        |
| [x] Sync only over Wi-Fi network                            |
| [ ] Auto-upload scans in background                         |
+-------------------------------------------------------------+
```

---

### Page 10: Notifications & Alert Feeds
*   **Objective:** Alert users of regional pathogen epidemics and agronomist support replies.

```
+-------------------------------------------------------------+
| Notifications Center                                        |
+-------------------------------------------------------------+
| Quick Filter: [All]  [Critical Alerts]  [Agronomist Chats]  |
+-------------------------------------------------------------+
| [!] CRITICAL OUTBREAK ALERT                       [30m ago] |
|     Late Blight has been identified in 8 farms within       |
|     15km of your location. Inspect potato/tomato crops!     |
|                                                             |
| [Chat] Agronomist Dr. Elena                       [4h ago]  |
|     "Suresh, I reviewed your scan #c1fde. The chemical      |
|      dosage you applied is correct. Do not water tonight."  |
|                                                             |
| [Sync] Server Synchronization                     [1d ago]  |
|     2 offline scans synced successfully.                    |
+-------------------------------------------------------------+
```

---

## 4. Key Reusable UI Components Spec

### 4.1 DiagnosticCard Component
Renders details of a diagnostic scan.
*   **Props:**
    *   `cropName`: string
    *   `diseaseName`: string
    *   `confidence`: float
    *   `timestamp`: datetime
    *   `isSynced`: boolean
*   **Accessibility Design:** Explicit `aria-label` stating crop name, health prediction, and synchronization status. Focusable outline ring triggered on key events.

### 4.2 CameraFrameOverlay Component
Guides leaf centering.
*   **Props:**
    *   `cameraActive`: boolean
    *   `lightingWarning`: boolean
    *   `isParallel`: boolean
*   **Accessibility Design:** Non-visual screen reader guidelines outputting voice alerts: *"Position leaf in the center"* or *"Ensure leaf is well-lit"*.

---

*This UI/UX Design System serves as the layout guideline blueprint for the AgroVision React + Tailwind application.*
