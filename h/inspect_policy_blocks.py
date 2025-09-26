#!/usr/bin/env python3
"""
Inspect AMS-I.D Policy Blocks
Retrieves and displays all available blocks in the AMS-I.D policy
"""

import json
from ams_id_aggregator import AMSIDAggregator, AMSIDConfig

def main():
    """Main inspection function"""
    print("🔍 AMS-I.D Policy Block Inspector")
    print("=" * 50)
    
    # Create aggregator and authenticate
    config = AMSIDConfig.from_file()
    aggregator = AMSIDAggregator(config)
    
    print("🔐 Authenticating with Guardian...")
    if not aggregator.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    # Get policy blocks
    print(f"\n📋 Retrieving blocks for policy: {config.policy_id}")
    blocks = aggregator.get_policy_blocks()
    
    if not blocks:
        print("❌ No blocks retrieved!")
        return
    
    print(f"✅ Retrieved {len(blocks)} blocks")
    
    # Display blocks in a structured way
    print(f"\n📊 Policy Block Structure:")
    print("-" * 80)
    
    # Look for blocks with tags
    tagged_blocks = []
    for i, block in enumerate(blocks):
        if isinstance(block, dict):
            block_type = block.get('blockType', 'unknown')
            block_tag = block.get('tag', '')
            block_id = block.get('id', '')
            
            if block_tag:
                tagged_blocks.append({
                    'index': i,
                    'type': block_type,
                    'tag': block_tag,
                    'id': block_id
                })
                
                print(f"  [{i:2d}] {block_type:<25} | {block_tag:<30} | {block_id}")
    
    # Show target blocks we're looking for
    print(f"\n🎯 Target Blocks (from config):")
    print("-" * 50)
    target_blocks = {
        'Project Creation': config.project_creation_block,
        'Report Creation': config.report_creation_block,
        'Project Validation': config.project_validation_block,
        'Report Verification': config.report_verification_block
    }
    
    for name, tag in target_blocks.items():
        found = any(block['tag'] == tag for block in tagged_blocks)
        status = "✅ FOUND" if found else "❌ NOT FOUND"
        print(f"  {status} {name:<20} | {tag}")
    
    # Show all available tags for reference
    print(f"\n📝 All Available Block Tags:")
    print("-" * 50)
    all_tags = sorted(set(block['tag'] for block in tagged_blocks if block['tag']))
    
    for i, tag in enumerate(all_tags, 1):
        print(f"  {i:2d}. {tag}")
    
    # Look for likely candidates
    print(f"\n🔍 Likely Block Candidates:")
    print("-" * 50)
    
    keywords = {
        'project': ['project', 'add_project', 'create_project'],
        'report': ['report', 'add_report', 'create_report', 'monitoring'],
        'validation': ['validate', 'approval', 'approve'],
        'verification': ['verify', 'verification']
    }
    
    for category, search_terms in keywords.items():
        print(f"\n  {category.upper()} blocks:")
        matches = []
        for block in tagged_blocks:
            tag_lower = block['tag'].lower()
            if any(term in tag_lower for term in search_terms):
                matches.append(block)
        
        if matches:
            for match in matches:
                print(f"    • {match['tag']} ({match['type']})")
        else:
            print(f"    • No matches found")
    
    # Save detailed block info to file
    output_file = "ams_id_blocks_detailed.json"
    with open(output_file, 'w') as f:
        json.dump(blocks, f, indent=2)
    
    print(f"\n💾 Detailed block information saved to: {output_file}")
    print(f"\n✅ Inspection complete!")

if __name__ == "__main__":
    main()