# GripWise Demo Script (3 Minutes)

This script provides a structured narrative designed to hit every judging criteria for both the Tata Imagination Challenge (Safety Awareness) and Eurogrip TORQ Challenge 4.0 (Trust and Mechanic Engagement) within a strict 3-minute window.

## Prerequisites
- Start the backend from the project root: `python -m uvicorn backend.main:app --reload`
- Start the frontend: `cd frontend && npm run dev`
- Ensure no real user data exists in the local database.

---

## 0:00 - 0:30 | The Rider's Dilemma
**Narrator/Presenter**: 
"Welcome to GripWise, a platform designed to bridge the trust gap between everyday riders and tyre maintenance. For many riders, knowing when a tyre is unsafe feels like guesswork. Let's step into the shoes of Rahul, an everyday scooter rider."

**Action**: 
- Open the application and sign up as a **RIDER** (Rahul).
- Register a vehicle (Honda Activa).
- Navigate to the **New Inspection** tab.

## 0:30 - 1:15 | AI-Assisted Safety
**Narrator/Presenter**: 
"Rahul notices his front tyre feels a bit slippery in the rain, but he's not sure if it needs replacing. He takes a photo using his smartphone and uploads it to GripWise."

**Action**:
- Upload an image of a moderately worn tyre (use a test image).
- *Wait for the "Processing" animation to complete.*
- Show the **Inspection Report**. 

**Narrator/Presenter**: 
"Our AI pipeline analyzes the tread depth proxy and searches for anomalies. It gives Rahul an immediate, easy-to-understand recommendation: 'Monitor Closely'. It highlights potential wear but doesn't force a panic purchase. Instead, it advises him to get it verified by a professional."

## 1:15 - 2:00 | Bridging the Trust Gap (Mechanic Handoff)
**Narrator/Presenter**: 
"Here's where the Eurogrip TORQ challenge really shines. We aren't replacing mechanics; we are empowering them. Rahul decides to visit 'Mike's Tyres'. To share his data securely, he grants Mike explicit, temporary access."

**Action**:
- In the Rider Dashboard, navigate to **Mechanic Access**.
- Generate/Grant access to "Mike's Tyres".
- *Switch browsers or open an Incognito window.*
- Log in as **MECHANIC** (Mike).

## 2:00 - 2:30 | The Mechanic's Workspace & Verification
**Narrator/Presenter**: 
"On Mike's tablet, Rahul's vehicle instantly appears in the active queue. Mike can see the AI's preliminary findings, giving him immediate context. He physically inspects the tyre and confirms the wear is significant on the right side."

**Action**:
- As Mike, click on Rahul's inspection in the Service Queue (`/mechanic/dashboard`).
- Add a **Physical Finding**: "Tread depth at 1.8mm. Suggest replacement."
- Log a **Service Record**: "Tyre Replaced - OEM Compatible".

## 2:30 - 3:15 | GripWise Saathi — Mechanic Advocacy & Engagement (Eurogrip TORQ 4.0)
**Narrator/Presenter**:
"Now, let's explore **GripWise Saathi**, our dedicated mechanic advocacy module designed for Case Study 4. Instead of transactional cash discounts, Saathi empowers mechanics as recognized safety champions."

**Action**:
- Click on **GripWise Saathi** in the navigation header (`/mechanic/saathi`).
- **Advocacy Dashboard**: Highlight Mike's real Engagement Points, his current **Participation Tier** (e.g. Bronze -> Silver), and unlocked digital badges like *Physical Diagnostic Pro* and *Verified Workshop*.
- **Tyre-Care Learning Hub**: Open the module *"Tread Wear Patterns, TWI & Safety Limits"*. Show the plain-language technical guidance (ISO/ETRTO standards), answer the 3-question quiz, and watch the score (+50 points) and *Knowledge Pioneer* badge unlock instantly!
- **Customer Follow-Ups**: Show the consent-aware follow-up tracker where Mike schedules upcoming monsoon tyre checks for his customers without collecting invasive personal data.
- **Eurogrip TORQ 4.0 Concept**: Show the proposed tool-support initiatives (digital tread depth gauges and calibrated PSI stations) that a tyre brand can sponsor to elevate local workshops.

## 3:15 - 3:30 | The Trust Loop & Conclusion
**Narrator/Presenter**:
"Back on Rahul's phone, the inspection carries a 'Mechanic Verified' badge and permanent service record. Rahul revokes temporary consent feeling in complete control. For Eurogrip, mechanics become passionate advocates driven by accredited pride and precision tools. This is GripWise Saathi: AI safety for riders, professional advocacy for mechanics, and lasting trust for the tyre brand. Thank you."

**Action**:
- Switch back to Rider (Rahul).
- Show the "Mechanic Verified" badge and Service History.
- Revoke Mechanic Access.
- End Demo.
