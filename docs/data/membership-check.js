
// Membership status checker - include in premium pages
var LFMembership={check:function(){
var m=JSON.parse(localStorage.getItem("lf_active_membership"));
if(!m)return {active:false,plan:"free"};
var expired=new Date(m.expiry)<new Date();
if(expired){localStorage.removeItem("lf_active_membership");return {active:false,plan:"free"}}
return {active:true,plan:m.plan,expiry:m.expiry,daysLeft:Math.ceil((new Date(m.expiry)-new Date())/(86400000))};
},requirePro:function(){var s=this.check();if(!s.active){if(confirm("此功能需要 Pro 會員。要升級嗎？")){window.location.href="/docs/pricing.html"}return false}return true}};
