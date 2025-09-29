#!/usr/bin/env python3
"""
Guardian Credentials API Endpoint
FastAPI server to receive and store Guardian verifiable credentials
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from guardian_credentials_manager import GuardianCredentialsManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Guardian Credentials API",
    description="API for storing and managing Guardian verifiable credentials",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the credentials manager
try:
    credentials_manager = GuardianCredentialsManager()
    logger.info("✅ Guardian Credentials Manager initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Guardian Credentials Manager: {e}")
    credentials_manager = None

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_connected: bool

class CredentialResponse(BaseModel):
    success: bool
    credential_uuid: Optional[str] = None
    credential_id: Optional[str] = None
    organization: Optional[str] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None

class CredentialListResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    count: int
    limit: int
    offset: int

class LocationResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    count: int
    bounds: Dict[str, float]

class SummaryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str

class PartnerSignupRequest(BaseModel):
    company_name: str
    contact_person: str
    email: str
    phone: Optional[str] = None
    country: Optional[str] = None
    project_type: Optional[str] = None
    project_description: Optional[str] = None
    expected_emission_reductions: Optional[float] = None

class PartnerSignupResponse(BaseModel):
    success: bool
    message: str
    partner_id: Optional[str] = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        database_connected=credentials_manager is not None
    )

@app.post("/api/credentials", response_model=CredentialResponse)
async def store_credential(credential_data: Dict[str, Any]):
    """
    Store a Guardian verifiable credential
    
    Expected JSON payload: Complete Guardian credential object
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Validate credential structure
        if not credentials_manager.validate_credential_structure(credential_data):
            raise HTTPException(
                status_code=400,
                detail="Invalid credential structure"
            )
        
        # Insert the credential
        credential_uuid = credentials_manager.insert_credential(credential_data)
        
        logger.info(f"✅ Stored credential: {credential_data.get('id', 'unknown')}")
        
        return CredentialResponse(
            success=True,
            credential_uuid=credential_uuid,
            credential_id=credential_data.get('id'),
            organization=credential_data.get('credentialSubject', [{}])[0]
                .get('participant_profile', {})
                .get('organizationName', 'Unknown'),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error storing credential: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store credential: {str(e)}"
        )

@app.get("/api/credentials/{credential_id}")
async def get_credential(credential_id: str):
    """
    Retrieve a credential by ID
    
    Args:
        credential_id: The credential ID (urn:uuid format)
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        credential_data = credentials_manager.get_credential_by_id(credential_id)
        
        if not credential_data:
            raise HTTPException(
                status_code=404,
                detail="Credential not found"
            )
        
        return {
            "success": True,
            "data": credential_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving credential: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve credential: {str(e)}"
        )

@app.get("/api/credentials", response_model=CredentialListResponse)
async def list_credentials(
    limit: int = Query(50, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    organization: Optional[str] = Query(None, description="Filter by organization name"),
    project_type: Optional[str] = Query(None, description="Filter by project type"),
    country: Optional[str] = Query(None, description="Filter by country"),
    sectoral_scope: Optional[str] = Query(None, description="Filter by sectoral scope")
):
    """
    List credentials with optional filtering
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Use search if filters are provided, otherwise list all
        if any([organization, project_type, country, sectoral_scope]):
            credentials = credentials_manager.search_credentials(
                organization_name=organization,
                project_type=project_type,
                country=country,
                sectoral_scope=sectoral_scope
            )
            # Apply pagination to search results
            credentials = credentials[offset:offset + limit]
        else:
            credentials = credentials_manager.list_credentials(limit=limit, offset=offset)
        
        return CredentialListResponse(
            success=True,
            data=credentials,
            count=len(credentials),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"❌ Error listing credentials: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list credentials: {str(e)}"
        )

@app.get("/api/credentials/location", response_model=LocationResponse)
async def get_credentials_by_location(
    lat_min: float = Query(-90, description="Minimum latitude"),
    lat_max: float = Query(90, description="Maximum latitude"),
    lon_min: float = Query(-180, description="Minimum longitude"),
    lon_max: float = Query(180, description="Maximum longitude")
):
    """
    Get credentials within a geographic bounding box
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        credentials = credentials_manager.get_credentials_by_location(
            lat_min=lat_min, lat_max=lat_max,
            lon_min=lon_min, lon_max=lon_max
        )
        
        return LocationResponse(
            success=True,
            data=credentials,
            count=len(credentials),
            bounds={
                'lat_min': lat_min, 'lat_max': lat_max,
                'lon_min': lon_min, 'lon_max': lon_max
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error searching by location: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search by location: {str(e)}"
        )

@app.get("/api/summary", response_model=SummaryResponse)
async def get_summary():
    """
    Get summary statistics of all credentials
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        summary = credentials_manager.get_emission_reductions_summary()
        
        return SummaryResponse(
            success=True,
            data=summary
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary: {str(e)}"
        )

