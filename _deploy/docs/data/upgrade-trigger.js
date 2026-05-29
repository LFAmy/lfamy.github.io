
<!-- Embed this in any page to show upgrade prompts based on usage -->
<script>
(function(){
var usage=JSON.parse(localStorage.getItem("lf_usage")||'{"practice":0,"ocr":0,"paper":0,"plan":"free"}');
var plan=usage.plan||"free";
if(plan!=="free")return;

// Check if near limit
var nearLimit=(usage.practice>=12)||(usage.ocr>=1)||(usage.paper>=4);
if(!nearLimit)return;

// Show subtle upgrade prompt
var banner=document.createElement("div");
banner.style.cssText="background:linear-gradient(135deg,#FEF3C7,#FDE68A);color:#92400E;text-align:center;padding:8px 16px;font-size:12px;font-weight:700;position:fixed;bottom:0;left:0;right:0;z-index:9999;cursor:pointer";
banner.innerHTML='⭐ 免費版用量將滿 · <span style="text-decoration:underline">升級 Pro 解鎖全部功能 $199/月</span> · 點擊了解';
banner.onclick=function(){window.location.href="/docs/pricing.html"};
document.body.appendChild(banner);
})();
</script>
