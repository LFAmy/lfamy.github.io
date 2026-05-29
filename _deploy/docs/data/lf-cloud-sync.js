// ═══════════════════════════════════════════
// 霖楓學苑 · LF Cloud Sync Engine v1.0
// Universal data layer: localStorage now → Firebase when keys available
// ═══════════════════════════════════════════

var LFCloud = {
  _ready: false,
  _firebaseAvailable: false,
  _listeners: {},
  _queue: [],
  
  // ── CONFIG ──
  config: {
    appName: 'lam-fung-academy',
    version: '1.0',
    collections: ['students','diagnostics','progress','reports','messages','settings'],
    syncInterval: 30000 // 30s auto-sync
  },
  
  // ── INIT ──
  init: function(config) {
    var self = this;
    if(config) Object.assign(this.config, config);
    
    // Try Firebase
    if(typeof firebase !== 'undefined' && firebase.apps && firebase.apps.length>0){
      this._firebaseAvailable = true;
      this._db = firebase.firestore();
      console.log('☁️ LFCloud: Firebase connected');
    } else {
      console.log('💾 LFCloud: localStorage mode (Firebase not configured)');
    }
    
    this._ready = true;
    this._processQueue();
    
    // Auto-sync
    setInterval(function(){ self.sync(); }, this.config.syncInterval);
    
    return this;
  },
  
  // ── UNIVERSAL GET ──
  get: function(collection, key) {
    return new Promise(function(resolve, reject) {
      var stored = localStorage.getItem('lf_cloud_'+collection+'_'+key);
      if(stored){
        try { resolve(JSON.parse(stored)); }
        catch(e){ resolve(stored); }
      } else {
        resolve(null);
      }
    });
  },
  
  // ── UNIVERSAL SET ──
  set: function(collection, key, data) {
    var self = this;
    return new Promise(function(resolve, reject) {
      // Always save to localStorage first (fast)
      try {
        localStorage.setItem('lf_cloud_'+collection+'_'+key, JSON.stringify(data));
      } catch(e) {
        // localStorage full - fallback
        console.warn('LFCloud: localStorage full, cleaning old data');
        self._cleanOldData();
        try { localStorage.setItem('lf_cloud_'+collection+'_'+key, JSON.stringify(data)); } catch(e2){}
      }
      
      // If Firebase available, sync to cloud
      if(self._firebaseAvailable && self._db){
        self._db.collection(collection).doc(String(key)).set({
          data: data,
          updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
          version: self.config.version
        }).then(resolve).catch(function(err){
          console.warn('LFCloud: Firebase write failed, data saved locally', err);
          resolve({local: true});
        });
      } else {
        resolve({local: true});
      }
      
      // Trigger listeners
      self._notify(collection, key, data);
    });
  },
  
  // ── QUERY COLLECTION ──
  query: function(collection, filter) {
    var self = this;
    return new Promise(function(resolve) {
      var results = [];
      var prefix = 'lf_cloud_'+collection+'_';
      for(var i=0;i<localStorage.length;i++){
        var key = localStorage.key(i);
        if(key && key.indexOf(prefix)===0){
          try {
            var data = JSON.parse(localStorage.getItem(key));
            if(!filter || self._matchFilter(data, filter)){
              results.push({id: key.replace(prefix,''), data: data});
            }
          } catch(e){}
        }
      }
      resolve(results);
    });
  },
  
  _matchFilter: function(data, filter) {
    for(var k in filter){
      if(data[k] !== filter[k]) return false;
    }
    return true;
  },
  
  // ── DELETE ──
  delete: function(collection, key) {
    localStorage.removeItem('lf_cloud_'+collection+'_'+key);
    if(this._firebaseAvailable && this._db){
      this._db.collection(collection).doc(String(key)).delete().catch(function(){});
    }
  },
  
  // ── SYNC ENGINE ──
  sync: function() {
    if(!this._firebaseAvailable) return Promise.resolve({local: true});
    
    var self = this;
    var promises = [];
    
    for(var c=0;c<this.config.collections.length;c++){
      var col = this.config.collections[c];
      var prefix = 'lf_cloud_'+col+'_';
      var allKeys = [];
      for(var i=0;i<localStorage.length;i++){
        var key = localStorage.key(i);
        if(key && key.indexOf(prefix)===0){
          allKeys.push(key.replace(prefix,''));
        }
      }
      
      // Batch sync each collection
      for(var k=0;k<allKeys.length;k++){
        (function(collection, key){
          promises.push(
            self.get(collection, key).then(function(data){
              if(data && self._db){
                return self._db.collection(collection).doc(String(key)).set({
                  data: data,
                  syncedAt: new Date().toISOString()
                }).catch(function(){});
              }
            })
          );
        })(col, allKeys[k]);
      }
    }
    
    return Promise.all(promises);
  },
  
  // ── LISTENERS (reactive data) ──
  on: function(collection, key, callback) {
    var id = collection+'_'+key;
    if(!this._listeners[id]) this._listeners[id] = [];
    this._listeners[id].push(callback);
    
    // Initial load
    this.get(collection, key).then(function(data){
      if(data) callback(data);
    });
  },
  
  _notify: function(collection, key, data) {
    var id = collection+'_'+key;
    if(this._listeners[id]){
      this._listeners[id].forEach(function(cb){ cb(data); });
    }
  },
  
  // ── QUEUE (for offline support) ──
  _processQueue: function() {
    var queue = JSON.parse(localStorage.getItem('lf_cloud_queue')||'[]');
    this._queue = queue;
  },
  
  enqueue: function(action) {
    this._queue.push({action: action, timestamp: Date.now()});
    localStorage.setItem('lf_cloud_queue', JSON.stringify(this._queue));
  },
  
  // ── CLEANUP ──
  _cleanOldData: function() {
    var keys = [];
    for(var i=0;i<localStorage.length;i++){
      var k = localStorage.key(i);
      if(k && k.indexOf('lf_cloud_')===0) keys.push(k);
    }
    // Remove oldest 20%
    keys.sort();
    var removeCount = Math.ceil(keys.length*0.2);
    for(var j=0;j<removeCount;j++){
      localStorage.removeItem(keys[j]);
    }
  },
  
  // ── STUDENT PROFILE ──
  getStudentProfile: function(studentId) {
    return this.get('students', studentId||'current');
  },
  
  saveStudentProfile: function(profile) {
    return this.set('students', profile.id||'current', profile);
  },
  
  // ── DIAGNOSTIC RESULTS ──
  saveDiagnostic: function(result) {
    var id = 'diag_'+Date.now();
    return this.set('diagnostics', id, {
      id: id,
      grade: result.grade,
      score: result.score,
      trapResults: result.trapResults,
      weakTraps: result.weakTraps,
      timestamp: new Date().toISOString(),
      answers: result.answers
    });
  },
  
  getLatestDiagnostic: function() {
    var self = this;
    return this.query('diagnostics', {}).then(function(results){
      if(results.length===0) return null;
      results.sort(function(a,b){
        return new Date(b.data.timestamp) - new Date(a.data.timestamp);
      });
      return results[0].data;
    });
  },
  
  // ── PROGRESS SNAPSHOT ──
  saveProgressSnapshot: function() {
    var self = this;
    var gf = null;
    try{ gf = JSON.parse(localStorage.getItem('lf_gamification')); }catch(e){}
    if(!gf) return Promise.resolve(null);
    
    return this.set('progress', 'snapshot_'+new Date().toISOString().split('T')[0], {
      xp: gf.xp,
      level: gf.level,
      totalCorrect: gf.totalCorrect,
      totalQuestions: gf.totalQuestions,
      accuracy: gf.totalQuestions>0?Math.round(gf.totalCorrect/gf.totalQuestions*100):0,
      streak: gf.currentStreak,
      bossDefeats: Object.keys(gf.bossDefeats||{}).length,
      trapDefeats: gf.trapDefeats,
      date: new Date().toISOString().split('T')[0]
    });
  },
  
  // ── PARENT REPORT ──
  generateParentReport: function() {
    var self = this;
    return Promise.all([
      this.getLatestDiagnostic(),
      this.query('progress', {}),
      new Promise(function(resolve){
        var gf = null;
        try{ gf = JSON.parse(localStorage.getItem('lf_gamification')); }catch(e){}
        resolve(gf);
      })
    ]).then(function(results){
      var diag = results[0];
      var progressHistory = results[1];
      var gf = results[2];
      
      var report = {
        generatedAt: new Date().toISOString(),
        diagnostic: diag,
        gamification: gf?{
          xp: gf.xp, level: gf.level,
          totalQuestions: gf.totalQuestions,
          accuracy: gf.totalQuestions>0?Math.round(gf.totalCorrect/gf.totalQuestions*100):0,
          streak: gf.currentStreak,
          bossDefeats: Object.keys(gf.bossDefeats||{}).length
        }:null,
        progressHistory: progressHistory.map(function(p){return p.data;})
      };
      
      return self.set('reports', 'latest', report).then(function(){ return report; });
    });
  }
};

// Auto-init
if(typeof window !== 'undefined'){
  window.LFCloud = LFCloud;
  document.addEventListener('DOMContentLoaded', function(){
    LFCloud.init();
  });
}

// Export for module use
if(typeof module !== 'undefined' && module.exports){
  module.exports = LFCloud;
}
