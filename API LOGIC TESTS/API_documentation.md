# Read this first:

To **access** the block configuration you referenced (with fields like `id`, `blockType`, `tag`, etc.), you need to use the Guardian Service API endpoints for **block data retrieval within a policy context**. Here's how you can do it based on the [Swagger API docs UI] you are viewing:

**Step-by-step:**
1. **Identify the policyId:** You need the `policyId` value for the policy to which this block belongs.
2. **Get block by UUID:**  
   Use the endpoint:
   ```
   GET /policies/{policyId}/blocks/{uuid}
   ```
   - Replace `{policyId}` with your specific policy ID.
   - Replace `{uuid}` with your block's `id` field (`162beba6-b8da-49a1-9c6a-d2178b54318f`).
   - This will return the full block configuration and data.

**Alternative by tag:**
- If you have the tag name (e.g. `"Project Participant_header"`), you can also use:
   ```
   GET /policies/{policyId}/tag/{tagName}
   ```
   - This retrieves the block by its tag for the given policy.

**Typical usage (curl example):**
```bash
curl -X GET "https://guardianservice.app/api/v1/policies/<policyId>/blocks/162beba6-b8da-49a1-9c6a-d2178b54318f" \
  -H "Authorization: Bearer <your-access-token>"
```
or
```bash
curl -X GET "https://guardianservice.app/api/v1/policies/<policyId>/tag/Project Participant_header" \
  -H "Authorization: Bearer <your-access-token>"
```

**Summary:**  
- Use **GET /policies/{policyId}/blocks/{uuid}** for direct access via block ID.
- Use **GET /policies/{policyId}/tag/{tagName}** via tag.

You will need an **API token** in your Authorization header for private data.[1]

Let me know if you need help with the exact API call, policy ID lookup, or the authentication flow!

[1](https://guardianservice.app/api-docs/#/)

# and this: 

To **enter a specific dry run session** in Guardian Service for a policy, use a combination of the policy viewer URL and the Guardian API. Here’s how you do it:

**1. Policy Viewer Dry Run Session:**
- The link you posted is a direct way to launch a dry-run session in the web UI:
  ```
  https://guardianservice.app/policy-viewer/{policyId}?policyParams={encodedParams}
  ```
  - `{policyId}` is your unique policy.
  - `{policyParams}` is a URL-safe base64 encoded string of user/session params.
- Opening this URL in your browser immediately takes you to the specific dry run session with preselected virtual users and parameters.

**2. API Dry Run Endpoints:**  
If you need to control or automate dry run sessions via API (for testing, simulation, etc.), use:

- **Create virtual user for dry run:**
  ```
  POST /policies/{policyId}/dry-run/user
  ```
- **Login as dry run user:**
  ```
  POST /policies/{policyId}/dry-run/login
  ```
- **Run block in dry run mode:**
  ```
  POST /policies/{policyId}/dry-run/block
  ```
- **Get dry run history (per block/tag):**
  ```
  GET /policies/{policyId}/dry-run/block/{tagName}/history
  ```
- **Get/Set savepoints:**
  - Create: `POST /policies/{policyId}/savepoint/create`
  - Restore: `GET /policies/{policyId}/savepoint/restore`

**3. Quick Steps:**
- Launch the dry run in browser using the URL as given.
- For API calls, use your access token and the endpoints above. This lets you create, login and operate virtual dry run users and session data.

**Summary:**
- **URL method:** Instantly opens the right session on web UI.
- **API method:** Automate and simulate sessions, users, and block actions programmatically.

Let me know which exact operation you want (just UI, user creation, automation, etc.) and I can give you a sample curl or code snippet!

[1](https://guardianservice.app/api-docs/#/)

# To login: 

## api doc:

curl -X 'POST' \
  'https://guardianservice.app/api/v1/accounts/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "Mhawar",
  "password": "Mhawar2001'\''",
  "tenantId": "68cc28cc348f53cc0b247ce4"
}'
Request URL
https://guardianservice.app/api/v1/accounts/login
Server response
Code	Details
200	
Response body
Download
{
  "username": "Mhawar",
  "did": "did:hedera:testnet:Gs1oimvxquyRv9RLaw4sUGbcyvwuWJvH1kS2opvZkSzu_0.0.6903523",
  "role": "STANDARD_REGISTRY",
  "refreshToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijg1MzM5YmZhLTlkYTEtNGMzYy1iYjRjLWRlZWJmOGQwMDA3NiIsIm5hbWUiOiJNaGF3YXIiLCJleHBpcmVBdCI6MTc5MDQxNDc2MzMwNiwiaWF0IjoxNzU4ODc4NzYzfQ.RRlsdKSAcEiNLG5UIDsuNmCpqlkVqd1QEEWkNfY0KM87iDAl6sDZkCxwzO1-Ej_KoFcuoRdQoLAr-pqIUDicBaZLyLSrNw2v4aikxCeL4BI2A1-oo3D-ISzOgDLvI6KDHQnpf9AMVGFOp9Qi_9cIq5mfVGj01SVNi_jMhc11XkY",
  "weakPassword": false
}
Response headers
 content-encoding: gzip 
 content-type: application/json; charset=utf-8 
 date: Fri,26 Sep 2025 09:26:03 GMT 
 strict-transport-security: max-age=15724800; includeSubDomains 
 vary: Accept-Encoding 

 # To get the access token (which is like the api key):

## api doc:

 curl -X 'POST' \
  'https://guardianservice.app/api/v1/accounts/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "Mhawar",
  "password": "Mhawar2001'\''",
  "tenantId": "68cc28cc348f53cc0b247ce4"
}'
Request URL
https://guardianservice.app/api/v1/accounts/login
Server response
Code	Details
200	
Response body
Download
{
  "username": "Mhawar",
  "did": "did:hedera:testnet:Gs1oimvxquyRv9RLaw4sUGbcyvwuWJvH1kS2opvZkSzu_0.0.6903523",
  "role": "STANDARD_REGISTRY",
  "refreshToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijg1MzM5YmZhLTlkYTEtNGMzYy1iYjRjLWRlZWJmOGQwMDA3NiIsIm5hbWUiOiJNaGF3YXIiLCJleHBpcmVBdCI6MTc5MDQxNDc2MzMwNiwiaWF0IjoxNzU4ODc4NzYzfQ.RRlsdKSAcEiNLG5UIDsuNmCpqlkVqd1QEEWkNfY0KM87iDAl6sDZkCxwzO1-Ej_KoFcuoRdQoLAr-pqIUDicBaZLyLSrNw2v4aikxCeL4BI2A1-oo3D-ISzOgDLvI6KDHQnpf9AMVGFOp9Qi_9cIq5mfVGj01SVNi_jMhc11XkY",
  "weakPassword": false
}
Response headers
 content-encoding: gzip 
 content-type: application/json; charset=utf-8 
 date: Fri,26 Sep 2025 09:26:03 GMT 
 strict-transport-security: max-age=15724800; includeSubDomains 
 vary: Accept-Encoding 

 # Maybe this is a way to get api token:

