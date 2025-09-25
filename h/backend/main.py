from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime
import uvicorn
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="ESP32 Carbon Credit Backend", version="0.6")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "your_supabase_url")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "your_supabase_anon_key")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase connection error: {e}")
    supabase = None

# Data models
class ESP32Reading(BaseModel):
    device_id: str
    timestamp: str
    current: float
    voltage: float
    power: float
    ac_power_kw: float
    total_energy_kwh: float
    grid_frequency_hz: float
    power_factor: float
    ambient_temp_c: float
    irradiance_w_m2: float
    system_status: int
    efficiency: float

class CarbonCreditData(BaseModel):
    methodology: str = "GCCM001_v4"
    reporting_period: str
    project_info: dict
    monitoring_data: dict
    calculations: dict

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Store latest readings in memory
latest_readings = {}
readings_history = []

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the real-time dashboard"""
    return HTMLResponse(content=dashboard_html, status_code=200)

@app.post("/api/energy-data")
async def receive_energy_data(reading: ESP32Reading):
    """Receive energy data from ESP32"""
    try:
        # Store in memory
        latest_readings[reading.device_id] = reading.dict()
        readings_history.append(reading.dict())
        
        # Keep only last 1000 readings in memory
        if len(readings_history) > 1000:
            readings_history.pop(0)
        
        # Store in Supabase
        if supabase:
            try:
                result = supabase.table("energy_readings").insert(reading.dict()).execute()
                print(f"Stored in Supabase: {result}")
            except Exception as e:
                print(f"Supabase insert error: {e}")
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "energy_reading",
            "data": reading.dict()
        }))
        
        return {"status": "success", "message": "Data received and stored"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/latest-readings")
async def get_latest_readings():
    """Get latest readings from all devices"""
    return latest_readings

@app.get("/api/readings-history")
async def get_readings_history(limit: int = 100):
    """Get historical readings"""
    return readings_history[-limit:]

@app.get("/api/carbon-credits/{device_id}")
async def calculate_carbon_credits(device_id: str):
    """Calculate carbon credits for a device"""
    if device_id not in latest_readings:
        raise HTTPException(status_code=404, detail="Device not found")
    
    reading = latest_readings[device_id]
    
    # Morocco grid emission factor (tCO2/MWh)
    morocco_ef = 0.81
    
    # Convert kWh to MWh
    export_mwh = reading["total_energy_kwh"] / 1000.0 * 0.98  # 98% export efficiency
    
    # Calculate emissions
    baseline_emissions = export_mwh * morocco_ef
    project_emissions = 0  # Solar has zero operational emissions
    emission_reductions = baseline_emissions
    
    carbon_credit_data = CarbonCreditData(
        reporting_period=reading["timestamp"],
        project_info={
            "project_name": f"ESP32 Solar Monitor - {device_id}",
            "project_id": f"VCC-{device_id}",
            "location": "Morocco",
            "capacity_mw": 0.001  # 1kW = 0.001MW
        },
        monitoring_data={
            "gross_generation_mwh": reading["total_energy_kwh"] / 1000.0,
            "net_export_mwh": export_mwh,
            "capacity_factor": (reading["ac_power_kw"] / 0.001) * 100 if reading["ac_power_kw"] > 0 else 0,
            "average_irradiance": reading["irradiance_w_m2"],
            "current_rms": reading["current"],
            "system_efficiency": reading["efficiency"]
        },
        calculations={
            "baseline_emissions_tco2": baseline_emissions,
            "project_emissions_tco2": project_emissions,
            "emission_reductions_tco2": emission_reductions,
            "carbon_credits_generated": emission_reductions
        }
    )
    
    return carbon_credit_data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await manager.connect(websocket)
    try:
        while True:
            # Send latest readings every 5 seconds
            if latest_readings:
                await websocket.send_text(json.dumps({
                    "type": "latest_readings",
                    "data": latest_readings
                }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Dashboard HTML
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Carbon Credit Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .status { 
            display: inline-block; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: bold; 
        }
        .status.online { 
            background: #4CAF50; 
        }
        .status.offline { 
            background: #f44336; 
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .card { 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px); 
            border-radius: 15px; 
            padding: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.2); 
        }
        .card h3 { 
            margin-top: 0; 
            color: #fff; 
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 10px; 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 8px; 
        }
        .metric-value { 
            font-weight: bold; 
            color: #4CAF50; 
        }
        .chart-container { 
            position: relative; 
            height: 300px; 
            margin: 20px 0; 
        }
        .carbon-credits { 
            background: linear-gradient(45deg, #4CAF50, #45a049); 
            text-align: center; 
            padding: 30px; 
            border-radius: 15px; 
            margin: 20px 0; 
        }
        .carbon-credits h2 { 
            margin: 0; 
            font-size: 2.5em; 
        }
        .carbon-credits p { 
            margin: 10px 0 0 0; 
            opacity: 0.9; 
        }
        .last-update { 
            text-align: center; 
            opacity: 0.7; 
            margin-top: 20px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌞 ESP32 Carbon Credit Dashboard</h1>
            <p>Real-time monitoring of solar energy generation and carbon credit calculation</p>
            <span id="connectionStatus" class="status offline">Connecting...</span>
        </div>

        <div id="devicesContainer"></div>

        <div class="carbon-credits">
            <h2 id="totalCredits">0.000</h2>
            <p>Total Carbon Credits Generated (tCO2)</p>
        </div>

        <div class="card">
            <h3>📊 Real-time Power Generation</h3>
            <div class="chart-container">
                <canvas id="powerChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h3>⚡ Energy Accumulation</h3>
            <div class="chart-container">
                <canvas id="energyChart"></canvas>
            </div>
        </div>

        <div class="last-update">
            Last updated: <span id="lastUpdate">Never</span>
        </div>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connectionStatus');
        const devicesContainer = document.getElementById('devicesContainer');
        const totalCreditsElement = document.getElementById('totalCredits');
        const lastUpdateElement = document.getElementById('lastUpdate');

        // Chart setup
        const powerCtx = document.getElementById('powerChart').getContext('2d');
        const energyCtx = document.getElementById('energyChart').getContext('2d');

        const powerChart = new Chart(powerCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Power (W)',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'white' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'white' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });

        const energyChart = new Chart(energyCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    la000).0", port=5="0.0.0n(app, hostrn.ru  uvico_":
  _main__ == "_e_if __nam
"""

