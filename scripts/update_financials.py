#!/usr/bin/env python3
"""DART public-data collector. API keys are read only from DART_API_KEY."""
import io, json, os, sys, time, zipfile, re
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

ROOT=Path(__file__).resolve().parents[1]
BASE="https://opendart.fss.or.kr/api"
REPORTS={"Q1":"11013","H1":"11012","Q3":"11014","FY":"11011"}
PEERS=[
 {"stock_code":"093050","name":"LF","segment":"패션 브랜드·의류 유통"},
 {"stock_code":"031430","name":"신세계인터내셔날","segment":"패션 브랜드·수입 브랜드 유통"},
 {"stock_code":"383220","name":"F&F","segment":"패션 브랜드 운영"},
 {"stock_code":"111770","name":"영원무역","segment":"아웃도어·의류 제조 및 OEM"},
 {"stock_code":"105630","name":"한세실업","segment":"글로벌 의류 OEM/ODM"},
 {"stock_code":"001460","name":"BYC","segment":"내의·언더웨어"},
]
S=requests.Session()
S.headers["User-Agent"]="SH-Handsomme-Financial-Dashboard/1.0"
def get(path,params,binary=False):
 r=S.get(BASE+"/"+path,params=params,timeout=45);r.raise_for_status()
 if binary:return r.content
 d=r.json();status=str(d.get("status",""))
 if status=="013":return {"list":[]}
 if status and status!="000":raise RuntimeError(f"DART API 오류 {status}: {d.get('message','')}")
 time.sleep(.06);return d
def corp_map(key):
 body=get("corpCode.xml",{"crtfc_key":key},True)
 try:
  with zipfile.ZipFile(io.BytesIO(body)) as z:
   xml=z.read(next(n for n in z.namelist() if n.lower().endswith(".xml")))
  root=ET.fromstring(xml)
 except Exception as e:raise RuntimeError("기업고유번호 응답을 읽을 수 없습니다. API 키를 확인하세요.") from e
 out={}
 for e in root.findall(".//list"):
  stock=(e.findtext("stock_code") or "").strip()
  code=(e.findtext("corp_code") or "").strip()
  name=(e.findtext("corp_name") or "").strip()
  if stock and code:out[stock.zfill(6)]={"corp_code":code,"stock_code":stock.zfill(6),"name":name}
 return out
def amount(v):
 try:
  s=str(v or "").replace(",","").strip()
  if not s or s=="-":return None
  if s.startswith("(") and s.endswith(")"):s="-"+s[1:-1]
  return float(s)
 except:return None
def norm(s):return re.sub(r"[\\s()（）·ㆍ-]","",s or "").lower()
SPECS={
 "revenue":({"ifrs-full_Revenue","ifrs-full_RevenueFromContractsWithCustomers","dart_Revenue"},{"매출액","수익(매출액)","매출","영업수익"},{"IS","CIS"}),
 "operating_income":({"dart_OperatingIncomeLoss","ifrs-full_OperatingProfitLoss"},{"영업이익","영업이익(손실)"},{"IS","CIS"}),
 "net_income":({"ifrs-full_ProfitLoss","ifrs-full_ProfitLossAttributableToOwnersOfParent"},{"당기순이익","당기순이익(손실)","분기순이익","반기순이익"},{"IS","CIS"}),
 "assets":({"ifrs-full_Assets"},{"자산총계"},{"BS"}),
 "liabilities":({"ifrs-full_Liabilities"},{"부채총계"},{"BS"}),
 "equity":({"ifrs-full_Equity"},{"자본총계"},{"BS"}),
 "current_assets":({"ifrs-full_CurrentAssets"},{"유동자산"},{"BS"}),
 "current_liabilities":({"ifrs-full_CurrentLiabilities"},{"유동부채"},{"BS"}),
 "operating_cash_flow":({"ifrs-full_CashFlowsFromUsedInOperatingActivities","ifrs-full_CashFlowsFromOperatingActivities"},{"영업활동현금흐름","영업활동으로인한현금흐름"},{"CF"}),
}
def pick(rows,key):
 ids,names,statements=SPECS[key]; pool=[r for r in rows if r.get("sj_div") in statements] or rows
 for r in pool:
  if r.get("account_id") in ids:
   v=amount(r.get("thstrm_amount"))
   if v is not None:return v
 for r in pool:
  name=norm(r.get("account_nm",""))
  if name in {norm(x) for x in names} or (key=="net_income" and "당기순이익" in name and "포괄" not in name) or (key=="operating_cash_flow" and "영업활동" in name and "현금흐름" in name):
   v=amount(r.get("thstrm_amount"))
   if v is not None:return v
 return None
FLOW=("revenue","operating_income","net_income","operating_cash_flow")
def ratios(rows,annual_factor):
 prev=None
 for x in rows:
  div=lambda a,b:round(a/b*100*annual_factor,2) if a is not None and b not in (None,0) else None
  x["operating_margin"]=div(x.get("operating_income"),x.get("revenue"),) if False else (round(x["operating_income"]/x["revenue"]*100,2) if x.get("operating_income") is not None and x.get("revenue") else None)
  x["net_margin"]=round(x["net_income"]/x["revenue"]*100,2) if x.get("net_income") is not None and x.get("revenue") else None
  x["debt_ratio"]=round(x["liabilities"]/x["equity"]*100,2) if x.get("liabilities") is not None and x.get("equity") else None
  x["current_ratio"]=round(x["current_assets"]/x["current_liabilities"]*100,2) if x.get("current_assets") is not None and x.get("current_liabilities") else None
  eq=x.get("equity");den=((prev+eq)/2 if prev is not None and eq is not None else eq)
  x["roe"]=round(x["net_income"]/den*100*annual_factor,2) if x.get("net_income") is not None and den else None
  if eq is not None:prev=eq
  if x.get("report_no"):x["report_url"]="https://dart.fss.or.kr/dsaf001/main.do?rcpNo="+str(x["report_no"])