## api doc:

 POST
/accounts/sso/generate
Generate API token for Indexer.


Generate API token for Indexer.

Parameters
Cancel
Name	Description
expire
number
(path)
Expire time for a token in days. If not set, default value is 14 days.

14
callbackUrl *
string
(path)
Callback url for a token usage. Host must be in allowed hosts list.

https://indexer.guardianservice.app/sso
Execute
Clear
Responses
Curl

curl -X 'POST' \
  'https://guardianservice.app/api/v1/accounts/sso/generate' \
  -H 'accept: application/json' \
  -d ''
Request URL
https://guardianservice.app/api/v1/accounts/sso/generate
Server response
Code	Details
401	
Error: response status is 401

Response body
Download
{
  "message": "Unauthorized",
  "statusCode": 401
}
Response headers
 content-length: 43 
 content-type: application/json; charset=utf-8 
 date: Sat,27 Sep 2025 09:53:38 GMT 
 strict-transport-security: max-age=15724800; includeSubDomains 
Responses
Code	Description	Links
200	
Successful operation.

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "success": true,
  "token": "string"
}
No links
401	
Unauthorized.

No links
403	
Forbidden.

No links
451	
Unavailable for Legal Reasons. User must accept new terms of use.

Media type

application/json
Example Value
Schema
{
  "code": "string",
  "details": {}
}
No links
500	
Internal server error.

Media type

application/json
Example Value
Schema
{
  "code": 500,
  "message": "Error message"
}

# Policy:

## the actual json and id values: 

