import requests

print("# --- Step 1: Login (get refresh token) ---")
login_url = 'https://guardianservice.app/api/v1/accounts/loginByEmail'
login_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}
login_payload = {
    "email": "abderrahmanemhawar@gmail.com",
    "password": "Mhawar2001'"
}

response = requests.post(login_url, headers=login_headers, json=login_payload)
if not response.ok:
    print("Login error:", response.text)
    exit()
login_data = response.json()
refresh_token = login_data.get('login', {}).get('refreshToken')
print("Refresh token:", refresh_token)
print(" ")

print("# --- Step 2: Exchange for access token ---")
access_token_url = "https://guardianservice.app/api/v1/accounts/access-token"
access_headers = login_headers.copy()
access_payload = {
    "refreshToken": refresh_token
}
response = requests.post(access_token_url, headers=access_headers, json=access_payload)
if not response.ok:
    print("Access token error:", response.text)
    exit()
access_token = response.json().get("accessToken")
print("Access token:", access_token)
print(" ")

print("# --- Step 3: Initialize dry-run for policy ---")
policy_id = "68d69341152381fe552b21ec"
dry_run_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run"
dry_run_headers = access_headers.copy()
dry_run_headers["Authorization"] = f"Bearer {access_token}"
response = requests.put(dry_run_url, headers=dry_run_headers, json={})
print("Dry-run initialization:", response.status_code, response.json().get("isValid"))
print(" ")

print("# --- Step 4: Create Project Participant virtual user ---")
create_user_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run/user"
user_headers = dry_run_headers.copy()
user_payload = {
    "role": "Project_Participant"
}
response = requests.post(create_user_url, headers=user_headers, json=user_payload)
print("Create Project Participant user:", response.status_code)
print("Response:", response.text)
print(" ")

print("# --- Step 5: Activate/set virtual user (login as virtual) ---")
users_response = response.json()

users_response = response.json()

# Show all usernames present
print("Available virtual users:")
for user in users_response:
    print(f"username: {user['username']} (id: {user['id']}, active: {user['active']})")

chosen_username = input("Enter the username of the user to activate: ")
selected_user = next(u for u in users_response if u["username"] == chosen_username)

activate_user_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/dry-run/login"
activate_user_headers = user_headers.copy()
activate_user_payload = {
    "did": selected_user["did"],
    "username": selected_user["username"],
    "hederaAccountId": selected_user["hederaAccountId"],
    "_id": selected_user["_id"],
    "id": selected_user["id"]
}

response = requests.post(activate_user_url, headers=activate_user_headers, json=activate_user_payload)
print("Activate/set virtual user:", response.status_code)
print("Response:", response.text)
print(" ")


print("# Step 6a: Retrieve block id by tag (always up-to-date)")
choose_role_tag = "Choose_Roles"
choose_role_tag_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/tag/{choose_role_tag}"
choose_role_headers = user_headers.copy()

# Get block info for tag
response = requests.get(choose_role_tag_url, headers=choose_role_headers)
block_config = response.json()  # Should have an "id" field
choose_role_block_id = block_config["id"]

print("# Step 6b: Use the found block id for POST")
choose_role_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{choose_role_block_id}"
choose_role_payload = {
    "role": "Project Participant"
}

response = requests.post(choose_role_url, headers=choose_role_headers, json=choose_role_payload)
print("Choose Role Block:", response.status_code)
print("Response:", response.text)
print(" ")

print("# --- Step 7: Minimal Project Participant Profile Submission ---")

policy_id = "68d69341152381fe552b21ec"
create_profile_tag = "create_pp_profile"
bearer_token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OGQ1NjMwYTA4MmVlMDk5NGM1N2M4Y2YiLCJ1c2VybmFtZSI6Ik1oYXdhciIsImRpZCI6ImRpZDpoZWRlcmE6dGVzdG5ldDpHczFvaW12eHF1eVJ2OVJMYXc0c1VHYmN5dnd1V0p2SDFrUzJvcHZaa1N6dV8wLjAuNjkwMzUyMyIsInJvbGUiOiJTVEFOREFSRF9SRUdJU1RSWSIsImV4cGlyZUF0IjoxNzU5MTQ3NDg0MTk4LCJpYXQiOjE3NTkwNjEwODQsImlzcyI6Imd1YXJkaWFuc2VydmljZS5hcHAifQ.LulBHJ0q9K1XbHsVuo--vIcujtDDZfhHejdJ5H1AEfMlUcZVDlrfxf85WMP-KMT_YttbmBOyQnKOJfQgp0pfR0uknRF6mqJ8emxPCQIQQ_r5B4JAO3Kp8oadbe863nGr5KAcgJhKNpcvpwhkWjwRjRhHuhOBE6uNkaTRkUZIcSE"
headers = {
    "Authorization": bearer_token,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

# Lookup block UUID by tag
lookup_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/tag/{create_profile_tag}"
response = requests.get(lookup_url, headers=headers)
block_id = response.json()["id"]
print(f"Block UUID for '{create_profile_tag}': {block_id}")

# Prompt for VVB Name input
vvb_name = input("Enter VVB Name for Project Participant profile: ")

# Correct payload: wrap field0 inside "document"
profile_payload = {
    "document": {
        "field0": vvb_name
    }
}

send_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{block_id}"
print("POSTing payload:", profile_payload)
response = requests.post(send_url, headers=headers, json=profile_payload)
print("Status:", response.status_code)
print("Response:", response.text)

print("# --- Step 8: New Project Creation Submission ---")

policy_id = "68d69341152381fe552b21ec"
block_tag = "add_project_bnt"
lookup_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/tag/{block_tag}"
response = requests.get(lookup_url, headers=headers)
project_block_id = response.json()["id"]

headers = {
    "Authorization": bearer_token,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

# 1. GET block schema via tag
schema_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/tag/{block_tag}/blocks"
response = requests.get(schema_url, headers=headers)
block_json = response.json()
print("Raw schema API response:", block_json)

# 2. Extract schema, handle both list/dict responses
schema = None
if isinstance(block_json, list):
    schema = block_json[0].get("schema", {}).get("document", {})
elif isinstance(block_json, dict) and "schema" in block_json:
    schema = block_json.get("schema", {}).get("document", {})
else:
    print("ERROR: No 'schema' key found in API response. Check block existence and permissions.")
    exit()

required_fields = schema.get("required", [])
properties = schema.get("properties", {})
print("Required project fields:", required_fields)

# 3. Prompt for required fields interactively
project_fields = {}
for field in required_fields:
    label = properties.get(field, {}).get("title", field)
    example = properties.get(field, {}).get("examples", [""])[0]
    dtype = properties.get(field, {}).get("type", "string")
    value = input(f"Enter value for '{label}' ({field}, type={dtype}, example='{example}'): ")
    project_fields[field] = value

# 4. Wrap fields in 'document' for API POST
project_payload = {
    "document": project_fields
}

# 5. POST to block
send_url = f"https://guardianservice.app/api/v1/policies/{policy_id}/blocks/{block_id}"
print("POSTing project payload:", project_payload)
response = requests.post(send_url, headers=headers, json=project_payload)
print("Status:", response.status_code)
print("Response:", response.text)