@app.post("/api/test", response_model=CredentialResponse)
async def test_endpoint():
    """
    Test endpoint with sample Guardian credential data
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    # Sample credential for testing
    sample_credential = {
        "id": f"urn:uuid:test-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "type": ["VerifiableCredential"],
        "issuer": "did:hedera:testnet:test-issuer",
        "issuanceDate": datetime.utcnow().isoformat() + "Z",
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "schema:guardian-policy-v1"
        ],
        "credentialSubject": [{
            "participant_profile": {
                "summaryDescription": "Test renewable energy project",
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
                "projectEligibility": "Test compliance",
                "organizationName": "Test Energy Company",
                "contactPerson": "Test Person",
                "contactTitle": "Test Manager",
                "address": "Test Address",
                "country": "Morocco",
                "telephone": "+212600000000",
                "email": "test@example.com",
                "ownership": "Test Energy Company",
                "emissionsTradingPrograms": "Test Program",
                "participationOtherGHGPrograms": "None",
                "otherEnvCredits": "No",
                "rejectedOtherGHGPrograms": "No",
                "methodologies": "Test Methodology",
                "startDate": "2025-01-01",
                "creditingPeriods": [{
                    "start": "2025-01-01",
                    "end": "2030-12-31"
                }],
                "monitoringPeriods": [{
                    "start": "2025-01-01",
                    "end": "2025-12-31"
                }],
                "monitoringPlan": "Test monitoring plan",
                "compliance": "Test compliance",
                "eligibilityCriteria": "Test criteria",
                "sustainableDevelopment": "Test development",
                "EGPJ_calculation": "Test calculation",
                "leakageEmissions": 0.0,
                "emissionReductions": 8000,
                "buildMargin_mostRecentYear": 2024,
                "buildMargin_totalSystemGen": 4000000,
                "combinedMarginBuildDataAvailable": True,
                "firstCreditingPeriodData": True,
                "fossilFuelEmissions": False,
                "biomassSourceDedicatedPlantations": False,
                "averageCO2_massFraction": 0.25,
                "averageCH4_massFraction": 0.001,
                "CH4_globalWarmingPotential": 28,
                "steamProduced": 150000,
                "steamEnteringPlant": 145000,
                "steamLeavingPlant": 140000,
                "workingFluidLeakedReinjected": 300,
                "workingFluidGWP": 0,
                "integratedHydroProjects": False,
                "policyId": "test-policy-id",
                "guardianVersion": "3.3.0-test",
                "@context": ["schema:guardian-policy-v1"],
                "type": "guardian-policy-v1"
            }
        }],
        "proof": {
            "type": "Ed25519Signature2018",
            "created": datetime.utcnow().isoformat() + "Z",
            "verificationMethod": "did:hedera:testnet:test-issuer#did-root-key",
            "proofPurpose": "assertionMethod",
            "jws": "test-signature"
        }
    }
    
    try:
        credential_uuid = credentials_manager.insert_credential(sample_credential)
        
        return CredentialResponse(
            success=True,
            credential_uuid=credential_uuid,
            credential_id=sample_credential['id'],
            message="Test credential created successfully",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating test credential: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create test credential: {str(e)}"
        )

@app.post("/api/partners/signup", response_model=PartnerSignupResponse)
async def partner_signup(signup_data: PartnerSignupRequest):
    """
    Partner signup endpoint
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        # Insert partner signup data
        result = credentials_manager.supabase.table("partners").insert({
            "company_name": signup_data.company_name,
            "contact_person": signup_data.contact_person,
            "email": signup_data.email,
            "phone": signup_data.phone,
            "country": signup_data.country,
            "project_type": signup_data.project_type,
            "project_description": signup_data.project_description,
            "expected_emission_reductions": signup_data.expected_emission_reductions,
            "status": "pending"
        }).execute()
        
        if result.data:
            partner_id = result.data[0]["id"]
            logger.info(f"✅ Partner signup: {signup_data.email} - {signup_data.company_name}")
            
            return PartnerSignupResponse(
                success=True,
                message="Partnership application submitted successfully! We'll contact you soon.",
                partner_id=partner_id
            )
        else:
            raise Exception("Failed to insert partner data")
            
    except Exception as e:
        logger.error(f"❌ Error in partner signup: {e}")
        
        # Check if it's a duplicate email error
        if "duplicate key value" in str(e) or "unique constraint" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Email already registered. Please use a different email address."
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit partnership application: {str(e)}"
        )

@app.get("/api/partners")
async def list_partners(limit: int = Query(50, le=100), offset: int = Query(0, ge=0)):
    """
    List partner signups (admin endpoint)
    """
    if not credentials_manager:
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )
    
    try:
        result = credentials_manager.supabase.table("partners")\
            .select("*")\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return {
            "success": True,
            "data": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"❌ Error listing partners: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list partners: {str(e)}"
        )

if __name__ == '__main__':
    import uvicorn
    
    print("🌞 Guardian Credentials API Server (FastAPI)")
    print("=" * 50)
    print("📡 Starting FastAPI server...")
    print("🔗 Endpoints available:")
    print("   GET  /health - Health check")
    print("   POST /api/credentials - Store credential")
    print("   GET  /api/credentials - List credentials")
    print("   GET  /api/credentials/{id} - Get specific credential")
    print("   GET  /api/credentials/location - Search by location")
    print("   GET  /api/summary - Get summary statistics")
    print("   POST /api/test - Create test credential")
    print("   POST /api/partners/signup - Partner signup")
    print("   GET  /api/partners - List partners")
    print("   GET  /docs - Interactive API documentation")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=5000)