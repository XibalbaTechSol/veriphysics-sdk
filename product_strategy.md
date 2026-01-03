# VeriPhysics Product Strategy

## Market Landscape
The market for media authentication is bifurcating into:
1.  **Active Provenance**: Proving reality at the moment of capture (High Value, "Guarantee").
2.  **Passive Detection**: Analyzing files after the fact (Low Value, "Probability").

VeriPhysics focuses on **Active Provenance** using **Physics-based Verification**.

## Competitive Landscape

### 1. The "Heavyweight" Incumbents (Direct Competitors)
*   **Truepic / Serelay**
*   **Model**: Enterprise B2B, Secure Hardware, Closed Source.
*   **Gap**: Expensive, heavy integration, requires specific hardware support.

### 2. The "Blockchain/Web3" Challengers
*   **Numbers Protocol / Nodle**
*   **Model**: Decentralized ledgers, Tokens.
*   **Gap**: High friction for Web2 developers (wallets, crypto).

### 3. The "Deepfake Detectors" (Indirect Competitors)
*   **Sensity / Reality Defender**
*   **Model**: AI Scanning (Passive).
*   **Gap**: False positives, lacks mathematical certainty.

### 4. Open Source
*   **ProofMode**
*   **Model**: Free, Open Source tools.
*   **Gap**: Unpolished, lacks a simple "True/False" Verification-as-a-Service API.

## Our Strategy: "Stripe for Reality"
Position VeriPhysics as the developer-first SDK.
-   **Differentiation**: **Multi-modal Physics** (Gyro vs. Optical Flow) proves *causality*, not just metadata security. Works on standard hardware.
-   **User Experience**: Simple integration (`isReal = Verify.capture()`).
-   **Business Model**: Web2 API (SaaS), strictly B2B.

### Value Proposition
> "Competitors check metadata (which can be spoofed); we check physical laws (which cannot)."

## Differentiating Feature Roadmap

To maintain our competitive moat against C2PA (container security) and AI Detection (pixel scanning), we will implement features that provide mathematical **Certainty**.

### 1. The "Causality Score" (Core Metric)
-   **What**: A normalized 0-100 score indicating how perfectly the video's optical flow aligns with the device's sensor logs.
-   **Advantage**: Provides a definitive, math-based truth value that probabilistic AI detection cannot offering.
-   **Status**: **[ MVP Implemented ]** (basic correlation) -> **[ Planned ]** (normalized scoring).

### 2. "Screen Attack" Immunity (The Analog Hole Solver)
-   **What**: Explicit detection of "2D Planar Motion". If a user films a deepfake on a monitor, the optical flow lacks true 3D parallax.
-   **Advantage**: Defeats the #1 attack vector against C2PA/Truepic (filming a screen).
-   **Status**: **[ Planned ]**

### 3. "Handheld Human" Verification
-   **What**: frequency analysis of gyroscope data to detect the 8-12Hz micro-tremors characteristic of human muscles.
-   **Advantage**: Proves a **human** was holding the device, prohibiting "tripod attacks", bots, or AI-injected camera paths.
-   **Status**: **[ Planned ]**

### 4. C2PA "Physics" Assertion
-   **What**: Act as a C2PA Signing Authority that injects a "Physics Verified" assertion into standard C2PA manifests.
-   **Advantage**: Makes VeriPhysics a value-add partner to the C2PA ecosystem, not just a competitor. Enables interoperability.
-   **Status**: **[ Long Term ]**
