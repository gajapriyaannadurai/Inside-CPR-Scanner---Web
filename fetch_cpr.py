<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Inside CPR Scanner — Stark School of Finance</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f4f6f9;color:#1a1a2e;padding:1.5rem 1rem}
.page-wrap{max-width:1380px;margin:0 auto}
.card{background:#fff;border-radius:14px;border:1px solid #e2e6ed;overflow:hidden;margin-bottom:1.5rem}
.top-header{background:#0a1628;padding:1.5rem 2rem}
.top-header h2{font-size:24px;font-weight:700;color:#fff;margin-bottom:4px}
.top-header p{font-size:13px;color:rgba(255,255,255,0.45)}
.tf-row{display:flex;align-items:center;gap:10px;margin-top:1rem;flex-wrap:wrap}
.tf-label{font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:rgba(255,255,255,0.4)}
.tf-btn{padding:7px 20px;border-radius:7px;font-size:13px;font-weight:500;cursor:pointer;border:1px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.55);background:transparent}
.tf-btn.active{background:#00c878;color:#0a1628;border-color:#00c878;font-weight:700}
.stats-row{display:flex;border-bottom:1px solid #e8ecf0;flex-wrap:wrap}
.stat{flex:1;min-width:110px;padding:14px 18px;border-right:1px solid #e8ecf0;background:#f8fafc}
.stat:last-child{border-right:none}
.stat-label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:#888;margin-bottom:5px}
.stat-val{font-size:24px;font-weight:700;color:#1a1a2e}
.stat-val.green{color:#0b6b40}
.stat-val.muted{color:#888;font-size:14px;padding-top:4px}
.flag-bar{padding:9px 18px;border-bottom:1px solid #e8ecf0;display:flex;align-items:center;gap:10px}
.flag-pill{display:inline-flex;align-items:center;gap:5px;padding:3px 12px;border-radius:20px;font-weight:600;font-size:12px}
.flag-red{background:#fff0f0;color:#c0392b;border:1px solid #f5c6c6}
.flag-green{background:#e8f5ee;color:#0b6b40;border:1px solid #c8e6d0}
.flag-msg{font-size:12.5px;color:#666}
.status-bar{padding:7px 18px;border-bottom:1px solid #e8ecf0;display:flex;align-items:center;gap:8px;font-size:12px;background:#fff}
.dot{width:8px;height:8px;border-radius:50%;background:#ccc;display:inline-block;flex-shrink:0}
.dot.live{background:#00c878}
.dot.loading{background:#ef9f27}
.dot.error{background:#e24b4a}
.filter-row{padding:12px 18px;border-bottom:1px solid #e8ecf0;display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;background:#fff}
.fg{display:flex;flex-direction:column;gap:4px}
.fg label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:#888}
.fg select,.fg input{font-size:13px;padding:7px 10px;border-radius:7px;border:1px solid #dde1e8;background:#fff;color:#1a1a2e;outline:none}
.scan-btn{padding:9px 24px;background:#00c878;color:#0a1628;border:none;border-radius:7px;font-size:13px;font-weight:700;cursor:pointer;align-self:flex-end}
.reset-btn{padding:9px 14px;background:transparent;border:1px solid #dde1e8;border-radius:7px;font-size:13px;cursor:pointer;color:#888;align-self:flex-end}
.dl-btn{padding:9px 14px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;align-self:flex-end}
.dl-csv{background:#fff;color:#185fa5;border:1px solid #185fa5}
.dl-xlsx{background:#fff;color:#0b6b40;border:1px solid #0b6b40}
.dl-btn:disabled{opacity:0.35;cursor:not-allowed}
.rcount{font-size:13px;color:#888;align-self:flex-end;margin-left:auto}
.progress-wrap{height:3px;background:#e8ecf0;display:none}
.progress-bar{height:3px;background:#00c878;width:0%;transition:width 0.3s}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse}
thead th{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#888;padding:11px 14px;text-align:left;border-bottom:1px solid #e8ecf0;background:#f8fafc;white-space:nowrap;cursor:pointer;user-select:none}
thead th:hover{color:#1a1a2e}
tbody td{padding:12px 14px;border-bottom:1px solid #f0f2f5;white-space:nowrap;vertical-align:middle}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover td{background:#f8fafc}
.sym{font-size:14px;font-weight:700;color:#0a1628}
.company{font-size:12px;color:#555}
.sector-tag{font-size:11px;color:#888}
.price-cell{font-size:14px;font-weight:600;color:#1a1a2e;text-align:right}
.pc{font-size:13px;color:#888;text-align:right}
.tc-cell{font-size:13px;color:#0b6b40;text-align:right;font-weight:600}
.bc-cell{font-size:13px;color:#a32d2d;text-align:right;font-weight:600}
.up{font-size:13px;color:#0b6b40;text-align:right;font-weight:500}
.dn{font-size:13px;color:#a32d2d;text-align:right;font-weight:500}
.badge{font-size:11px;font-weight:600;padding:3px 9px;border-radius:20px;display:inline-block}
.b-narrow{background:#e6f1fb;color:#185fa5}
.b-medium{background:#faeeda;color:#7a4a08}
.b-wide{background:#fcebeb;color:#a32d2d}
.b-fno{background:#eeedfe;color:#3c3489}
.wbar-wrap{display:flex;align-items:center;gap:6px;justify-content:flex-end}
.wbar{height:5px;border-radius:3px;background:#00c878;display:inline-block}
.empty-state{padding:3rem;text-align:center;color:#888;font-size:15px;line-height:2}
.brand-footer{text-align:center;font-size:12px;color:#aaa;margin-top:1rem}
.brand-footer a{color:#00c878;text-decoration:none;font-weight:600}
</style>
</head>
<body>
<div class="page-wrap">
<div class="card">
  <div class="top-header">
    <h2>Inside CPR Scanner</h2>
    <p>Scans stocks where current period CPR fits inside the previous period CPR — Stark School of Finance</p>
    <div class="tf-row">
      <span class="tf-label">Timeframe</span>
      <button class="tf-btn active" onclick="setTF('daily',this)">Daily</button>
      <button class="tf-btn" onclick="setTF('weekly',this)">Weekly</button>
      <button class="tf-btn" onclick="setTF('monthly',this)">Monthly</button>
    </div>
  </div>
  <div class="stats-row">
    <div class="stat"><div class="stat-label">Inside CPR</div><div class="stat-val green" id="s-inside">—</div></div>
    <div class="stat"><div class="stat-label">Narrow CPR</div><div class="stat-val muted" id="s-narrow" style="font-size:20px;padding-top:3px">—</div></div>
    <div class="stat"><div class="stat-label">Wide CPR</div><div class="stat-val muted" id="s-wide" style="font-size:20px;padding-top:3px">—</div></div>
    <div class="stat"><div class="stat-label">Stocks Scanned</div><div class="stat-val muted" id="s-scanned" style="font-size:20px;padding-top:3px">—</div></div>
    <div class="stat"><div class="stat-label">Last Scanned</div><div class="stat-val muted" id="s-time">—</div></div>
  </div>
  <div class="flag-bar">
    <span class="flag-pill" id="flag-pill">⏳ Loading...</span>
    <span class="flag-msg" id="flag-msg"></span>
  </div>
  <div class="status-bar">
    <span class="dot" id="status-dot"></span>
    <span id="status-text" style="color:#888">Click Scan Now to load data</span>
  </div>
  <div class="progress-wrap" id="pw"><div class="progress-bar" id="pb"></div></div>
  <div class="filter-row">
    <div class="fg"><label>Index</label>
      <select id="f-index">
        <option value="nifty50">Nifty 50</option>
        <option value="niftybank">Nifty Bank</option>
        <option value="niftyit">Nifty IT</option>
        <option value="niftymidcap50">Nifty Midcap 50</option>
        <option value="nifty100">Nifty 100</option>
        <option value="nifty200">Nifty 200</option>
        <option value="nifty500">Nifty 500</option>
        <option value="fno">F&amp;O Segment</option>
      </select></div>
    <div class="fg"><label>Sector</label>
      <select id="f-sector">
        <option value="">All sectors</option>
        <option>Financial Services</option>
        <option>Information Technology</option>
        <option>Healthcare</option>
        <option>Automobile</option>
        <option>Capital Goods</option>
        <option>FMCG</option>
        <option>Oil &amp; Gas</option>
        <option>Metals &amp; Mining</option>
        <option>Chemicals</option>
        <option>Realty</option>
        <option>Power</option>
        <option>Telecom</option>
        <option>Consumer Durables</option>
        <option>Services</option>
      </select></div>
    <div class="fg"><label>CPR Width</label>
      <select id="f-width">
        <option value="">Any</option>
        <option value="narrow">Narrow (&lt;0.5%)</option>
        <option value="medium">Medium (0.5–1.5%)</option>
        <option value="wide">Wide (&gt;1.5%)</option>
      </select></div>
    <div class="fg"><label>F&amp;O Only</label>
      <select id="f-fno">
        <option value="">All stocks</option>
        <option value="yes">F&amp;O only</option>
      </select></div>
    <div class="fg"><label>Min Price (₹)</label>
      <input type="number" id="f-price" placeholder="e.g. 100" style="width:100px"></div>
    <button class="scan-btn" onclick="doScan()">&#9654; Scan Now</button>
    <button class="reset-btn" onclick="doReset()">&#8635; Reset</button>
    <button class="dl-btn dl-csv" id="dl-csv" onclick="dlCSV()" disabled>&#8595; CSV</button>
    <button class="dl-btn dl-xlsx" id="dl-xlsx" onclick="dlExcel()" disabled>&#8595; Excel</button>
    <span class="rcount" id="rcount"></span>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th onclick="srt('symbol')">Symbol</th>
        <th onclick="srt('name')">Company</th>
        <th onclick="srt('sector')">Sector</th>
        <th onclick="srt('fno')">F&amp;O</th>
        <th onclick="srt('price')" style="text-align:right">CMP (₹)</th>
        <th onclick="srt('change')" style="text-align:right">Chg %</th>
        <th onclick="srt('pivot')" style="text-align:right">Pivot</th>
        <th onclick="srt('tc')" style="text-align:right" id="th-tc">Curr. TC</th>
        <th onclick="srt('bc')" style="text-align:right" id="th-bc">Curr. BC</th>
        <th onclick="srt('prevTc')" style="text-align:right" id="th-ptc">Prev. TC</th>
        <th onclick="srt('prevBc')" style="text-align:right" id="th-pbc">Prev. BC</th>
        <th onclick="srt('widthPct')" style="text-align:right;min-width:120px">Width %</th>
      </tr></thead>
      <tbody id="tbody">
        <tr><td colspan="12" class="empty-state">Select index and click <strong>Scan Now</strong></td></tr>
      </tbody>
    </table>
  </div>
</div>
<div class="brand-footer">Powered by <a href="https://www.tradingwithgp.com" target="_blank">Stark School of Finance — tradingwithgp.com</a></div>
</div>

<script>
// ── State ──────────────────────────────────────────────────────────────────────
var tf='daily', sk='widthPct', sa=true, results=[], allData=[], dataLoaded=false;

// ── Index symbol sets ──────────────────────────────────────────────────────────
var IDX={
  nifty50:['RELIANCE','TCS','HDFCBANK','BHARTIARTL','ICICIBANK','INFY','SBIN','HINDUNILVR','ITC','KOTAKBANK','LT','AXISBANK','BAJFINANCE','MARUTI','ASIANPAINT','TITAN','SUNPHARMA','NESTLEIND','WIPRO','ONGC','NTPC','POWERGRID','TATASTEEL','TECHM','HCLTECH','DRREDDY','DIVISLAB','JSWSTEEL','ADANIENT','BAJAJFINSV','ULTRACEMCO','GRASIM','INDUSINDBK','CIPLA','EICHERMOT','APOLLOHOSP','BPCL','COALINDIA','BRITANNIA','TATACONSUM','HEROMOTOCO','HINDALCO','SBILIFE','HDFCLIFE','BAJAJ-AUTO','M&M','SHRIRAMFIN','TRENT','BEL','TMPV'],
  niftybank:['HDFCBANK','ICICIBANK','KOTAKBANK','SBIN','AXISBANK','INDUSINDBK','BANDHANBNK','FEDERALBNK','IDFCFIRSTB','AUBANK','PNB','BANKBARODA'],
  niftyit:['TCS','INFY','HCLTECH','WIPRO','TECHM','LTIM','MPHASIS','COFORGE','PERSISTENT','OFSS'],
  niftymidcap50:['COFORGE','VOLTAS','MUTHOOTFIN','PERSISTENT','ABCAPITAL','KPITTECH','LAURUSLABS','IIFL','ANGELONE','DMART','IRCTC','NAUKRI','GODREJPROP','TATAPOWER','TATAELXSI','FORTIS'],
};
IDX.nifty100=[...new Set([...IDX.nifty50,'ADANIPORTS','ADANIGREEN','ADANIPOWER','BAJAJHLDNG','BERGEPAINT','BHEL','BIOCON','BOSCHLTD','CDSL','CGPOWER','CHOLAFIN','COFORGE','CROMPTON','CUMMINSIND','DABUR','DEEPAKNTR','DIXON','DLF','GAIL','GODREJCP','GODREJPROP','HAL','HDFCAMC','HINDCOPPER','HINDPETRO','HINDZINC','ICICIGI','ICICIPRULI','IEX','IOC','IRCTC','JSWSTEEL','JUBLFOOD','LTIM','LTTS','LUPIN','M&MFIN','MANAPPURAM','MARICO','MCX','MFSL','MPHASIS','NATIONALUM','NAUKRI','NMDC','NYKAA','PERSISTENT','PETRONET','PFC','PIIND','POLYCAB','RBLBANK','RECLTD','SAIL','SBICARD','SHREECEM','SIEMENS','SRF','SYNGENE','TATACHEM','TATACOMM','TATAPOWER','TORNTPHARM','TRENT','TVSMOTOR','UPL','VEDL','VOLTAS','ZOMATO','ZYDUSLIFE'])];
IDX.nifty200=[...new Set([...IDX.nifty100,'ABB','ACC','AIAENG','APLAPOLLO','AUBANK','AARTIIND','ABBOTINDIA','ABFRL','AWL','ALKEM','ALKYLAMINE','AMBUJACEM','ANGELONE','APOLLOTYRE','ASHOKLEY','ASTRAL','AUROPHARMA','BALKRISIND','BANDHANBNK','BANKBARODA','BANKINDIA','BATAINDIA','BDL','BHARATFORG','CAMS','CANFINHOME','CANBK','CEATLTD','CHAMBLFERT','COCHINSHIP','COLPAL','CONCOR','COROMANDEL','CYIENT','DALBHARAT','ESCORTS','FEDERALBNK','FORTIS','FLUOROCHEM','GLAND','GLENMARK','GRANULES','GSPL','HAVELLS','HINDCOPPER','IDFCFIRSTB','INDHOTEL','INDUSTOWER','IRFC','JINDALSTEL','JUBLFOOD','JIOFINANCE','KAJARIACER','LAURUSLABS','MANKIND','MUTHOOTFIN','NAVINFLUOR','NHPC','NYKAA','PAGEIND','PNB','RAMCOCEM','RVNL','SJVN','STARHEALTH','TATACHEM','TATACOMM','TATAELXSI','TVSMOTOR','UNIONBANK','VEDL','YESBANK','ZOMATO'])];

// ── Utility ────────────────────────────────────────────────────────────────────
function setStatus(type,msg){
  var d=document.getElementById('status-dot');
  var t=document.getElementById('status-text');
  d.className='dot'+(type?' '+type:'');
  t.textContent=msg;
  t.style.color=type==='error'?'#a32d2d':type==='live'?'#0b6b40':'#888';
}
function setProg(p){
  document.getElementById('pw').style.display=p>0?'block':'none';
  document.getElementById('pb').style.width=p+'%';
}
function setFlag(green,label,msg){
  var p=document.getElementById('flag-pill');
  var m=document.getElementById('flag-msg');
  p.className='flag-pill '+(green?'flag-green':'flag-red');
  p.textContent=(green?'🟢 ':'🔴 ')+label;
  m.textContent=msg;
}
function updateFlag(){
  var now=new Date();
  var ist=new Date(now.getTime()+(now.getTimezoneOffset()*60000)+(5.5*3600000));
  var day=ist.getDay();
  var hhmm=ist.getHours()*100+ist.getMinutes();
  var isWeekday=day>=1&&day<=5;
  var isOpen=isWeekday&&hhmm>=915&&hhmm<1530;
  var isAfterClose=isWeekday&&hhmm>=1530;
  var isFriday=day===5;
  var isWeekend=day===0||day===6;
  var lastDay=new Date(ist.getFullYear(),ist.getMonth()+1,0).getDate();
  var isMonthEnd=ist.getDate()===lastDay&&isAfterClose;

  // Update column headers
  if(tf==='daily'){
    document.getElementById('th-tc').textContent=isAfterClose?'Tom. TC':'Curr. TC';
    document.getElementById('th-bc').textContent=isAfterClose?'Tom. BC':'Curr. BC';
    document.getElementById('th-ptc').textContent=isAfterClose?'Today TC':'Prev. TC';
    document.getElementById('th-pbc').textContent=isAfterClose?'Today BC':'Prev. BC';
  }

  if(tf==='daily'){
    if(isOpen) setFlag(false,'Market Open','CPR calculated from yesterday\'s OHLC — valid for today\'s session.');
    else if(isAfterClose) setFlag(true,'Market Closed','CPR calculated from today\'s OHLC — valid for tomorrow\'s trading.');
    else setFlag(true,'Market Closed','CPR calculated from last session\'s OHLC — valid for today\'s trading.');
  } else if(tf==='weekly'){
    if((isFriday&&isAfterClose)||isWeekend) setFlag(true,'Week Closed','CPR calculated from this week\'s OHLC — valid for next week\'s trading.');
    else setFlag(false,'Week Running','CPR calculated from previous week\'s OHLC — valid for this week\'s trading session.');
  } else if(tf==='monthly'){
    if(isMonthEnd) setFlag(true,'Month Closed','CPR calculated from this month\'s OHLC — valid for next month\'s trading.');
    else setFlag(false,'Month Running','CPR calculated from previous month\'s OHLC — valid for this month\'s trading session.');
  }
}

// ── TF switch ──────────────────────────────────────────────────────────────────
function setTF(t,el){
  tf=t;
  document.querySelectorAll('.tf-btn').forEach(function(b){b.classList.remove('active');});
  el.classList.add('active');
  updateFlag();
  if(dataLoaded) applyFilters();
  else document.getElementById('tbody').innerHTML='<tr><td colspan="12" class="empty-state">Click <strong>Scan Now</strong> to load data</td></tr>';
}

// ── Scan ───────────────────────────────────────────────────────────────────────
function doScan(){
  setStatus('loading','Loading CPR data...');
  setProg(20);

  // Use embedded data if available (injected by GitHub Actions)
  if(window.__CPR_DATA__){
    allData=window.__CPR_DATA__.stocks||[];
    dataLoaded=true;
    setProg(80);
    applyFilters();
    setProg(100);
    setTimeout(function(){setProg(0);},500);
    setStatus('live','Loaded '+allData.length+' stocks · '+(window.__CPR_DATA__.generated_at||''));
    document.getElementById('s-time').textContent=window.__CPR_DATA__.generated_at||'—';
    return;
  }

  // Fallback: fetch from URL
  var urls=[
    'https://scanner.tradingwithgp.com/cpr_data.json',
    'https://gajapriyaannadurai.github.io/Inside-CPR-Scanner---Web/cpr_data.json'
  ];
  tryFetch(urls,0);
}

function tryFetch(urls,i){
  if(i>=urls.length){
    setStatus('error','No data found. Please run the GitHub Action first.');
    setProg(0);
    document.getElementById('tbody').innerHTML='<tr><td colspan="12" class="empty-state" style="color:#a32d2d">Data not available.<br>Go to GitHub repo → Actions → CPR Daily Scanner → Run workflow.<br>Wait 4 minutes then click Scan Now again.</td></tr>';
    return;
  }
  setStatus('loading','Trying: '+urls[i]);
  var xhr=new XMLHttpRequest();
  xhr.open('GET',urls[i]+'?t='+Date.now(),true);
  xhr.onreadystatechange=function(){
    if(xhr.readyState===4){
      if(xhr.status===200){
        try{
          var json=JSON.parse(xhr.responseText);
          allData=json.stocks||[];
          dataLoaded=true;
          setProg(100);
          setTimeout(function(){setProg(0);},500);
          applyFilters();
          setStatus('live','Loaded '+allData.length+' stocks · '+(json.generated_at||''));
          document.getElementById('s-time').textContent=json.generated_at||'—';
        } catch(e){
          tryFetch(urls,i+1);
        }
      } else {
        tryFetch(urls,i+1);
      }
    }
  };
  xhr.onerror=function(){ tryFetch(urls,i+1); };
  xhr.send();
}

// ── Filter ─────────────────────────────────────────────────────────────────────
function applyFilters(){
  var idxKey=document.getElementById('f-index').value;
  var secF=document.getElementById('f-sector').value;
  var widF=document.getElementById('f-width').value;
  var fnoF=document.getElementById('f-fno').value;
  var priceF=parseFloat(document.getElementById('f-price').value)||0;

  var idxSet=null;
  if(IDX[idxKey]) idxSet=new Set(IDX[idxKey]);
  else if(idxKey==='nifty500'||idxKey==='fno') idxSet=null; // all

  results=[];
  allData.forEach(function(s){
    if(idxSet&&!idxSet.has(s.symbol)) return;
    if(secF&&s.sector!==secF) return;
    if(fnoF==='yes'&&!s.fno) return;
    if(priceF&&s.price<priceF) return;
    if(idxKey==='fno'&&!s.fno) return;

    var tfData=s[tf];
    if(!tfData||!tfData.inside) return;

    var wc=tfData.width_pct<0.5?'narrow':tfData.width_pct<=1.5?'medium':'wide';
    if(widF&&wc!==widF) return;

    results.push({
      symbol:s.symbol,name:s.name,sector:s.sector,fno:s.fno,
      price:s.price,change:s.change,
      pivot:tfData.curr_cpr.pivot,tc:tfData.curr_cpr.tc,bc:tfData.curr_cpr.bc,
      prevTc:tfData.prev_cpr.tc,prevBc:tfData.prev_cpr.bc,
      widthPct:tfData.width_pct,widthCat:wc
    });
  });

  var scanned=allData.filter(function(s){
    if(!IDX[idxKey]) return true;
    return IDX[idxKey]?new Set(IDX[idxKey]).has(s.symbol):true;
  }).length;

  document.getElementById('s-inside').textContent=results.length;
  document.getElementById('s-narrow').textContent=results.filter(function(r){return r.widthCat==='narrow';}).length;
  document.getElementById('s-wide').textContent=results.filter(function(r){return r.widthCat==='wide';}).length;
  document.getElementById('s-scanned').textContent=scanned||allData.length;
  document.getElementById('rcount').textContent=results.length+' stocks found';
  document.getElementById('dl-csv').disabled=results.length===0;
  document.getElementById('dl-xlsx').disabled=results.length===0;
  renderTable();
}

function doReset(){
  ['f-sector','f-width','f-fno'].forEach(function(id){document.getElementById(id).value='';});
  document.getElementById('f-price').value='';
  if(dataLoaded) applyFilters();
}

// ── Sort + Render ──────────────────────────────────────────────────────────────
function srt(k){
  if(sk===k) sa=!sa; else{sk=k;sa=true;}
  renderTable();
}
function n2(v){return v!=null&&!isNaN(v)?Number(v).toFixed(2):'—';}
function renderTable(){
  var sorted=results.slice().sort(function(a,b){
    var av=a[sk],bv=b[sk];
    if(typeof av==='number') return sa?av-bv:bv-av;
    return sa?String(av).localeCompare(String(bv)):String(bv).localeCompare(String(av));
  });
  var tbody=document.getElementById('tbody');
  if(!sorted.length){
    tbody.innerHTML='<tr><td colspan="12" class="empty-state">No Inside CPR stocks found. Try a broader index or clear filters.</td></tr>';
    return;
  }
  var mx=Math.max.apply(null,sorted.map(function(r){return r.widthPct;}));
  tbody.innerHTML=sorted.map(function(r){
    var bw=Math.round((r.widthPct/mx)*50);
    var wc=r.widthCat==='narrow'?'b-narrow':r.widthCat==='medium'?'b-medium':'b-wide';
    return '<tr>'
      +'<td><span class="sym">'+r.symbol+'</span></td>'
      +'<td><span class="company">'+r.name+'</span></td>'
      +'<td><span class="sector-tag">'+r.sector+'</span></td>'
      +'<td>'+(r.fno?'<span class="badge b-fno">F&O</span>':'<span style="color:#ccc;font-size:11px">—</span>')+'</td>'
      +'<td class="price-cell">&#8377;'+n2(r.price)+'</td>'
      +'<td class="'+(r.change>=0?'up':'dn')+'">'+(r.change>=0?'▲':'▼')+' '+Math.abs(r.change||0).toFixed(2)+'%</td>'
      +'<td class="pc">'+n2(r.pivot)+'</td>'
      +'<td class="tc-cell">'+n2(r.tc)+'</td>'
      +'<td class="bc-cell">'+n2(r.bc)+'</td>'
      +'<td class="pc">'+n2(r.prevTc)+'</td>'
      +'<td class="pc">'+n2(r.prevBc)+'</td>'
      +'<td><div class="wbar-wrap"><span style="font-size:13px">'+n2(r.widthPct)+'%</span><span class="wbar" style="width:'+bw+'px"></span><span class="badge '+wc+'">'+r.widthCat.charAt(0).toUpperCase()+r.widthCat.slice(1)+'</span></div></td>'
      +'</tr>';
  }).join('');
}

// ── Downloads ──────────────────────────────────────────────────────────────────
function dlCSV(){
  if(!results.length) return;
  var hdr=['Symbol','Company','Sector','F&O','CMP','Chg%','Pivot','Curr TC','Curr BC','Prev TC','Prev BC','Width%','Width Cat'];
  var rows=results.map(function(r){return[r.symbol,r.name,r.sector,r.fno?'Yes':'No',n2(r.price),n2(r.change)+'%',n2(r.pivot),n2(r.tc),n2(r.bc),n2(r.prevTc),n2(r.prevBc),n2(r.widthPct)+'%',r.widthCat];});
  var csv=['# Inside CPR Scanner — tradingwithgp.com','# Generated: '+new Date().toLocaleString('en-IN'),'',hdr.join(',')].concat(rows.map(function(r){return r.map(function(v){return '"'+String(v).replace(/"/g,'""')+'"';}).join(',');})).join('\n');
  var a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='inside_cpr_'+new Date().toISOString().slice(0,10)+'.csv';
  a.click();
}
function dlExcel(){
  if(!results.length) return;
  var hdr=['Symbol','Company','Sector','F&O','CMP','Chg%','Pivot','Curr TC','Curr BC','Prev TC','Prev BC','Width%','Width Cat'];
  var rows=results.map(function(r){return[r.symbol,r.name,r.sector,r.fno?'Yes':'No',n2(r.price),n2(r.change)+'%',n2(r.pivot),n2(r.tc),n2(r.bc),n2(r.prevTc),n2(r.prevBc),n2(r.widthPct)+'%',r.widthCat];});
  var xml='<?xml version="1.0" encoding="UTF-8"?><?mso-application progid="Excel.Sheet"?><Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><Styles><Style ss:ID="h"><Font ss:Bold="1" ss:Color="#FFFFFF"/><Interior ss:Color="#0a1628" ss:Pattern="Solid"/></Style></Styles><Worksheet ss:Name="Inside CPR"><Table>'+
    '<Row>'+hdr.map(function(h){return'<Cell ss:StyleID="h"><Data ss:Type="String">'+h+'</Data></Cell>';}).join('')+'</Row>'+
    rows.map(function(r){return'<Row>'+r.map(function(v){return'<Cell><Data ss:Type="String">'+String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</Data></Cell>';}).join('')+'</Row>';}).join('')+
    '</Table></Worksheet></Workbook>';
  var a=document.createElement('a');
  a.href='data:application/vnd.ms-excel;charset=utf-8,'+encodeURIComponent(xml);
  a.download='inside_cpr_'+new Date().toISOString().slice(0,10)+'.xls';
  a.click();
}

// ── Init ───────────────────────────────────────────────────────────────────────
updateFlag();
setInterval(updateFlag,60000);

// ===EMBEDDED_DATA_START===
// Data will be injected here by GitHub Actions
// ===EMBEDDED_DATA_END===
</script>
</body>
</html>
