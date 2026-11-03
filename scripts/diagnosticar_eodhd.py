"""Diagnóstico de cobertura EODHD. No imprime token ni publica precios."""
import json,os,urllib.parse,urllib.request
token=os.environ.get("EODHD_API_TOKEN","").strip()
if not token:
    raise SystemExit("Falta EODHD_API_TOKEN en los secretos del repositorio.")
def get(path,params=None):
    args={"api_token":token,"fmt":"json",**(params or {})}
    url="https://eodhd.com/api/"+path+"?"+urllib.parse.urlencode(args)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Capital2033-coverage-check"}),timeout=25) as r:
        return json.load(r)
exchanges=get("exchanges-list/")
matches=[e for e in exchanges if str(e.get("CountryISO2","")).upper()=="CL" or "santiago" in str(e.get("Name","")).lower() or "chile" in str(e.get("Name","")).lower()]
if not matches:
    print("No se identificó bolsa chilena en el catálogo del plan actual.")
    raise SystemExit(0)
symbols={"CHILE","COLBUN","COPEC","ENELCHILE","IAM","PARAUCO","QUINENCO","ZOFRI","CCU","ENELAM","PEHUENCHE","CFINRENTAS","ENELGXCH","NTGCLGAS"}
for exchange in matches:
    code=str(exchange.get("Code","")).upper()
    print("Mercado candidato:",code,"|",exchange.get("Name"),"| moneda:",exchange.get("Currency"))
    try:
        listing=get("exchange-symbol-list/"+urllib.parse.quote(code),{"symbols":",".join(sorted(symbols))})
        if not isinstance(listing,list): raise ValueError("Respuesta no es una lista")
        found={str(s.get("Code","")).upper():s for s in listing}
        for symbol in sorted(symbols):
            if symbol in found:
                s=found[symbol]
                print("  COINCIDE:",symbol,"|",str(s.get("Name",""))[:80],"|",s.get("Currency"),"|",s.get("Type"))
            else:
                print("  SIN COINCIDENCIA:",symbol)
    except Exception as e:
        print("  No se pudo consultar el catálogo:",type(e).__name__,str(e)[:120])
print("Diagnóstico terminado. No se actualizaron cotizaciones.")
