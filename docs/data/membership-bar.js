document.addEventListener('DOMContentLoaded',function(){
var member=null,usage=null;
try{member=JSON.parse(localStorage.getItem('lf_active_membership'))}catch(e){}
try{usage=JSON.parse(localStorage.getItem('lf_usage'))}catch(e){}
var name=localStorage.getItem('lf_student_name')||'';
var bar=document.createElement('div');
bar.className='lf-member-bar';
bar.id='lfMemberBar';
bar.innerHTML='<div class="mb-left"><a href="/docs/index.html" class="mb-brand"><img src="logo.png" alt="霖楓學苑" style="height:24px"></a><span id="mbGreeting"></span></div><div class="mb-right" id="mbRight"></div>';
var style=document.createElement('style');
style.textContent='.lf-member-bar{background:linear-gradient(135deg,#1A3C6D,#1E4D8C);color:white;padding:6px 12px;display:flex;justify-content:space-between;align-items:center;font-size:12px;font-family:"Noto Sans HK","PingFang SC","Microsoft YaHei",sans-serif;z-index:9999;position:sticky;top:0;flex-wrap:wrap;gap:6px}.lf-member-bar a{color:white;text-decoration:none;font-weight:700;padding:4px 12px;border-radius:15px;transition:all 0.2s;white-space:nowrap}.lf-member-bar a:hover{background:rgba(255,255,255,0.1)}.lf-member-bar .mb-left{display:flex;align-items:center;gap:8px}.lf-member-bar .mb-right{display:flex;align-items:center;gap:6px}.lf-member-bar .mb-brand{font-weight:900;font-size:14px;color:#C9A84C;font-family:"Noto Serif HK",serif}.mb-badge{display:inline-block;padding:3px 10px;border-radius:10px;font-size:10px;font-weight:700}.mb-badge-free{background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7)}.mb-badge-pro{background:#C9A84C;color:#1A3C6D}.mb-badge-expiring{background:#DC2626;color:white}.mb-btn-login{background:rgba(255,255,255,0.15);color:white}.mb-btn-register{background:#DC2626;color:white;animation:mb-pulse 2s infinite}.mb-btn-upgrade{background:#C9A84C;color:#1A3C6D}@keyframes mb-pulse{0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,0.4)}50%{box-shadow:0 0 0 8px rgba(220,38,38,0)}}@media(max-width:500px){.lf-member-bar{font-size:10px;padding:6px 10px}.lf-member-bar .mb-brand{font-size:11px}}';
document.head.appendChild(style);
if(document.body.firstChild){document.body.insertBefore(bar,document.body.firstChild)}else{document.body.appendChild(bar)}

var right=bar.querySelector('#mbRight');
var greeting=bar.querySelector('#mbGreeting');
if(member&&member.expiry&&new Date(member.expiry)>new Date()){
var days=Math.ceil((new Date(member.expiry)-new Date())/86400000);
var pn=member.plan==='annual'?'年費':member.plan==='trial'?'試用':'Pro';
greeting.textContent=(name?name+'，':'')+'你好！';
var bc=days<=7?'mb-badge-expiring':'mb-badge-pro';
right.innerHTML='<span class="mb-badge '+bc+'">'+pn+' · 剩'+days+'日</span><a href="/docs/student-platform.html">學習平台</a><a href="/docs/pricing.html">續期</a>';
}else if(usage&&usage.usedThisMonth>0){
var left=15-(usage.usedThisMonth||0);
greeting.textContent='免費版用戶';
right.innerHTML='<span class="mb-badge mb-badge-free">免費 · '+Math.max(0,left)+'/15次</span><a href="/docs/pricing.html" class="mb-btn-upgrade">升級 Pro</a><a href="/docs/student-platform.html">學習平台</a>';
}else{
greeting.textContent='歡迎！';
right.innerHTML='<a href="/docs/activate.html" class="mb-btn-login">登入/激活</a><a href="/docs/enroll.html" class="mb-btn-register">免費註冊</a>';
}
});