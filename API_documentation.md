# To login: 

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

# Create a New PP (This is the id of creating new PP)

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