-- Guardian API Verifiable Credentials Database Schema
-- Extends existing energy_readings schema with credential management

-- Main verifiable credentials table
CREATE TABLE IF NOT EXISTS verifiable_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id TEXT UNIQUE NOT NULL, -- The "id" field from JSON (urn:uuid:project-participant-uuid)
    credential_type TEXT[] NOT NULL DEFAULT '{"VerifiableCredential"}',
    issuer TEXT NOT NULL, -- DID of the issuer
    issuance_date TIMESTAMPTZ NOT NULL,
    context JSONB NOT NULL DEFAULT '["https://www.w3.org/2018/credentials/v1"]',
    policy_id TEXT NOT NULL,
    guardian_version TEXT NOT NULL,
    proof JSONB NOT NULL, -- Complete proof object
    raw_credential JSONB NOT NULL, -- Store complete original credential
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project participant profiles table (main credential subject data)
CREATE TABLE IF NOT EXISTS project_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id UUID REFERENCES verifiable_credentials(id) ON DELETE CASCADE,
    
    -- Basic project info
    summary_description TEXT,
    sectoral_scope TEXT,
    project_type TEXT,
    type_of_activity TEXT,
    project_scale TEXT,
    
    -- Location data
    location_latitude DECIMAL(10, 7),
    location_longitude DECIMAL(11, 7),
    location_geojson JSONB, -- Store GeoJSON point
    
    -- Project details
    project_eligibility TEXT,
    organization_name TEXT NOT NULL,
    contact_person TEXT,
    contact_title TEXT,
    address TEXT,
    country TEXT,
    telephone TEXT,
    email TEXT,
    ownership TEXT,
    
    -- Programs and compliance
    emissions_trading_programs TEXT,
    participation_other_ghg_programs TEXT,
    other_env_credits TEXT,
    rejected_other_ghg_programs TEXT,
    methodologies TEXT,
    
    -- Dates and periods
    start_date DATE,
    
    -- Monitoring and compliance
    monitoring_plan TEXT,
    compliance TEXT,
    eligibility_criteria TEXT,
    sustainable_development TEXT,
    further_info TEXT,
    
    -- Calculations
    egpj_calculation TEXT,
    leakage_emissions DECIMAL(15, 6) DEFAULT 0.0,
    emission_reductions DECIMAL(15, 6),
    build_margin_most_recent_year INTEGER,
    build_margin_total_system_gen DECIMAL(15, 6),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crediting periods table (array data from JSON)
