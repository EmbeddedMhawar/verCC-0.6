#!/usr/bin/env python3
"""
Get Full AMS-I.D Policy Configuration
Downloads the complete policy configuration to find correct block tags
"""

import json
import requests
from ams_id_aggregator import AMSIDAggregator, AMSIDConfig

def main():
    """Main function to get policy configuration"""
    print("📥 AMS-I.D Policy Configuration Downloader")
    print("=" * 50)
    
    # Create aggregator and authenticate
    config = AMSIDConfig.from_file()
    aggregator = AMSIDAggregator(config)
    
    print("🔐 Authenticating with Guardian...")
    if not aggregator.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    # Try to get the full policy configuration
    print(f"\n📋 Getting policy configuration for: {config.policy_id}")
    
    try:
        # Try the export/file endpoint
        endpoint = f"{config.guardian_base_url}/policies/{config.policy_id}/export/file"
        
        headers = {
            "Authorization": f"Bearer {aggregator.guardian_client.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            policy_data = response.json()
            
            # Save to file
            with open("ams_id_policy_full.json", "w") as f:
                json.dump(policy_data, f, indent=2)
            
            print("✅ Policy configuration downloaded successfully!")
            print("💾 Saved to: ams_id_policy_full.json")
            
            # Analyze the structure
            analyze_policy_structure(policy_data)
            
        else:
            print(f"❌ Failed to get policy configuration: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try alternative endpoint - get policy by ID
            try_alternative_endpoints(aggregator, config)
    
    except Exception as e:
        print(f"❌ Error getting policy configuration: {e}")
        try_alternative_endpoints(aggregator, config)

def try_alternative_endpoints(aggregator, config):
    """Try alternative endpoints to get policy information"""
    print("\n🔄 Trying alternative endpoints...")
    
    endpoints_to_try = [
        f"/policies/{config.policy_id}",
        f"/policies/{config.policy_id}/export/message",
        f"/policies"
    ]
    
    for endpoint_path in endpoints_to_try:
        try:
            endpoint = f"{config.guardian_base_url}{endpoint_path}"
            
            headers = {
                "Authorization": f"Bearer {aggregator.guardian_client.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(endpoint, headers=headers)
            
            print(f"\n📡 Trying: {endpoint_path}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Save successful response
                filename = f"policy_response_{endpoint_path.replace('/', '_')}.json"
                with open(filename, "w") as f:
                    json.dump(data, f, indent=2)
                
                print(f"   ✅ Success! Saved to: {filename}")
                
                # If this is the policies list, look for our policy
                if endpoint_path == "/policies" and isinstance(data, list):
                    our_policy = None
                    for policy in data:
                        if policy.get("id") == config.policy_id:
                            our_policy = policy
                            break
                    
                    if our_policy:
                        print(f"   📋 Found our policy: {our_policy.get('name', 'Unknown')}")
                        print(f"   📊 Status: {our_policy.get('status', 'Unknown')}")
                        
                        # Save just our policy
                        with open("our_ams_id_policy.json", "w") as f:
                            json.dump(our_policy, f, indent=2)
                        
                        analyze_policy_structure(our_policy)
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def analyze_policy_structure(policy_data):
    """Analyze policy structure to find block tags"""
    print(f"\n🔍 Analyzing Policy Structure...")
    print("-" * 50)
    
    def find_blocks_recursive(obj, path=""):
        """Recursively find all blocks with tags"""
        blocks_found = []
        
        if isinstance(obj, dict):
            # Check if this is a block with a tag
            if "blockType" in obj and "tag" in obj:
                block_info = {
                    "path": path,
                    "blockType": obj["blockType"],
                    "tag": obj["tag"],
                    "id": obj.get("id", ""),
                    "uiMetaData": obj.get("uiMetaData", {})
                }
                blocks_found.append(block_info)
            
            # Recursively search in all values
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                blocks_found.extend(find_blocks_recursive(value, new_path))
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                blocks_found.extend(find_blocks_recursive(item, new_path))
        
        return blocks_found
    
    # Find all blocks
    all_blocks = find_blocks_recursive(policy_data)
    
    if all_blocks:
        print(f"✅ Found {len(all_blocks)} blocks with tags:")
        print()
        
        # Group by block type
        by_type = {}
        for block in all_blocks:
            block_type = block["blockType"]
            if block_type not in by_type:
                by_type[block_type] = []
            by_type[block_type].append(block)
        
        # Display by type
        for block_type, blocks in by_type.items():
            print(f"  📦 {block_type} ({len(blocks)} blocks):")
            for block in blocks:
                title = block["uiMetaData"].get("title", "")
                title_str = f" - {title}" if title else ""
                print(f"    • {block['tag']}{title_str}")
            print()
        
        # Look for likely candidates
        print("🎯 Likely Block Candidates:")
        print("-" * 30)
        
        keywords = {
            "Project Creation": ["project", "add_project", "create_project", "new_project"],
            "Report Creation": ["report", "add_report", "create_report", "monitoring"],
            "Project Validation": ["validate", "approval", "approve", "project"],
            "Report Verification": ["verify", "verification", "approve", "report"]
        }
        
        for category, search_terms in keywords.items():
            print(f"\n  {category}:")
            matches = []
            for block in all_blocks:
                tag_lower = block["tag"].lower()
                title_lower = block["uiMetaData"].get("title", "").lower()
                
                if any(term in tag_lower or term in title_lower for term in search_terms):
                    matches.append(block)
            
            if matches:
                for match in matches:
                    title = match["uiMetaData"].get("title", "")
                    title_str = f" ({title})" if title else ""
                    print(f"    ✅ {match['tag']}{title_str}")
            else:
                print(f"    ❌ No matches found")
        
        # Save block summary
        with open("ams_id_blocks_summary.json", "w") as f:
            json.dump(all_blocks, f, indent=2)
        
        print(f"\n💾 Block summary saved to: ams_id_blocks_summary.json")
    
    else:
        print("❌ No blocks with tags found in policy structure")

if __name__ == "__main__":
    main()