>
</html>
</body  </script>ror));
   data:', ernitialing ich fetror.error('Er => consoleror   .catch(er         
        })
     });       
        ing);rd(readpdateDashboa           u        => {
 (reading forEach(data).luesct.va        Obje        a => {
en(dat     .th)
       ponse.json()es rresponse =>      .then(')
      dingsreai/latest-('/ap     fetch
   atah initial detc        // F   }

);
     s.toFixed(6bon_creditt = cartextContenlement.talCreditsE      to 
                 o_ef;
mwh * morocc export_n_credits =st carbocon          
  98;0 * 0._kwh / 1000.gyl_enertotading.ea_mwh = rconst export            ef = 0.81;
morocco_t ons   c   
      h) tCO2/MWactor: 0.81sion fmisocco es (Moredite carbon cratalcul       // Cng) {
     edits(readiateCarbonCrupdn  functio         }

      
e');'nonhart.update( energyC                   
   
            }hift();
 ts[0].data.s.datasedatat.  energyChar             t();
 .labels.shift.datayChar energ              {
  ngth > 20).lelabelsta..dagyChart (ener          if   
         h);
  _kwenergyl_ota(reading.t0].data.pushets[ta.datasgyChart.daener            time);
sh(ta.labels.purt.dahayC      energ
      gy chartdate ener       // Up    
          ;
   date('none')rChart.up    powe  
                 }
    
         );data.shift(s[0].datasethart.data.owerC  p             ft();
 a.labels.shihart.datowerC       p      20) {
   h > els.lengta.labathart.derC     if (pow    ints
    poly last 20  // Keep on
                     ;
 ing.power)push(read[0].data.atasetsata.dt.drCharpowe         
   (time);.labels.pushhart.datawerC        pot
    er charpowe   // Updat        
             ring();
 eStoLocaleTim.tp)amg.timestadinate(re = new D const time           reading) {
teCharts(ction upda  fun}

      
         W/m²`;(0)}xed.toFiadiance_w_m2rrading.itent = `${retextConiance`).ad-irrviceId}Id(`${deentBygetElemdocument.            (1)}°C`;
oFixedemp_c.tambient_tng.`${readi= tContent }-temp`).texviceIdd(`${deetElementByIocument.g     d       (1)}%`;
ixed0).toFency * 10ding.efficint = `${(reaontecy`).textC}-efficien{deviceIdmentById(`$ent.getEleum       dockWh`;
     )} ed(4Fixnergy_kwh.tog.total_e= `${readint tContennergy`).texceId}-e${devi(`ByIdementElcument.get     do     
  ixed(3)} A`;t.toFding.curren{rea`$ntent = textCo-current`).iceId}evntById(`${dtElemegecument.   do       } W`;
  1).toFixed(powering.{read`$ontent = `).textCpowerId}-ce(`${deviIdElementBydocument.get        _id;
    evice.dd = reading deviceI const      ) {
     eadingard, rcs(ctridateDeviceMen upunctio   f  }

     
      ard;    return c      `;
    
              </div>            </div>
                   n>
 0 W/m²</spadiance">viceId}-irra{de"$lue" id=etric-va"mclass=  <span                
       </span>ce:n>Irradian   <spa                >
     ic"s="metr   <div clas           div>
                </         C</span>
 mp">0°eviceId}-ted="${dlue" ivatric-="meclass     <span                   >
 :</spanperatureTemspan> <                  ">
     tricss="me  <div cla                  </div>
                    span>
">0%</iciencyeId}-eff{devic" id="$value"metric-ss=span cla      <                >
  an:</spciency<span>Effi                      ric">
  lass="metiv c         <d        
       </div>              >
  /spanrgy">0 kWh<}-ene"${deviceIdalue" id=-vass="metricn cl    <spa                  >
  spanergy:</<span>En                 ">
       "metrics=  <div clas              </div>
                n>
        sparent">0 A</Id}-cur{device"$ue" id=metric-val class="   <span              n>
       </spaurrent:an>C         <sp           ic">
    etrv class="m       <di      
       v>/di    <                0 W</span>
-power">d}"${deviceI" id=ueric-valetlass="m     <span c                 :</span>
   <span>Power                       tric">
="me<div class                    r 1fr;">
umns: 1fate-colgrid-templle=""grid" sty <div class=     
          iceId}</h3>vice: ${dev  <h3>📱 De              = `
nnerHTML    card.i         d}`;
eIic{dev`device-$rd.id =      ca       
 = 'card';me.classNaard        c
    );lement('div'eE.creat = documentonst card           c{
 (deviceId) ardceCn createDevi     functio

       };
    eString().toLocalg.timestamp)dinte(reaDaw ntent = neCotextt.teElemenastUpda         lmestamp
   Update ti//        
                g);
 readinbonCredits(ardateCup      
      n creditsbopdate car U   //             
        ing);
eCard, readcs(deviciceMetriteDevupda         trics
    Update me      //      }

   
         ceCard);Child(devindppesContainer.aevice           d
     _id);vice.deeading(rardeateDeviceCard = creC    devic        ) {
    rdiceCa if (!dev          
 evice_id}`);{reading.dce-$deviyId(`etElementBument.gard = docdeviceC   let s
         ardate device c  // Upd      g) {
    dind(reashboarn updateDafunctio

        
        };   };
         })               );
 ngboard(readi updateDash           {
        g => h(readinacrE.data).fogelues(messact.va   Obje          ngs') {
   adi_re== 'latestsage.type =lse if (mes    } e
        a);essage.datarts(m updateCh              
 data);ge.essaashboard(mateD      upd        
   {eading')ergy_r== 'enpe =tyessage.       if (m   
             data);
 se(event. JSON.parsage =t mesons     c      ) {
 n(eventtioncessage = funmws.o     
   };
        fline';
ofatus  = 'stssNames.claectionStatu      conn;
      nnected'nt = 'DiscotConteexonStatus.tectionn      c {
      nt)(eveonose = functiws.oncl        ;

     }nline';
   s oatu'stsName = clasatus.ctionSt     conned';
       Connecteent = 'nts.textCotunStatio      connec
       {vent)n(eiocten = fun    ws.onop

    );       }}
                }
            hite' } }
 olor: 'wlabels: { cnd: {      lege               lugins: {
 p            },
                     }
             }
      white'lor: ' { co  ticks:                  
    )' },0.1255, , 255, 55r: 'rgba(2d: { colo    gri                {
             x:       
            },    
          }: 'white'cks: { color        ti             },
    , 0.1)', 255, 255255'rgba(: d: { color        gri      
          : true,AtZero       begin                     y: {
              cales: {
   s            lse,
    fapectRatio:intainAs         ma        true,
nsive:spo    re            ns: {
ptio        o},
                }]
                ion: 0.4
 tens                
   .1)', 0150, 243,a(33, : 'rgbkgroundColor  bac                196F3',
   '#2borderColor:             
        data: [],             )',
      y (kWhEnergl: 'be