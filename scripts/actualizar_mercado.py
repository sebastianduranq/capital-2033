"""Carga EODHD opcional: no publica cotizaciones sin credenciales ni datos válidos."""
import json, os, urllib.request, urllib.parse, datetime, pathlib, time

ROOT=pathlib.Path(__file__).resolve().parents[1]
TOKEN=os.getenv("EODHD_API_TOKEN","").strip()
SYMBOLS=["AGUAS-A","ALMENDRAL","ANDINA-B","BCI","BICE","CAP","CCU","CENCOMALLS","CENCOSUD","CFINRENTAS","CFMITNIPSA","CHILE","CMPC","COLBUN","CONCHATORO","COPEC","ENELAM","ENELCHILE","ENELGXCH","FALABELLA","IAM","ITAUCL","LIPIGAS","NTGCLGAS","PARAUCO","PEHUENCHE","QUEMCHI","QUINENCO","SCOTIABKCL","SK","SMU","SONDA","SQM-B","VAPORES","ZOFRI"]
# Confirmar exchange y correspondencia de símbolos en EODHD antes de habilitar.
EXCHANGE=os.getenv("EODHD_EXCHANGE","").strip().upper()
def fetch(path,params):
    url="https://eodhd.com/api/"+path+"?"+urllib.parse.urlencode({**params,"api_token":TOKEN,"fmt":"json"})
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Capital2033/2.0"}),timeout=20) as response:
        return json.load(response)
def load(name,default):
    try: return json.loads((ROOT/name).read_text())
    except (FileNotFoundError,ValueError): return default
def write(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
if not TOKEN or not EXCHANGE:
    print("Sin token o exchange verificado: no se modifican los datos publicados.")
    raise SystemExit(0)
today=datetime.date.today()
old=load("precios.json",{"quotes":[]})
prior={q["symbol"]:q for q in old.get("quotes",[]) if "symbol" in q}
events=load("dividendos-mercado.json",{"events":[]})
known={(e.get("symbol"),e.get("date"),e.get("dpa")) for e in events.get("events",[])}
for symbol in SYMBOLS:
    try:
        # EODHD exchange symbols deben verificarse individualmente: sin coincidencia no publicar.
        result=fetch("eod/"+urllib.parse.quote(symbol+"."+EXCHANGE),{"from":str(today-datetime.timedelta(days=12)),"order":"d"})
        if isinstance(result,list):
            result=sorted(result,key=lambda q:q.get("date",""),reverse=True)
            for q in result:
                day=str(q.get("date",""))
                close=float(q.get("close",0))
                if close>0 and 0<=(today-datetime.date.fromisoformat(day)).days<=7:
                    prior[symbol]={"symbol":symbol,"close":close,"date":day,"currency":"CLP","source":"EODHD"}
                    break
    except Exception as exc: print("Precio no actualizado",symbol,str(exc)[:160])
    # Dividendos se consultan solo si el presupuesto de API lo permite; nunca inferir fechas.
    time.sleep(.2)
if prior:
    write("precios.json",{"provider":"EODHD","updated_at":str(today),"quotes":sorted(prior.values(),key=lambda x:x["symbol"])})
print("Precios disponibles:",len(prior))
