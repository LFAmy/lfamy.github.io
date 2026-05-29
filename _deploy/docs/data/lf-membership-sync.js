// ═══════════════════════════════════════════
// 霖楓學苑 LF Academy · 會員系統同步 v2.0
// Firebase Firestore 持久化 · 跨裝置同步
// ═══════════════════════════════════════════
(function() {
  // Wait for Firebase to be ready
  function waitForFirebase(cb, tries) {
    tries = tries || 0;
    if (typeof firebase !== 'undefined' && firebase.firestore) {
      cb();
    } else if (tries < 50) {
      setTimeout(function() { waitForFirebase(cb, tries + 1); }, 200);
    } else {
      console.warn('[LF-Sync] Firebase not available, running offline');
    }
  }

  waitForFirebase(function() {
    var db = firebase.firestore();
    var auth = firebase.auth();
    
    window.LF_Sync = {
      db: db,
      auth: auth,
      ready: true,
      
      // ═══ User Profile ═══
      saveProfile: function(data) {
        var user = auth.currentUser;
        if (!user) return Promise.reject('not logged in');
        return db.collection('users').doc(user.uid).set({
          displayName: data.name || user.displayName,
          email: user.email,
          role: data.role || 'student',
          grade: data.grade || '',
          phone: data.phone || '',
          updatedAt: firebase.firestore.FieldValue.serverTimestamp()
        }, { merge: true });
      },
      
      getProfile: function() {
        var user = auth.currentUser;
        if (!user) return Promise.reject('not logged in');
        return db.collection('users').doc(user.uid).get().then(function(doc) {
          return doc.exists ? doc.data() : null;
        });
      },
      
      // ═══ Diagnostic Results ═══
      saveDiagnostic: function(result) {
        var user = auth.currentUser;
        var data = {
          grade: result.grade,
          traps: result.traps || {},
          score: result.score || 0,
          totalQuestions: result.totalQuestions || 10,
          completedAt: firebase.firestore.FieldValue.serverTimestamp()
        };
        if (user) {
          data.uid = user.uid;
          return db.collection('diagnostics').add(data);
        } else {
          // Anonymous: save locally
          var d = JSON.parse(localStorage.getItem('lf_diagnostics') || '[]');
          d.push(Object.assign({}, data, { completedAt: new Date().toISOString() }));
          if (d.length > 5) d.shift();
          localStorage.setItem('lf_diagnostics', JSON.stringify(d));
          return Promise.resolve({ local: true });
        }
      },
      
      getDiagnostics: function() {
        var user = auth.currentUser;
        if (user) {
          return db.collection('diagnostics')
            .where('uid', '==', user.uid)
            .orderBy('completedAt', 'desc')
            .limit(10)
            .get()
            .then(function(snapshot) {
              return snapshot.docs.map(function(d) { return d.data(); });
            });
        } else {
          return Promise.resolve(JSON.parse(localStorage.getItem('lf_diagnostics') || '[]'));
        }
      },
      
      // ═══ Practice History ═══
      savePractice: function(data) {
        var user = auth.currentUser;
        var record = {
          topic: data.topic,
          correct: data.correct || 0,
          total: data.total || 0,
          trapsHit: data.trapsHit || [],
          completedAt: firebase.firestore.FieldValue.serverTimestamp()
        };
        if (user) {
          record.uid = user.uid;
          return db.collection('practice_history').add(record);
        } else {
          var h = JSON.parse(localStorage.getItem('lf_practice_history') || '[]');
          h.push(Object.assign({}, record, { completedAt: new Date().toISOString() }));
          if (h.length > 50) h.splice(0, h.length - 50);
          localStorage.setItem('lf_practice_history', JSON.stringify(h));
          return Promise.resolve({ local: true });
        }
      },
      
      getPracticeHistory: function(limit) {
        limit = limit || 20;
        var user = auth.currentUser;
        if (user) {
          return db.collection('practice_history')
            .where('uid', '==', user.uid)
            .orderBy('completedAt', 'desc')
            .limit(limit)
            .get()
            .then(function(snapshot) {
              return snapshot.docs.map(function(d) { return d.data(); });
            });
        } else {
          return Promise.resolve(JSON.parse(localStorage.getItem('lf_practice_history') || '[]').slice(-limit));
        }
      },
      
      // ═══ Progress Stats ═══
      getStats: function() {
        var user = auth.currentUser;
        if (user) {
          return Promise.all([
            this.getDiagnostics(),
            this.getPracticeHistory(100)
          ]).then(function(results) {
            var diags = results[0], practices = results[1];
            var totalCorrect = practices.reduce(function(s, p) { return s + (p.correct || 0); }, 0);
            var totalQ = practices.reduce(function(s, p) { return s + (p.total || 0); }, 0);
            return {
              diagnostics: diags.length,
              practices: practices.length,
              totalCorrect: totalCorrect,
              totalQuestions: totalQ,
              accuracy: totalQ > 0 ? Math.round(totalCorrect / totalQ * 100) : 0,
              lastDiagnostic: diags.length > 0 ? diags[0] : null
            };
          });
        } else {
          var d = JSON.parse(localStorage.getItem('lf_diagnostics') || '[]');
          var h = JSON.parse(localStorage.getItem('lf_practice_history') || '[]');
          return Promise.resolve({
            diagnostics: d.length,
            practices: h.length,
            totalCorrect: 0,
            totalQuestions: 0,
            accuracy: 0,
            lastDiagnostic: d.length > 0 ? d[d.length-1] : null
          });
        }
      },
      
      // ═══ Migration: Local → Cloud ═══
      migrateLocalToCloud: function() {
        var user = auth.currentUser;
        if (!user) return Promise.reject('not logged in');
        
        var promises = [];
        var diags = JSON.parse(localStorage.getItem('lf_diagnostics') || '[]');
        var practices = JSON.parse(localStorage.getItem('lf_practice_history') || '[]');
        
        diags.forEach(function(d) {
          d.uid = user.uid;
          promises.push(db.collection('diagnostics').add(d));
        });
        practices.forEach(function(p) {
          p.uid = user.uid;
          promises.push(db.collection('practice_history').add(p));
        });
        
        return Promise.all(promises).then(function() {
          localStorage.removeItem('lf_diagnostics');
          localStorage.removeItem('lf_practice_history');
          console.log('[LF-Sync] Migrated ' + (diags.length + practices.length) + ' records to cloud');
          return { migrated: diags.length + practices.length };
        });
      }
    };
    
    // ═══ Auto-sync on login ═══
    auth.onAuthStateChanged(function(user) {
      if (user) {
        console.log('[LF-Sync] User logged in, syncing...');
        window.LF_Sync.migrateLocalToCloud().catch(function() {});
      }
    });
    
    console.log('[LF-Sync] 🍁 Membership sync ready');
  });
})();
