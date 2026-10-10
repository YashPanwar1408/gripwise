# GripWise Demo Script (3 Minutes)

This script provides a structured narrative designed to hit every judging criteria for both the Tata Imagination Challenge (Safety Awareness) and Eurogrip TORQ Challenge 4.0 (Trust and Mechanic Engagement) within a strict 3-minute window.

## Prerequisites
- Start the backend: `cd backend && python -m uvicorn main:app --reload`
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

## 2:00 - 2:40 | The Mechanic's Workspace & Verification
**Narrator/Presenter**: 
"On Mike's tablet, Rahul's vehicle instantly appears in the active queue. Mike can see the AI's preliminary findings, giving him immediate context. He physically inspects the tyre and confirms the wear is significant on the right side."

**Action**:
- As Mike, click on Rahul's inspection.
- Add a **Physical Finding**: "Tread depth at 1.8mm. Suggest replacement."
- Log a **Service Record**: "Tyre Replaced - Eurogrip Pro".

## 2:40 - 3:00 | The Trust Loop & Conclusion
**Narrator/Presenter**:
"Back on Rahul's phone, the inspection now carries a 'Mechanic Verified' badge. He can see the permanent service record in his vehicle's history. He revokes the temporary access, feeling completely in control of his data and confident in his purchase. This is GripWise: Explainable AI safety for the rider, verifiable engagement for the mechanic, and unshakeable trust for the brand. Thank you."

**Action**:
- Switch back to Rider (Rahul).
- Show the "Verified" badge and Service History.
- Revoke Mechanic Access.
- End Demo.
