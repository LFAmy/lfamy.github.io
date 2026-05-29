
// 霖楓學苑 Unified Data Layer
// Drop-in replacement for localStorage → Google Sheets migration ready
var LFData = {
    _storage: localStorage,
    _sheetsURL: null,

    init: function(sheetsURL){
        if(sheetsURL) this._sheetsURL = sheetsURL;
        return this;
    },

    get: function(key, fallback){
        try{
            var val = this._storage.getItem("lf_"+key);
            return val ? JSON.parse(val) : (fallback || null);
        }catch(e){ return fallback || null; }
    },

    set: function(key, value){
        try{
            this._storage.setItem("lf_"+key, JSON.stringify(value));
            // Cloud sync
            if(typeof LFCloud !== 'undefined' && LFCloud.configured){
                if(key==="gamification"){ LFCloud.push({type:"gamification",data:value}); }
                else if(key==="active_membership"){ LFCloud.pushMembership(value); }
                else if(key==="test_results"){ LFCloud.pushPractice(value[value.length-1]||{}); }
            }
            // Auto-sync to Sheets if configured (legacy)
            if(this._sheetsURL){
                fetch(this._sheetsURL, {
                    method: "POST", mode: "no-cors",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({key: "lf_"+key, value: value, timestamp: new Date().toISOString()})
                }).catch(function(){});
            }
        }catch(e){}
    },

    getAll: function(){
        var data = {};
        for(var i=0; i<this._storage.length; i++){
            var k = this._storage.key(i);
            if(k.startsWith("lf_")){
                try{ data[k] = JSON.parse(this._storage.getItem(k)); }catch(e){}
            }
        }
        return data;
    },

    export: function(){
        var data = this.getAll();
        var blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a"); a.href = url;
        a.download = "lf_data_backup_" + new Date().toISOString().split("T")[0] + ".json";
        a.click();
        return "Backup downloaded";
    },

    import: function(jsonData){
        var self = this;
        Object.entries(jsonData).forEach(function(e){
            self._storage.setItem(e[0], JSON.stringify(e[1]));
        });
        return Object.keys(jsonData).length + " keys imported";
    }
};
