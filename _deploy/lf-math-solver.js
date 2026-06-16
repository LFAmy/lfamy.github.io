// LF Academy Client-Side Math Solver v1.0
// Direct computation when Render backend is unavailable
var MATH_SOLVER = {
  solve: function(question) {
    var q = question.replace(/[\uFF1F?\u3002\uFF0C,]/g," ").replace(/\s+/g," ").trim();
    var nums = q.match(/[\d.]+/g);
    if (!nums || nums.length < 1) return null;
    
    var ns = [];
    for (var i = 0; i < nums.length; i++) {
      var n = parseFloat(nums[i]);
      if (!isNaN(n)) ns.push(n);
    }
    if (ns.length < 1) return null;
    
    var result = null;
    if (q.indexOf("+") >= 0 || q.indexOf("\u52A0") >= 0) {
      var total = ns[0];
      var stepStr = total + "";
      for (var i = 1; i < ns.length; i++) { total += ns[i]; stepStr += " + " + ns[i]; }
      result = { answer: total, steps: stepStr + " = " + total, op: "\u52A0\u6CD5" };
    } else if (q.indexOf("\u2212") >= 0 || q.indexOf("\u2013") >= 0 || q.indexOf("\u2014") >= 0 || q.indexOf("\u6E1B") >= 0 || (q.indexOf("-") >= 0 && q.indexOf("\u00D7") < 0 && q.indexOf("/") < 0)) {
      if (ns.length >= 2) {
        result = { answer: ns[0] - ns[1], steps: ns[0] + " - " + ns[1] + " = " + (ns[0] - ns[1]), op: "\u6E1B\u6CD5" };
      }
    } else if (q.indexOf("\u00D7") >= 0 || q.indexOf("\uFF0A") >= 0 || q.indexOf("*") >= 0 || q.indexOf("x") >= 0 || q.indexOf("\u4E58") >= 0) {
      if (ns.length >= 2) {
        result = { answer: ns[0] * ns[1], steps: ns[0] + " \u00D7 " + ns[1] + " = " + (ns[0] * ns[1]), op: "\u4E58\u6CD5" };
      }
    } else if (q.indexOf("\u00F7") >= 0 || q.indexOf("/") >= 0 || q.indexOf("\u9664") >= 0) {
      if (ns.length >= 2 && ns[1] !== 0) {
        result = { answer: ns[0] / ns[1], steps: ns[0] + " \u00F7 " + ns[1] + " = " + (ns[0] / ns[1]), op: "\u9664\u6CD5" };
      }
    } else if (q.indexOf("%") >= 0 || q.indexOf("\u767E\u5206") >= 0 || q.indexOf("\u6298") >= 0) {
      if (ns.length >= 1) {
        var pct = ns[0], base = ns.length >= 2 ? ns[1] : 100;
        result = { answer: base * pct / 100, steps: base + " \u00D7 " + pct + "% = " + base + " \u00D7 " + (pct/100) + " = " + (base * pct / 100), op: "\u767E\u5206\u6578" };
      }
    }
    
    if (!result && ns.length >= 1 && (q.indexOf("=\u5E7E\u591A") >= 0 || q.indexOf("= ?") >= 0)) {
      if (ns.length >= 2) {
        result = { answer: ns[0] + ns[1], steps: ns[0] + " + " + ns[1] + " = " + (ns[0] + ns[1]), op: "\u8A08\u7B97" };
      }
    }
    
    return result;
  },
  
  teach: function(question, solved) {
    if (!solved) return null;
    return "\uD83D\uDCA1 <strong>\u8A08\u7B97\u6B65\u9A5F\uFF1A</strong>\n" +
      "\u2460\uFE0F \u984C\u76EE\uFF1A" + question + "\n" +
      "\u2461\uFE0F \u904B\u7B97\uFF1A" + solved.op + "\n" +
      "\u2462\uFE0F \u6B65\u9A5F\uFF1A" + solved.steps + "\n" +
      "\u2705 \u7B54\u6848\uFF1A" + solved.answer + "\n\n" +
      "\uD83D\uDCD6 \u89E3\u91CB\uFF1A\u5148\u770B\u6E05\u695A\u984C\u76EE\u554F\u4EC0\u9EBC\uFF0C\u5206\u6B65\u8A08\u7B97\uFF0C\u8A08\u5B8C\u6AA2\u67E5\uFF01";
  }
};
console.log("MATH_SOLVER v1.0 loaded");