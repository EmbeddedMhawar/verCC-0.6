Here’s your **end-to-end, explicit workflow for integrating Python → mrv-sender → Guardian, including how to get PolicyID, blockId for monitoring report, and schemaId using API endpoints or YAML/JSON:**

***

## **Workflow Overview**

### **1. Prepare Guardian Policy and IDs**

- **PolicyID:**  
  Extracted from policy YAML/JSON or UI:  
  - e.g. `68d5ba75152381fe552b1c6d`

- **BlockId (Monitoring Report):**  
  Find the block used for "Add Monitoring Report" in your policy config;  
  - Example block label: `addreportbnt`
  - Search for its `id` attribute, e.g. `1021939c-b948-4732-bd5f-90cc4ae1cd50`
  - Validate in UI (Monitor Reports/add report button typically points to this block).

- **SchemaId:**  
  The schema for monitoring report submissions is listed in the block config:  
  - Example: `3b99fd4b-8285-4b91-a84f-99ecec076f4b` (sometimes versioned as `3b99fd4b-8285-4b91-a84f-99ecec076f4b1.0.0`)

***

### **2. Authenticate Against Guardian API**

- **Login (get refreshToken):**
  ```bash
  curl -X POST \
    'https://guardianservice.app/api/v1/accounts/login' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "username": "Mhawar",
      "password": "Mhawar2001'",
      "tenantId": "68cc28cc348f53cc0b247ce4"
    }'
  ```

- **Request accessToken:**
  ```bash
  curl -X POST 'https://guardianservice.app/api/v1/accounts/access-token' \
    -H "Content-Type: application/json" \
    -d '{"refreshToken":"YOUR_REFRESH_TOKEN"}'
  ```
- Use accessToken for all further API calls.

***

### **3. Run mrv-sender on Your PC**

- Download and run mrv-sender:
  ```bash
  git clone https://github.com/hashgraph/guardian.git
  cd guardian/mrv-sender
  npm install
  npm start
  ```

***

### **4. Python Backend Sends Data to mrv-sender**

- Your Python code could look like:
  ```python
  import requests

  data = {
      "field0": "ProjectID123",  # Map to schema
      # add other fields based on your schemaId!
  }

  resp = requests.post("http://localhost:3005/mrv-generate", json=data)
  print(resp.status_code, resp.text)
  ```
- mrv-sender receives, wraps as Verifiable Credential, and forwards to Guardian.

***

### **5. mrv-sender to Guardian Submission**

- mrv-sender POSTs to Guardian using:
  ```
  https://guardianservice.app/api/v1/policies/<PolicyID>/blocks/<blockId>/external
  ```
  and puts your Bearer accessToken in the `Authorization` header.

***

### **6. Monitor and Approve in Guardian UI**

- Log into Guardian
- Check for incoming MRV (monitoring report) under AMS-I.D policy
- Approve and mint tokens as needed in workflow

***

### **How to Find IDs in YAML/JSON**

See : C:\Users\mhawa\OneDrive\Bureau\FairDer (akram's fork)\verCC 0.6\h\AMS-I-D.yaml

- **PolicyID:**  
  Top-level key, `id: ...`
- **BlockId:**  
  Under "steps" or "children" in blocks, look for document/upload/report block with id attribute.
- **SchemaId:**  
  In blocks of type `requestVcDocumentBlock` for reports, under `schema: ...`

Sample snippet:
```
- id: 1021939c-b948-4732-bd5f-90cc4ae1cd50
  blockType: requestVcDocumentBlock
  schema: 3b99fd4b-8285-4b91-a84f-99ecec076f4b
  tag: addreportbnt
```

***

### **API Endpoint Summary**

- Login: `/api/v1/accounts/login`
- Get access token: `/api/v1/accounts/access-token`
- Add monitoring report: `/api/v1/policies/<PolicyID>/blocks/<blockId>/external`

All request bodies must match the expected schema for `schemaId`.

***

**This process lets you automate end-to-end MRV reporting with Python, mrv-sender, and Guardian, perfectly mapped to your AMS-I.D renewable energy policy setup. If you want an exact Python payload according to your schema fields, just ask!**

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/75042773/3111564d-9b6f-4430-b8d4-64bf0c2e2c2e/paste.txt)