{
"id": "68d69341152381fe552b21ec",
"uuid": "aef9157e-a9b6-41b2-9f77-526e01a622c3",
"name": "AMS-I.D 1758892865729",
"version": "Dry Run",
"description": "AMS-I.D",
"topicDescription": "AMS-I.D",
"projectSchema": "#161f2947-f16c-4601-9c4c-3545f286a55c",
"categories": [],
"status": "DRY-RUN",
"creator": "did:hedera:testnet:Gs1oimvxquyRv9RLaw4sUGbcvywwJvH1kLS2opvZkSzu.0.6903523",
"owner": "did:hedera:testnet:Gs1oimvxquyRv9RLaw4sUGbcvywwJvH1kLS2opvZkSzu.0.6903523",
"topicId": "0.0.691085",
"instanceTopicId": "0.0.17588967928617",
"synchronizationTopicId": null,
"policyTag": "Tag_1758892865729",
"codeVersion": "1.0.0",
"createdAt": "2025-09-26T13:21:05.744Z",
"policyRoles": [here is full actualy],
"policyNavigation": [here is full actualy],
"policyTokens": [here is full actualy],
"policyGroups": [here is full actualy],
"config": {here is full actualy}
}

# First we have pp step as header

## the actual json and id values: 

{
  "id": "162beba6-b8da-49a1-9c6a-d2178b54318f",
  "blockType": "interfaceContainerBlock",
  "defaultActive": true,
  "uiMetaData": {
    "type": "tabs"
  },
  "permissions": [
    "Project Participant"
  ],
  "onErrorAction": "no-action",
  "tag": "Project Participant_header"
}

# then we have pp step

{
  "id": "3fdb9779-391e-48f7-a5a3-e02b54596f68",
  "blockType": "interfaceDocumentsSourceBlock",
  "defaultActive": true,
  "uiMetaData": {
    "fields": [
      {
        "title": "Owner",
        "name": "document.issuer",
        "tooltip": "",
        "type": "text"
      },
      {
        "title": "Text",
        "name": "document.credentialSubject.0.field0",
        "tooltip": "",
        "type": "text"
      },
      {
        "title": "Operation",
        "name": "",
        "tooltip": "",
        "type": "block",
        "action": "",
        "url": "",
        "dialogContent": "",
        "dialogClass": "",
        "dialogType": "",
        "bindBlock": "pp_revoke_profile",
        "bindGroup": "pp_documents"
      },
      {
        "title": "Operation",
        "name": "option.status",
        "tooltip": "",
        "type": "text",
        "action": "",
        "url": "",
        "dialogContent": "",
        "dialogClass": "",
        "dialogType": "",
        "bindBlock": "",
        "width": "250px"
      },
      {
        "title": "Document",
        "name": "document",
        "tooltip": "",
        "type": "button",
        "action": "dialog",
        "url": "",
        "dialogContent": "VC",
        "dialogClass": "",
        "dialogType": "json",
        "bindBlock": "",
        "content": "View Document",
        "uiClass": "link"
      }
    ]
  },
  "permissions": [
    "Project Participant"
  ],
  "dependencies": [
    "save_new_approve_document"
  ],
  "onErrorAction": "no-action",
  "tag": "pp_profile_grid"
}

## the actual json and id values: 
{
  "id": "bd54ae71-d750-49b6-996f-eb21e3439853",
  "blockType": "interfaceStepBlock",
  "defaultActive": true,
  "permissions": [
    "Project Participant"
  ],
  "onErrorAction": "no-action",
  "uiMetaData": {},
  "tag": "pp_step"
}

# Create a New PP (This is the id of creating new PP):

## the actual json and id values:

POST & GET
{
  "id": "70b59a78-d1db-463e-a41f-723d9b421818",
  "blockType": "requestVcDocumentBlock",
  "defaultActive": true,
  "uiMetaData": {
    "privateFields": [],
    "type": "page",
    "title": "New PP"
  },
  "permissions": [
    "Project Participant"
  ],
  "idType": "OWNER",
  "schema": "#8244680f-1cd2-406a-af15-374f76b86d00",
  "onErrorAction": "no-action",
  "presetFields": [
    {
      "name": "field0",
      "title": "VVB Name",
      "value": "field0",
      "readonly": false
    }
  ],
  "preset": true,
  "presetSchema": "#291acfd0-6568-42f8-a064-240c9368cc1b",
  "tag": "create_pp_profile"
}

# the status for the waiting for approval:

## the actual json and id values:

GET only
{
  "id": "0eb44b50-c2ef-4aa1-b384-f516ab62d05b",
  "blockType": "informationBlock",
  "defaultActive": true,
  "permissions": [
    "Project Participant"
  ],
  "uiMetaData": {
    "title": "Waiting for approval",
    "description": "Waiting for approval",
    "type": "text"
  },
  "stopPropagation": true,
  "onErrorAction": "no-action",
  "tag": "pp_wait_for_approve"
}

