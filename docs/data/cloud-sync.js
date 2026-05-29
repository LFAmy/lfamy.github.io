
// LF Cloud Sync — bidirectional localStorage ↔ Google Sheets
var LFCloud = {
  _url: null,
  _apiKey: 'lf_cloud_2026',
  _syncInterval: null,
  _syncEveryMs: 30000, // 30 seconds
  _pending: [],
  _lastSync: null,
  _studentId: null,

  init: function(opts) {
    opts = opts || {};
    this._url = opts.url || localStorage.getItem('lf_cloud_url');
    this._studentId = opts.studentId || localStorage.getItem('lf_student_id') || 'student_' + Date.now().toString(36);
    if (!localStorage.getItem('lf_student_id')) {
      localStorage.setItem('lf_student_id', this._studentId);
    }
    this._lastSync = localStorage.getItem('lf_cloud_last_sync');

    if (this._url && this._url.length > 5) {
      this._startAutoSync();
      this.pull(); // Pull remote data on init
    }

    return this;
  },

  get configured() { return !!this._url && this._url.length > 5; },

  configure: function(url, studentId) {
    this._url = url;
    localStorage.setItem('lf_cloud_url', url);
    if (studentId) {
      this._studentId = studentId;
      localStorage.setItem('lf_student_id', studentId);
    }
    this._startAutoSync();
    this.pull();
    return this;
  },

  _startAutoSync: function() {
    var self = this;
    if (this._syncInterval) clearInterval(this._syncInterval);
    this._syncInterval = setInterval(function() { self.pushPending(); }, this._syncEveryMs);
  },

  // --- PUSH: send local data to cloud ---
  push: function(record) {
    if (!this._url) return;
    this._pending.push(record);

    var self = this;
    var payload = {
      action: 'batch_sync',
      student_id: this._studentId,
      records: this._pending.slice()
    };

    fetch(this._url, {
      method: 'POST',
      mode: 'no-cors',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    }).then(function() {
      self._pending = [];
      self._lastSync = new Date().toISOString();
      localStorage.setItem('lf_cloud_last_sync', self._lastSync);
      self._updateStatus('synced');
    }).catch(function(err) {
      self._updateStatus('error');
      console.warn('LFCloud push failed, will retry:', err);
    });
  },

  pushPending: function() {
    if (this._pending.length === 0) return;
    this.push({type: 'heartbeat', ts: new Date().toISOString()});
  },

  // Push student profile
  pushStudent: function(studentData) {
    if (!this._url) return;
    fetch(this._url, {
      method: 'POST', mode: 'no-cors',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        action: 'save_student',
        student_id: this._studentId,
        student: Object.assign({student_id: this._studentId}, studentData)
      })
    }).catch(function() {});
  },

  // Push practice record
  pushPractice: function(practiceData) {
    this.push({
      type: 'practice',
      student_id: this._studentId,
      data: Object.assign({
        id: 'pr_' + Date.now(),
        student_id: this._studentId,
        date: new Date().toISOString().split('T')[0]
      }, practiceData)
    });
  },

  // Push badge
  pushBadge: function(badgeId, badgeName) {
    this.push({
      type: 'badge', student_id: this._studentId,
      data: {
        id: badgeId, name: badgeName,
        earned_date: new Date().toISOString().split('T')[0]
      }
    });
  },

  // Push monster update
  pushMonster: function(trapType, stage, defeats) {
    this.push({
      type: 'monster', student_id: this._studentId,
      data: {trap_type: trapType, stage: stage, defeats: defeats}
    });
  },

  // Push membership
  pushMembership: function(membershipData) {
    this.push({
      type: 'membership', student_id: this._studentId,
      data: membershipData
    });
  },

  // Push attendance
  pushAttendance: function(classId) {
    this.push({
      type: 'attendance', student_id: this._studentId,
      data: {
        id: 'att_' + Date.now(),
        student_id: this._studentId,
        class_id: classId,
        checkin_time: new Date().toISOString(),
        class_date: new Date().toISOString().split('T')[0]
      }
    });
  },

  // --- PULL: get remote data ---
  pull: function() {
    if (!this._url) return;
    var self = this;
    var url = this._url + '?action=get_sync_data&student_id=' + encodeURIComponent(this._studentId);

    fetch(url)
      .then(function(r) { return r.json(); })
      .then(function(result) {
        if (result.status !== 'ok' || !result.data) return;
        var d = result.data;

        // Merge student profile
        if (d.student) {
          localStorage.setItem('lf_student_profile', JSON.stringify(d.student));
        }

        // Merge badges (add any from cloud not in local)
        if (d.badges && d.badges.length > 0) {
          var localBadges = JSON.parse(localStorage.getItem('lf_gamification') || '{}');
          if (!localBadges.badges) localBadges.badges = {};
          d.badges.forEach(function(b) {
            if (!localBadges.badges[b.badge_id]) {
              localBadges.badges[b.badge_id] = b.earned_date;
            }
          });
          localStorage.setItem('lf_gamification', JSON.stringify(localBadges));
        }

        // Merge monsters
        if (d.monsters && d.monsters.length > 0) {
          var localGam = JSON.parse(localStorage.getItem('lf_gamification') || '{}');
          if (!localGam.monsterStages) localGam.monsterStages = {};
          if (!localGam.trapDefeats) localGam.trapDefeats = {};
          d.monsters.forEach(function(m) {
            localGam.monsterStages[m.trap_type] = Math.max(
              localGam.monsterStages[m.trap_type] || 0, m.stage
            );
            localGam.trapDefeats[m.trap_type] = Math.max(
              localGam.trapDefeats[m.trap_type] || 0, m.defeats
            );
          });
          localStorage.setItem('lf_gamification', JSON.stringify(localGam));
        }

        self._lastSync = new Date().toISOString();
        localStorage.setItem('lf_cloud_last_sync', self._lastSync);
        self._updateStatus('synced');
        self._fireEvent('pull_complete', result.data);
      })
      .catch(function(err) {
        self._updateStatus('offline');
        console.warn('LFCloud pull failed:', err);
      });
  },

  // --- Sync All (push all local → cloud) ---
  syncAll: function() {
    if (!this._url) return;
    var self = this;
    var studentData = {
      student_id: this._studentId,
      name: localStorage.getItem('lf_student_name') || '',
      grade: localStorage.getItem('lf_student_grade') || ''
    };
    this.pushStudent(studentData);

    // Push gamification state
    var gam = JSON.parse(localStorage.getItem('lf_gamification') || '{}');
    if (gam.badges) {
      Object.keys(gam.badges).forEach(function(badgeId) {
        self.pushBadge(badgeId, badgeId);
      });
    }
    if (gam.monsterStages) {
      Object.keys(gam.monsterStages).forEach(function(t) {
        self.pushMonster(t, gam.monsterStages[t], gam.trapDefeats[t] || 0);
      });
    }

    // Push membership
    var member = JSON.parse(localStorage.getItem('lf_active_membership') || 'null');
    if (member) {
      this.pushMembership(member);
    }

    this._updateStatus('syncing');
  },

  // --- Status ---
  _updateStatus: function(status) {
    var el = document.getElementById('lf-cloud-status');
    if (el) {
      var icons = {synced: '☁️', syncing: '🔄', offline: '⚡', error: '⚠️'};
      var labels = {synced: '已同步', syncing: '同步中…', offline: '離線', error: '同步失敗'};
      el.innerHTML = icons[status] + ' ' + labels[status];
    }
  },

  getStatus: function() {
    return {
      configured: this.configured,
      lastSync: this._lastSync,
      pending: this._pending.length,
      studentId: this._studentId,
      url: this._url ? this._url.substring(0, 50) + '…' : null
    };
  },

  // --- Event ---
  _listeners: {},
  on: function(event, fn) {
    if (!this._listeners[event]) this._listeners[event] = [];
    this._listeners[event].push(fn);
  },
  _fireEvent: function(event, data) {
    (this._listeners[event] || []).forEach(function(fn) { try { fn(data); } catch(e) {} });
  }
};

// Auto-init
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() {
    LFCloud.init();
  });
}