CREATE TABLE IF NOT EXISTS crediting_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID REFERENCES project_participants(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Monitoring periods table (array data from JSON)
CREATE TABLE IF NOT EXISTS monitoring_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID REFERENCES project_participants(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Electricity system information (Tool 07 data)
CREATE TABLE IF NOT EXISTS electricity_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID REFERENCES project_participants(id) ON DELETE CASCADE,
    electricity_system_info TEXT,
    hourly_or_annual_data TEXT,
    most_recent_year_gen INTEGER,
    total_system_gen DECIMAL(15, 6),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Power units within electricity systems
CREATE TABLE IF NOT EXISTS power_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    electricity_system_id UUID REFERENCES electricity_systems(id) ON DELETE CASCADE,
    unit_type TEXT NOT NULL,
    commissioned DATE,
    generation DECIMAL(15, 6),
    capacity DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Combined margin and emissions data
CREATE TABLE IF NOT EXISTS emissions_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID REFERENCES project_participants(id) ON DELETE CASCADE,
    
    -- Boolean/dropdown fields
    combined_margin_build_data_available BOOLEAN DEFAULT false,
    first_crediting_period_data BOOLEAN DEFAULT false,
    fossil_fuel_emissions BOOLEAN DEFAULT false,
    biomass_source_dedicated_plantations BOOLEAN DEFAULT false,
    integrated_hydro_projects BOOLEAN DEFAULT false,
    
    -- Emission factors and calculations
    average_co2_mass_fraction DECIMAL(8, 6),
    average_ch4_mass_fraction DECIMAL(8, 6),
    ch4_global_warming_potential DECIMAL(8, 2),
    
    -- Steam and fluid data
    steam_produced DECIMAL(15, 6),
    steam_entering_plant DECIMAL(15, 6),
    steam_leaving_plant DECIMAL(15, 6),
    working_fluid_leaked_reinjected DECIMAL(15, 6),
    working_fluid_gwp DECIMAL(8, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_verifiable_credentials_credential_id ON verifiable_credentials(credential_id);
CREATE INDEX IF NOT EXISTS idx_verifiable_credentials_issuer ON verifiable_credentials(issuer);
CREATE INDEX IF NOT EXISTS idx_verifiable_credentials_policy_id ON verifiable_credentials(policy_id);
CREATE INDEX IF NOT EXISTS idx_verifiable_credentials_issuance_date ON verifiable_credentials(issuance_date);

CREATE INDEX IF NOT EXISTS idx_project_participants_credential_id ON project_participants(credential_id);
CREATE INDEX IF NOT EXISTS idx_project_participants_organization ON project_participants(organization_name);
CREATE INDEX IF NOT EXISTS idx_project_participants_country ON project_participants(country);
CREATE INDEX IF NOT EXISTS idx_project_participants_project_type ON project_participants(project_type);
CREATE INDEX IF NOT EXISTS idx_project_participants_location ON project_participants(location_latitude, location_longitude);

CREATE INDEX IF NOT EXISTS idx_crediting_periods_participant ON crediting_periods(participant_id);
CREATE INDEX IF NOT EXISTS idx_crediting_periods_dates ON crediting_periods(start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_monitoring_periods_participant ON monitoring_periods(participant_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_periods_dates ON monitoring_periods(start_date, end_date);

-- Create a view for complete credential data with participant info
CREATE OR REPLACE VIEW credential_summary AS
SELECT 
    vc.credential_id,
    vc.issuer,
    vc.issuance_date,
    vc.policy_id,
    vc.guardian_version,
    pp.organization_name,
    pp.project_type,
    pp.sectoral_scope,
    pp.country,
    pp.location_latitude,
    pp.location_longitude,
    pp.emission_reductions,
    pp.start_date as project_start_date,
    vc.created_at
FROM verifiable_credentials vc
JOIN project_participants pp ON vc.id = pp.credential_id;

-- Function to insert complete credential data
CREATE OR REPLACE FUNCTION insert_guardian_credential(credential_json JSONB)
RETURNS UUID AS $$
DECLARE
    credential_uuid UUID;
    participant_uuid UUID;
    system_uuid UUID;
    subject_data JSONB;
    tool_07_data JSONB;
    power_unit JSONB;
BEGIN
    -- Extract credential subject data
    subject_data := credential_json->'credentialSubject'->0->'participant_profile';
    tool_07_data := subject_data->'tool_07'->'electricitySystemInfo';
    
    -- Insert main credential
    INSERT INTO verifiable_credentials (
        credential_id,
        credential_type,
        issuer,
        issuance_date,
        context,
        policy_id,
        guardian_version,
        proof,
        raw_credential
    ) VALUES (
        credential_json->>'id',
        ARRAY(SELECT jsonb_array_elements_text(credential_json->'type')),
        credential_json->>'issuer',
        (credential_json->>'issuanceDate')::TIMESTAMPTZ,
        credential_json->'@context',
        subject_data->>'policyId',
        subject_data->>'guardianVersion',
        credential_json->'proof',
        credential_json
    ) RETURNING id INTO credential_uuid;
    
    -- Insert project participant
    INSERT INTO project_participants (
        credential_id,
        summary_description,
        sectoral_scope,
        project_type,
        type_of_activity,
        project_scale,
        location_latitude,
        location_longitude,
        location_geojson,
        project_eligibility,
        organization_name,
        contact_person,
        contact_title,
        address,
        country,
        telephone,
        email,
        ownership,
        emissions_trading_programs,
        participation_other_ghg_programs,
        other_env_credits,
        rejected_other_ghg_programs,
        methodologies,
        start_date,
        monitoring_plan,
        compliance,
        eligibility_criteria,
        sustainable_development,
        further_info,
        egpj_calculation,
        leakage_emissions,
        emission_reductions,
        build_margin_most_recent_year,
        build_margin_total_system_gen
    ) VALUES (
        credential_uuid,
        subject_data->>'summaryDescription',
        subject_data->>'sectoralScope',
        subject_data->>'projectType',
        subject_data->>'typeOfActivity',
        subject_data->>'projectScale',
        (subject_data->>'locationLatitude')::DECIMAL,
        (subject_data->>'locationLongitude')::DECIMAL,
        subject_data->'locationGeoJSON',
        subject_data->>'projectEligibility',
        subject_data->>'organizationName',
        subject_data->>'contactPerson',
        subject_data->>'contactTitle',
        subject_data->>'address',
        subject_data->>'country',
        subject_data->>'telephone',
        subject_data->>'email',
        subject_data->>'ownership',
        subject_data->>'emissionsTradingPrograms',
        subject_data->>'participationOtherGHGPrograms',
        subject_data->>'otherEnvCredits',
        subject_data->>'rejectedOtherGHGPrograms',
        subject_data->>'methodologies',
        (subject_data->>'startDate')::DATE,
        subject_data->>'monitoringPlan',
        subject_data->>'compliance',
        subject_data->>'eligibilityCriteria',
        subject_data->>'sustainableDevelopment',
        subject_data->>'furtherInfo',
        subject_data->>'EGPJ_calculation',
        (subject_data->>'leakageEmissions')::DECIMAL,
        (subject_data->>'emissionReductions')::DECIMAL,
        (subject_data->>'buildMargin_mostRecentYear')::INTEGER,
        (subject_data->>'buildMargin_totalSystemGen')::DECIMAL
    ) RETURNING id INTO participant_uuid;
    
    -- Insert crediting periods
    INSERT INTO crediting_periods (participant_id, start_date, end_date)
    SELECT 
        participant_uuid,
        (period->>'start')::DATE,
        (period->>'end')::DATE
    FROM jsonb_array_elements(subject_data->'creditingPeriods') AS period;
    
    -- Insert monitoring periods
    INSERT INTO monitoring_periods (participant_id, start_date, end_date)
    SELECT 
        participant_uuid,
        (period->>'start')::DATE,
        (period->>'end')::DATE
    FROM jsonb_array_elements(subject_data->'monitoringPeriods') AS period;
    
    -- Insert electricity system info if exists
    IF subject_data ? 'tool_07' THEN
        INSERT INTO electricity_systems (
            participant_id,
            electricity_system_info,
            hourly_or_annual_data,
            most_recent_year_gen,
            total_system_gen
        ) VALUES (
            participant_uuid,
            subject_data->'tool_07'->>'electricitySystemInfo',
            subject_data->'tool_07'->>'hourlyOrAnnualData',
            (subject_data->'tool_07'->'buildMargin'->>'mostRecentYearGen')::INTEGER,
            (subject_data->'tool_07'->'buildMargin'->>'totalSystemGen')::DECIMAL
        ) RETURNING id INTO system_uuid;
        
        -- Insert power units
        INSERT INTO power_units (electricity_system_id, unit_type, commissioned, generation, capacity)
        SELECT 
            system_uuid,
            unit->>'type',
            (unit->>'commissioned')::DATE,
            (unit->>'generation')::DECIMAL,
            (unit->>'capacity')::DECIMAL
        FROM jsonb_array_elements(subject_data->'tool_07'->'buildMargin'->'powerUnits') AS unit;
    END IF;
    
    -- Insert emissions data
    INSERT INTO emissions_data (
        participant_id,
        combined_margin_build_data_available,
        first_crediting_period_data,
        fossil_fuel_emissions,
        biomass_source_dedicated_plantations,
        integrated_hydro_projects,
        average_co2_mass_fraction,
        average_ch4_mass_fraction,
        ch4_global_warming_potential,
        steam_produced,
        steam_entering_plant,
        steam_leaving_plant,
        working_fluid_leaked_reinjected,
        working_fluid_gwp
    ) VALUES (
        participant_uuid,
        (subject_data->>'combinedMarginBuildDataAvailable')::BOOLEAN,
        (subject_data->>'firstCreditingPeriodData')::BOOLEAN,
        (subject_data->>'fossilFuelEmissions')::BOOLEAN,
        (subject_data->>'biomassSourceDedicatedPlantations')::BOOLEAN,
        (subject_data->>'integratedHydroProjects')::BOOLEAN,
        (subject_data->>'averageCO2_massFraction')::DECIMAL,
        (subject_data->>'averageCH4_massFraction')::DECIMAL,
        (subject_data->>'CH4_globalWarmingPotential')::DECIMAL,
        (subject_data->>'steamProduced')::DECIMAL,
        (subject_data->>'steamEnteringPlant')::DECIMAL,
        (subject_data->>'steamLeavingPlant')::DECIMAL,
        (subject_data->>'workingFluidLeakedReinjected')::DECIMAL,
        (subject_data->>'workingFluidGWP')::DECIMAL
    );
    
    RETURN credential_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to retrieve complete credential data
CREATE OR REPLACE FUNCTION get_credential_details(credential_id_param TEXT)
RETURNS TABLE (
    credential_data JSONB,
    participant_data JSONB,
    crediting_periods JSONB,
    monitoring_periods JSONB,
    electricity_system JSONB,
    emissions_data JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        to_jsonb(vc.*) as credential_data,
        to_jsonb(pp.*) as participant_data,
        COALESCE(
            (SELECT jsonb_agg(to_jsonb(cp.*)) FROM crediting_periods cp WHERE cp.participant_id = pp.id),
            '[]'::jsonb
        ) as crediting_periods,
        COALESCE(
            (SELECT jsonb_agg(to_jsonb(mp.*)) FROM monitoring_periods mp WHERE mp.participant_id = pp.id),
            '[]'::jsonb
        ) as monitoring_periods,
        COALESCE(
            (SELECT to_jsonb(es.*) FROM electricity_systems es WHERE es.participant_id = pp.id),
            '{}'::jsonb
        ) as electricity_system,
        COALESCE(
            (SELECT to_jsonb(ed.*) FROM emissions_data ed WHERE ed.participant_id = pp.id),
            '{}'::jsonb
        ) as emissions_data
    FROM verifiable_credentials vc
    JOIN project_participants pp ON vc.id = pp.credential_id
    WHERE vc.credential_id = credential_id_param;
END;
$$ LANGUAGE plpgsql;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Partners signup table
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    country TEXT,
    project_type TEXT,
    project_description TEXT,
    expected_emission_reductions DECIMAL(15, 6),
    status TEXT DEFAULT 'pending', -- pending, approved, rejected
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for partners table
CREATE INDEX IF NOT EXISTS idx_partners_email ON partners(email);
CREATE INDEX IF NOT EXISTS idx_partners_status ON partners(status);
CREATE INDEX IF NOT EXISTS idx_partners_created_at ON partners(created_at);

-- Add updated_at triggers
CREATE TRIGGER update_verifiable_credentials_updated_at
    BEFORE UPDATE ON verifiable_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_participants_updated_at
    BEFORE UPDATE ON project_participants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partners_updated_at
    BEFORE UPDATE ON partners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();