def collect(key,corp,yearlist):
 reports={};raw=[]
 for year in yearlist:
  for tag,rc in REPORTS.items():
   rows=[];fs=""
   for basis in ("CFS","OFS"):
    d=get("fnlttSinglAcntAll.json",{"crtfc_key":key,"corp_code":corp["corp_code"],"bsns_year":str(year),"reprt_code":rc,"fs_div":basis})
    rows=d.get("list",[])
    if rows:fs=basis;break
   if not rows:continue
   r={k:next((amount(row.get("thstrm_amount")) for row in rows if row.get("account_id") in ids and amount(row.get("thstrm_amount")) is not None),None) for k,(ids,_,_) in SPECS.items()}
   for k in SPECS:
    if r[k] is None:r[k]=pick(rows,k)
   r.update({"year":year,"period":str(year) if tag=="FY" else f"{year} H1" if tag=="H1" else f"{year} Q{1 if tag=='Q1' else 3}","report_no":next((z.get("rcept_no") for z in rows if z.get("rcept_no")),None),"report_code":rc,"report_name":{"Q1":"1분기","H1":"반기","Q3":"3분기","FY":"사업보고서"}[tag],"fs_div":fs})
   reports[(year,tag)]=r
   if corp["stock_code"]=="020000":raw.append({"year":year,"period_key":tag,"report_code":rc,"report_name":r["report_name"],"fs_div":fs,"rcept_no":r["report_no"],"rows":rows})
 annual=[];half=[];quarter=[]
 for y in yearlist:
  if (y,"FY") in reports:annual.append(dict(reports[(y,"FY")],period=str(y),period_type="annual"))
  if (y,"H1") in reports:half.append(dict(reports[(y,"H1")],period=f"{y} H1",period_type="half_year"))
  for q,tag,prev,factor in [(1,"Q1",None,4),(2,"H1","Q1",2),(3,"Q3","H1",4),(4,"FY","Q3",4)]:
   cur=reports.get((y,tag));prior=reports.get((y,prev)) if prev else None
   if not cur or (prev and not prior):continue
   row=dict(cur)
   if prior:
    for k in FLOW:
     row[k]=cur.get(k)-prior.get(k) if cur.get(k) is not None and prior.get(k) is not None else None
   row.update({"period":f"{y} Q{q}","period_type":"quarterly","quarter":q,"annualization":factor});quarter.append(row)
 ratios(annual,1);ratios(half,2);ratios(quarter,4)
 return {"annual":annual,"half_year":half,"quarterly":quarter,"raw_reports":raw}
def main():
 key=os.environ.get("DART_API_KEY","").strip()
 if len(key)!=40:raise RuntimeError("DART_API_KEY가 없거나 40자 인증키가 아닙니다. Actions Secret을 확인하세요.")
 corps=corp_map(key);maincorp=corps.get("020000")
 if not maincorp:raise RuntimeError("DART 기업고유번호 목록에서 한섬(020000)을 찾지 못했습니다.")
 years=list(range(datetime.now(timezone.utc).year-4,datetime.now(timezone.utc).year+1))
 all_data={"020000":collect(key,maincorp,years)};peerout=[]
 for p in PEERS:
  corp=corps.get(p["stock_code"]);dataset=collect(key,corp,years) if corp else {}
  if corp:all_data[p["stock_code"]]=dataset
  annual=dataset.get("annual",[])
  peerout.append({**p,"annual_latest":annual[-1] if annual else None})
 data=all_data["020000"];now=datetime.now(timezone.utc).isoformat(timespec="seconds")
 raw={"generated_at":now,"company":{"name":"한섬","stock_code":"020000","corp_code":maincorp["corp_code"]},"source":"DART fnlttSinglAcntAll.json","reports":data["raw_reports"]}
 (ROOT/"data/hansem_dart_reports.json").write_text(json.dumps(raw,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 clean={k:v for k,v in data.items() if k!="raw_reports"}
 out={"generated_at":now,"data_status":"ok" if any(clean[k] for k in ("annual","half_year","quarterly")) else "no_data","message":"","currency_unit":"KRW","display_unit":"억원","consolidation_basis":"연결 우선, 미제공 시 별도","company":{"name":"한섬","stock_code":"020000"},**clean,"peers":peerout}
 tmp=ROOT/"data/financials.json.tmp";tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");tmp.replace(ROOT/"data/financials.json")
 print("DART update completed:",len(clean["annual"]),"annual",len(clean["half_year"]),"half-year",len(clean["quarterly"]),"quarterly")
if __name__=="__main__":
 try:main()
 except requests.RequestException as e:
  print("DART HTTP 요청 실패. 키를 포함한 URL은 출력하지 않았습니다. 오류 유형:",type(e).__name__,file=sys.stderr);sys.exit(1)
 except (RuntimeError,ValueError,ET.ParseError) as e:print("DART 수집 실패:",e,file=sys.stderr);sys.exit(1)
