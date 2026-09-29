PharmaCopilot is an AI-powered customer complaint management system that converts natural-language complaints and uploaded documents into structured complaint records, performs risk assessment, and assists quality teams with investigation and resolution.

## Problem Statement

Build an **AI-powered Customer Complaint Management application** for a pharmaceutical manufacturing environment. The application should combine a structured complaint form with an **AI co-pilot** that allows users to create, update, and enrich complaints entirely through natural-language interaction.

### Core Requirement

Users **must not manually fill or edit the complaint form**. Instead, the AI assistant must be responsible for populating and updating all complaint fields based on the user's instructions or uploaded documents.

The application must implement the following three AI tools:

### 1. Log Complaint Tool

The AI should accept a natural-language description of a customer complaint and identify the relevant information, including where applicable:

* Product name
* Product grade/strength
* Batch number
* Manufacturing date
* Expiry date
* Affected quantity
* Complaint description
* Other relevant complaint details

The AI should use its reasoning to perform a **risk assessment** based on the complaint information. The assessment should include:

* Complaint severity/risk classification
* Reasoning behind the classification
* Recommended action
* Appropriate routing, such as Quality Assurance/Quality Control
* Actions such as investigation, replacement, escalation, or other appropriate follow-up

The extracted information and risk assessment should automatically appear in the complaint form.

### 2. Edit Complaint Tool

The AI should allow users to modify an existing complaint using natural language.

For example:

> "Change the batch number to B24017 and affected quantity to 50 units."

The AI should update only the requested fields while **preserving all other previously captured complaint information**.

After an edit, the application must ensure that:

* The complaint form reflects the updated information.
* Previously entered information remains intact.
* The risk assessment is updated when the changed information affects risk.
* Unchanged parts of the original risk assessment are preserved where appropriate.

Users should never need to manually edit the form.

### 3. Document Extraction Tool

Users should be able to upload a sample document, such as a **PDF or email containing realistic pharmaceutical manufacturing/customer complaint data**.

The AI should extract relevant information from the document, such as:

* Product name
* Product grade/strength
* Batch number
* Manufacturing date
* Expiry date
* Affected quantity
* Complaint details
* Other relevant pharmaceutical data

The extracted information should automatically populate the complaint form and generate the corresponding risk assessment.

After document extraction, the user must still be able to interact with the AI using natural language to modify the complaint.

For example:

> "The affected quantity is actually 75 units, and the customer reported that the issue occurred in three separate packs."

The AI should update the relevant fields and reassess the risk if necessary.

### Expected User Experience

The application should demonstrate a **chat-first complaint workflow**:

**User provides information → AI understands it → AI populates the form → AI performs risk assessment → User makes changes through natural language → AI updates the form and assessment.**

The complaint form should therefore act primarily as a **read-only visual representation of the AI's structured output**, rather than a form that users fill in themselves.

The final application should clearly demonstrate:

1. Natural-language complaint logging.
2. AI-driven form population.
3. AI-based risk assessment and recommended actions.
4. Natural-language complaint editing.
5. Preservation of existing complaint data during edits.
6. Document upload and AI extraction.
7. Natural-language modification after document extraction.
8. Automatic synchronization between the AI conversation, complaint form, and risk assessment.

The goal is to demonstrate an end-to-end **AI co-pilot for pharmaceutical customer complaint handling**, where the AI is responsible for converting unstructured information into a structured complaint and supporting the appropriate risk-based response.

## Bonus Features — Optional

The application may include additional AI capabilities that improve the complaint-management workflow and demonstrate deeper reasoning capabilities.

Potential bonus features include:

### 1. Complaint Completeness Checker

Analyze the complaint and identify missing or insufficient information required for investigation.

For example:

> "The batch number and affected quantity are missing. Please provide them before the complaint can be fully processed."

The AI should distinguish between **required information, optional information, and information that cannot reasonably be obtained**.

### 2. AI Risk Classification

Provide an explainable risk classification such as **Low, Medium, High, or Critical**, based on factors such as complaint type, product information, affected quantity, patient/customer impact, and other relevant details.

The AI should provide a short explanation for the classification and recommend appropriate next steps.

### 3. Root Cause Recommendation

Based on the complaint details, suggest potential areas or hypotheses for investigation.

The AI should clearly identify these as **potential root causes or investigation hypotheses**, rather than presenting them as confirmed causes.

### 4. Duplicate Complaint Detection

Compare the current complaint against existing complaints and identify potentially related or duplicate cases using information such as:

* Product
* Batch number
* Complaint type
* Description
* Customer
* Date

The AI should provide a similarity indication and explain why a complaint may be related.

### 5. CAPA Recommendation

Where appropriate, recommend potential **Corrective and Preventive Actions (CAPA)** based on the complaint and risk assessment.

Recommendations should be presented as suggestions for review by the appropriate quality team rather than automatically executing CAPA actions.

### 6. Complaint Summary

Generate a concise, structured summary of the complaint containing:

* Complaint overview
* Product and batch information
* Customer-reported issue
* Affected quantity
* Risk classification
* Recommended action
* Investigation considerations

The summary should update automatically whenever the underlying complaint information changes.

### Bonus Feature Design Principle

All bonus AI capabilities should follow the same **AI-first interaction model** as the core application. Users should be able to invoke or modify these capabilities through natural language without manually editing the underlying complaint form.

For example:

> "Check if this complaint is complete."

> "Are there any similar complaints?"

> "What could be the possible root causes?"

> "Give me a complaint summary."

> "What CAPA would you recommend?"

The AI should use the latest complaint state as the source of truth so that the form, risk assessment, recommendations, and generated summaries remain synchronized.