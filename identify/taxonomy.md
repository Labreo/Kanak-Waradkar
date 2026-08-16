# Pillar 1 — IDENTIFY: GenAI Payment Fraud Attack Taxonomy

## Executive Summary
This taxonomy details emerging Generative AI-enabled payment fraud attack vectors targeting onboarding/KYC, behavioral transaction channels, and autonomous agentic payment flows. It serves as the formal threat grounding for Project TRIAD's **Generate** and **Defend** engines.

---

## 1. Vector A: Synthetic Identity & Deepfake KYC Fraud

### 1.1 Fully Synthetic Identity
- **Description**: Entirely fabricated identity records containing generated names, synthesized national IDs (e.g., PAN/Aadhaar/SSN format with valid structure), and non-existent residential/employment backgrounds.
- **GenAI Acceleration**: Diffusion models and LLMs generate fully coherent synthetic life histories and credit profiles that pass surface-level consistency checks at near-zero marginal cost.
- **Target Surface**: Digital onboarding pipelines, automated credit scoring, neobank account opening.
- **Key Indicators**: Absence of historical credit bureau depth, synthetic document artifact noise, mismatched cross-bureau issuing timestamps.

### 1.2 Frankenstein Identity (Real Fragment + Fabricated Overlay)
- **Description**: Stitched hybrid identity combining a genuine, valid government identifier (e.g., real stolen SSN/PAN fragment from data breach) with fabricated names, addresses, and burner contact endpoints.
- **GenAI Acceleration**: Automated identity permutation algorithms match valid fragmented PII with statistically plausible demographic profiles to bypass algorithmic KYC filters.
- **Target Surface**: Merchant onboarding, loan origination, card issuance.
- **Key Indicators**: Divergence between demographic profile and historical bureau credit footprint, multiple distinct names sharing identical tax identifiers.

### 1.3 Deepfake Video KYC / Liveness Bypass
- **Description**: Real-time or pre-rendered synthetic video/audio presentation attacks utilizing neural face-swapping and 3D facial avatar animation to defeat video-KYC liveness detection (blink, head turn, challenge-response).
- **GenAI Acceleration**: Modern generative models synthesize sub-millisecond facial micro-movements, lighting adaptation, and dynamic challenge-response gestures.
- **Target Surface**: Video Customer Identification Process (V-CIP), remote biometric onboarding.
- **Key Indicators**: Temporal flickering around facial boundaries, gaze vector inconsistency, unnatural eyelid motion, spectral audio-video desynchronization.

### 1.4 Synthetic Document Generation & Checksum Spoofing
- **Description**: High-fidelity rendering of government ID cards (passports, driver's licenses, utility bills) featuring algorithmic typography, holographic overlay simulation, and calculated valid checksums.
- **GenAI Acceleration**: Multi-modal layout models produce pixel-perfect template alignments with anti-forensic noise dithering that masks standard image manipulation signatures.
- **Target Surface**: Document verification microservices, optical character recognition (OCR) intake gates.
- **Key Indicators**: Font kerning micro-deviations, metadata inconsistency, unnatural compression artifact boundaries between image and text layers.

---

## 2. Vector B: Behavioral & Transaction / Fake Merchant Fraud

### 2.1 LLM-Generated Fake Merchant Storefronts & Card-Testing Hubs
- **Description**: Automated deployment of ephemeral e-commerce stores with fully synthesized product catalogs, customer reviews, legal terms, and checkout pipelines configured for payment gateway card-testing or money laundering.
- **GenAI Acceleration**: Automated web synthesis agents stand up thousands of convincing, distinct storefronts in minutes with unique SEO text and plausible merchant categories (MCC).
- **Target Surface**: Payment aggregator onboarding, payment gateway acquirers.
- **Key Indicators**: Low domain age, high product catalog lexical similarity across distributed domains, repetitive payment gateway configuration fingerprints.

### 2.2 Bust-Out Merchant Drain Patterns
- **Description**: A fraudulent merchant account mimics legitimate, low-velocity organic transactions over weeks/months to build acquirer trust and lower risk scoring thresholds, culminating in a rapid, coordinated high-value cash-out drain before chargebacks trigger.
- **GenAI Acceleration**: Automated transaction botnets simulate realistic human purchasing behavior, varying basket sizes, time intervals, and dispute-free settlement history.
- **Target Surface**: Merchant settlement accounts, instant payout APIs.
- **Key Indicators**: Abrupt inflection in transaction velocity and average ticket size relative to seasonal baseline, disproportionate surge in prepaid/cross-border card acceptance.

### 2.3 Triangulation & Stolen Card Laundering
- **Description**: The fraudulent storefront advertises real goods at discounted rates to genuine buyers, accepts legitimate customer funds, and fulfills the shipment by purchasing the merchandise from genuine retailers using stolen credit card credentials.
- **GenAI Acceleration**: LLM customer support agents interact with genuine buyers in real time while automated headless scrapers execute fraudulent fulfillment transactions across retailer checkout flows.
- **Target Surface**: E-commerce gateways, point-of-sale card acquiring networks.
- **Key Indicators**: Discrepancy between billing address and merchant shipping destination, multiple disparate billing instruments associated with identical shipping addresses.

---

## 3. Vector C: Agentic Payment Hijacking & Social Engineering

### 3.1 LLM-Personalized Phishing & Spear-Phishing Injections
- **Description**: Contextually hyper-targeted SMS/email payment diversion requests tailored with specific victim behavioral context scraped from public breach disclosures and social footprinting.
- **GenAI Acceleration**: Real-time language model synthesis achieves native colloquial phrasing, urgency calibration, and personalized invoice pretexting at massive scale.
- **Target Surface**: P2P payment requests, corporate invoice approval workflows, mobile banking users.
- **Key Indicators**: Linguistic urgency patterns, anomalous beneficiary account parameters, mismatch between sender email header reputation and signature context.

### 3.2 Real-Time Conversational Voice & Chat Support Impersonation
- **Description**: Interactive conversational AI agents impersonating bank fraud departments or tech support to manipulate victims into approving Authorized Push Payments (APP) or sharing 2FA OTP codes.
- **GenAI Acceleration**: Sub-500ms voice cloning and dynamic conversational branching counter victim hesitation and simulate convincing bank IVR soundscapes.
- **Target Surface**: Consumer push payments, retail banking customer authentication.
- **Key Indicators**: Rapid outbound telephony originating from VOIP routing blocks, concurrent login attempts from untrusted geolocation during active call session.

### 3.3 Prompt Injection & Agentic Wallet Hijacking
- **Description**: Malicious injection payloads embedded in invoices, merchant descriptions, or payment notes that trick autonomous AI purchasing agents / agentic wallets into executing unauthorized fund transfers or altering destination wallet addresses.
- **GenAI Acceleration**: Indirect prompt injection techniques exploit autonomous LLM tool-calling capabilities to execute privileged financial operations without explicit user confirmation.
- **Target Surface**: Autonomous purchasing agents, LLM-driven corporate procurement bots, autonomous crypto/fiat payment agents.
- **Key Indicators**: Hidden markdown/Unicode control sequences in transaction memo fields, unexpected divergence between human prompt intent and agent tool call execution parameters.
