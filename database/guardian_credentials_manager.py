#!/usr/bin/env python3
"""
Guardian API Verifiable Credentials Database Manager
Handles insertion, retrieval, and management of Guardian credentials
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GuardianCredentialsManager:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def insert_credential(self, credential_data: Dict[str, Any]) -> str:
        """
        Insert a complete Guardian verifiable credential into the database
        
        Args:
            credential_data: The complete credential JSON object
            
        Returns:
            str: The UUID of the inserted credential
        """
        try:
            # Use the PostgreSQL function to insert the complete credential
            result = self.supabase.rpc(
                'insert_guardian_credential',
                {'credential_json': credential_data}
            ).execute()
            
            if result.data:
                credential_uuid = result.data
                print(f"✅ Successfully inserted credential: {credential_uuid}")
                return credential_uuid
            else:
                raise Exception("No UUID returned from insertion")
                
        except Exception as e:
            print(f"❌ Error inserting credential: {e}")
            raise
    
    def get_credential_by_id(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a complete credential by its ID
        
        Args:
            credential_id: The credential ID (urn:uuid format)
            
        Returns:
            Dict containing all credential data or None if not found
        """
        try:
            result = self.supabase.rpc(
                'get_credential_details',
                {'credential_id_param': credential_id}
            ).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving credential: {e}")
            return None
    
    def list_credentials(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all credentials with basic information
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of credential summaries
        """
        try:
            result = self.supabase.from_("credential_summary")\
                .select("*")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error listing credentials: {e}")
            return []
    
    def search_credentials(self, 
                          organization_name: Optional[str] = None,
                          project_type: Optional[str] = None,
                          country: Optional[str] = None,
                          sectoral_scope: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search credentials by various criteria
        
        Args:
            organization_name: Filter by organization name
            project_type: Filter by project type (Wind, Solar, etc.)
            country: Filter by country
            sectoral_scope: Filter by sectoral scope
            
        Returns:
            List of matching credentials
        """
        try:
            query = self.supabase.from_("credential_summary").select("*")
            
            if organization_name:
                query = query.ilike("organization_name", f"%{organization_name}%")
            if project_type:
                query = query.eq("project_type", project_type)
            if country:
                query = query.eq("country", country)
            if sectoral_scope:
                query = query.eq("sectoral_scope", sectoral_scope)
            
            result = query.order("created_at", desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error searching credentials: {e}")
            return []
    
    def get_credentials_by_location(self, 
                                   lat_min: float, lat_max: float,
                                   lon_min: float, lon_max: float) -> List[Dict[str, Any]]:
        """
        Get credentials within a geographic bounding box
        
        Args:
            lat_min, lat_max: Latitude range
            lon_min, lon_max: Longitude range
            
        Returns:
            List of credentials within the specified area
        """
        try:
            result = self.supabase.from_("credential_summary")\
                .select("*")\
                .gte("location_latitude", lat_min)\
                .lte("location_latitude", lat_max)\
                .gte("location_longitude", lon_min)\
                .lte("location_longitude", lon_max)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error searching by location: {e}")
            return []
    
    def get_emission_reductions_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of emission reductions across all credentials
        
        Returns:
            Dictionary with summary statistics
        """
        try:
            result = self.supabase.from_("project_participants")\
                .select("emission_reductions, project_type, country")\
                .execute()
            
            if not result.data:
                return {}
            
            total_reductions = sum(float(r['emission_reductions'] or 0) for r in result.data)
            
            # Group by project type
            by_type = {}
            by_country = {}
            
            for record in result.data:
                project_type = record.get('project_type', 'Unknown')
                country = record.get('country', 'Unknown')
                reductions = float(record.get('emission_reductions', 0))
                
                by_type[project_type] = by_type.get(project_type, 0) + reductions
                by_country[country] = by_country.get(country, 0) + reductions
            
            return {
                'total_emission_reductions': total_reductions,
                'total_projects': len(result.data),
                'by_project_type': by_type,
                'by_country': by_country
            }
            
        except Exception as e:
            print(f"❌ Error getting emission reductions summary: {e}")
            return {}
    
    def validate_credential_structure(self, credential_data: Dict[str, Any]) -> bool:
        """
        Validate that the credential has the required structure
        
        Args:
            credential_data: The credential JSON to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['id', 'type', 'issuer', 'issuanceDate', 'credentialSubject']
        
        for field in required_fields:
            if field not in credential_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check credential subject structure
        if not credential_data.get('credentialSubject'):
            print("❌ Missing credentialSubject")
            return False
        
        if not isinstance(credential_data['credentialSubject'], list):
            print("❌ credentialSubject must be an array")
            return False
        
        if len(credential_data['credentialSubject']) == 0:
            print("❌ credentialSubject array is empty")
            return False
        
        participant_profile = credential_data['credentialSubject'][0].get('participant_profile')
        if not participant_profile:
            print("❌ Missing participant_profile in credentialSubject")
            return False
        
        return True

def main():
    """Example usage of the GuardianCredentialsManager"""
    
    # Sample credential data (your provided JSON)
    sample_credential = {
        "id": "urn:uuid:project-participant-uuid",
        "type": ["VerifiableCredential"],
        "issuer": "did:hedera:testnet:issuer-id",
        "issuanceDate": "2025-09-29T10:57:00.000Z",
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "schema:guardian-policy-v1"
        ],
        "credentialSubject": [{
            "participant_profile": {
                "summaryDescription": "Renewable power plant for grid decarbonization",
                "sectoralScope": "Energy",
                "projectType": "Wind",
                "typeOfActivity": "Installation",
                "projectScale": "Large",
                "locationLatitude": 33.5731,
                "locationLongitude": -7.5898,
                "locationGeoJSON": {
                    "type": "Point",
                    "coordinates": [-7.5898, 33.5731]
                },
                "projectEligibility": "Complies with AMS-I.D.",
                "organizationName": "Green Energy Morocco Ltd",
                "contactPerson": "Fatima Zahra",
                "contactTitle": "Project Manager",
                "address": "123 Renewable Blvd, Casablanca",
                "country": "Morocco",
                "telephone": "+212612345678",
                "email": "contact@greenenergy.ma",
                "ownership": "Green Energy Morocco Ltd",
                "emissionsTradingPrograms": "iREC",
                "participationOtherGHGPrograms": "None",
                "otherEnvCredits": "No",
                "rejectedOtherGHGPrograms": "No",
                "methodologies": "AMS-I.D 1758892865729",
                "startDate": "2025-01-01",
                "creditingPeriods": [{
                    "start": "2025-01-01",
                    "end": "2030-12-31"
                }],
                "monitoringPeriods": [{
                    "start": "2025-01-01",
                    "end": "2025-12-31"
                }],
                "monitoringPlan": "Monthly reporting to regulator",
                "compliance": "Complies with national RE law",
                "eligibilityCriteria": "Plant registered with national grid",
                "sustainableDevelopment": "Provides jobs, clean energy",
                "furtherInfo": "ISO 14001 Certified",
                "EGPJ_calculation": "Greenfield power plants",
                "leakageEmissions": 0.0,
                "emissionReductions": 10000,
                "buildMargin_mostRecentYear": 2024,
                "buildMargin_totalSystemGen": 5000000,
                "tool_07": {
                    "electricitySystemInfo": "National interconnected system",
                    "hourlyOrAnnualData": "Hourly",
                    "buildMargin": {
                        "mostRecentYearGen": 2024,
                        "totalSystemGen": 5000000,
                        "powerUnits": [{
                            "type": "Wind",
                            "commissioned": "2023-05-01",
                            "generation": 400000,
                            "capacity": 70
                        }]
                    }
                },
                "combinedMarginBuildDataAvailable": True,
                "firstCreditingPeriodData": True,
                "projectActivityType": "Wind",
                "fossilFuelEmissions": False,
                "biomassSourceDedicatedPlantations": False,
                "averageCO2_massFraction": 0.25,
                "averageCH4_massFraction": 0.001,
                "CH4_globalWarmingPotential": 28,
                "steamProduced": 200000,
                "steamEnteringPlant": 190000,
                "steamLeavingPlant": 185000,
                "workingFluidLeakedReinjected": 500,
                "workingFluidGWP": 0,
                "integratedHydroProjects": False,
                "policyId": "68d69341152381fe552b21ec",
                "guardianVersion": "3.3.0-rc",
                "@context": ["schema:guardian-policy-v1"],
                "type": "guardian-policy-v1"
            }
        }],
        "proof": {
            "type": "Ed25519Signature2018",
            "created": "2025-09-29T10:57:00Z",
            "verificationMethod": "did:hedera:testnet:issuer-id#did-root-key",
            "proofPurpose": "assertionMethod",
            "jws": "example-signature"
        }
    }
    
    try:
        manager = GuardianCredentialsManager()
        
        print("🌞 Guardian Credentials Manager - Demo")
        print("=" * 50)
        
        # Validate credential structure
        if manager.validate_credential_structure(sample_credential):
            print("✅ Credential structure is valid")
            
            # Insert the credential
            credential_uuid = manager.insert_credential(sample_credential)
            print(f"✅ Inserted credential with UUID: {credential_uuid}")
            
            # Retrieve the credential
            retrieved = manager.get_credential_by_id(sample_credential['id'])
            if retrieved:
                print("✅ Successfully retrieved credential")
                print(f"   Organization: {retrieved['participant_data']['organization_name']}")
                print(f"   Project Type: {retrieved['participant_data']['project_type']}")
                print(f"   Emission Reductions: {retrieved['participant_data']['emission_reductions']}")
            
            # List all credentials
            credentials = manager.list_credentials(limit=10)
            print(f"✅ Found {len(credentials)} total credentials")
            
            # Get emission reductions summary
            summary = manager.get_emission_reductions_summary()
            if summary:
                print(f"✅ Total emission reductions: {summary.get('total_emission_reductions', 0)} tCO2")
                print(f"   Total projects: {summary.get('total_projects', 0)}")
        
        else:
            print("❌ Invalid credential structure")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()