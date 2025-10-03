#!/usr/bin/env python3
"""
Guardian Database Setup Script
Extends the existing Supabase setup with Guardian credentials schema
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from guardian_credentials_manager import GuardianCredentialsManager

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def setup_guardian_schema():
    """Setup Guardian credentials schema in Supabase"""
    
    print("🔧 Setting up Guardian credentials schema...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        print("📋 Guardian schema setup instructions:")
        print("1. Go to your Supabase project SQL Editor")
        print("2. Copy and paste the contents of 'guardian_credentials_schema.sql'")
        print("3. Run the SQL commands")
        print("")
        print("✅ After running the SQL, your database will have:")
        print("   - verifiable_credentials table")
        print("   - project_participants table")
        print("   - crediting_periods table")
        print("   - monitoring_periods table")
        print("   - electricity_systems table")
        print("   - power_units table")
        print("   - emissions_data table")
        print("   - credential_summary view")
        print("   - insert_guardian_credential() function")
        print("   - get_credential_details() function")
        print("   - Optimized indexes for performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

def test_guardian_schema():
    """Test Guardian credentials functionality"""
    
    print("\n🧪 Testing Guardian credentials schema...")
    
    # Sample test credential
    test_credential = {
        "id": "urn:uuid:test-credential-12345",
        "type": ["VerifiableCredential"],
        "issuer": "did:hedera:testnet:test-issuer",
        "issuanceDate": "2025-09-29T12:00:00.000Z",
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "schema:guardian-policy-v1"
        ],
        "credentialSubject": [{
            "participant_profile": {
                "summaryDescription": "Test renewable energy project",
                "sectoralScope": "Energy",
                "projectType": "Solar",
                "typeOfActivity": "Installation",
                "projectScale": "Medium",
                "locationLatitude": 31.7917,
                "locationLongitude": -7.0926,
                "locationGeoJSON": {
                    "type": "Point",
                    "coordinates": [-7.0926, 31.7917]
                },
                "projectEligibility": "Test compliance",
                "organizationName": "Test Solar Company",
                "contactPerson": "Test Person",
                "contactTitle": "Test Manager",
                "address": "Test Address, Morocco",
                "country": "Morocco",
                "telephone": "+212600000000",
                "email": "test@example.com",
                "ownership": "Test Solar Company",
                "emissionsTradingPrograms": "Test Program",
                "participationOtherGHGPrograms": "None",
                "otherEnvCredits": "No",
                "rejectedOtherGHGPrograms": "No",
                "methodologies": "Test Methodology",
                "startDate": "2025-01-01",
                "creditingPeriods": [{
                    "start": "2025-01-01",
                    "end": "2027-12-31"
                }],
                "monitoringPeriods": [{
                    "start": "2025-01-01",
                    "end": "2025-12-31"
                }],
                "monitoringPlan": "Test monitoring plan",
                "compliance": "Test compliance",
                "eligibilityCriteria": "Test criteria",
                "sustainableDevelopment": "Test development",
                "furtherInfo": "Test info",
                "EGPJ_calculation": "Test calculation",
                "leakageEmissions": 0.0,
                "emissionReductions": 5000,
                "buildMargin_mostRecentYear": 2024,
                "buildMargin_totalSystemGen": 2500000,
                "combinedMarginBuildDataAvailable": True,
                "firstCreditingPeriodData": True,
                "fossilFuelEmissions": False,
                "biomassSourceDedicatedPlantations": False,
                "averageCO2_massFraction": 0.20,
                "averageCH4_massFraction": 0.001,
                "CH4_globalWarmingPotential": 28,
                "steamProduced": 100000,
                "steamEnteringPlant": 95000,
                "steamLeavingPlant": 90000,
                "workingFluidLeakedReinjected": 250,
                "workingFluidGWP": 0,
                "integratedHydroProjects": False,
                "policyId": "test-policy-id-12345",
                "guardianVersion": "3.3.0-test",
                "@context": ["schema:guardian-policy-v1"],
                "type": "guardian-policy-v1"
            }
        }],
        "proof": {
            "type": "Ed25519Signature2018",
            "created": "2025-09-29T12:00:00Z",
            "verificationMethod": "did:hedera:testnet:test-issuer#did-root-key",
            "proofPurpose": "assertionMethod",
            "jws": "test-signature"
        }
    }
    
    try:
        manager = GuardianCredentialsManager()
        
        # Test credential validation
        if manager.validate_credential_structure(test_credential):
            print("✅ Test credential structure is valid")
            
            # Test insertion
            credential_uuid = manager.insert_credential(test_credential)
            print(f"✅ Test credential inserted with UUID: {credential_uuid}")
            
            # Test retrieval
            retrieved = manager.get_credential_by_id(test_credential['id'])
            if retrieved:
                print("✅ Test credential retrieved successfully")
                
                # Test search
                search_results = manager.search_credentials(
                    organization_name="Test Solar",
                    project_type="Solar"
                )
                if search_results:
                    print(f"✅ Search functionality working - found {len(search_results)} results")
                
                # Test location search
                location_results = manager.get_credentials_by_location(
                    lat_min=31.0, lat_max=32.0,
                    lon_min=-8.0, lon_max=-7.0
                )
                if location_results:
                    print(f"✅ Location search working - found {len(location_results)} results")
                
                # Test summary
                summary = manager.get_emission_reductions_summary()
                if summary:
                    print(f"✅ Summary statistics working - {summary.get('total_projects', 0)} projects")
                
                # Clean up test data
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                supabase.table("verifiable_credentials").delete().eq("credential_id", test_credential['id']).execute()
                print("✅ Test data cleaned up")
                
                return True
            else:
                print("❌ Failed to retrieve test credential")
                return False
        else:
            print("❌ Test credential structure validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Guardian schema test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🌞 Guardian Credentials Database Setup")
    print("=" * 60)
    
    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    print(f"📊 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 API Key: {SUPABASE_KEY[:20]}...")
    print("")
    
    # Setup Guardian schema
    if setup_guardian_schema():
        print("\n" + "=" * 60)
        
        # Test Guardian schema
        if test_guardian_schema():
            print("\n🎉 Guardian credentials setup completed successfully!")
            print("🚀 Your database is ready to store Guardian verifiable credentials")
            print("")
            print("📖 Usage examples:")
            print("   from guardian_credentials_manager import GuardianCredentialsManager")
            print("   manager = GuardianCredentialsManager()")
            print("   manager.insert_credential(your_credential_json)")
            print("   credentials = manager.list_credentials()")
            print("   summary = manager.get_emission_reductions_summary()")
        else:
            print("\n⚠️  Guardian schema setup incomplete - please run the SQL commands manually")
    else:
        print("\n❌ Setup failed - please check your credentials and try again")

if __name__ == "__main__":
    main()