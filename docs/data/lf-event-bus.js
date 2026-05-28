// ═══════════════════════════════════════════════════════════
// 霖楓全域腦 v7.0 · Unified Intelligence Event Bus
// 統一事件總線 — 捕捉·分析·觸發·閉環
// ═══════════════════════════════════════════════════════════
// v7.0 新增：
//   - AI 引擎自動連接（lf_api_client.js）
//   - 事件觸發自動化（診斷→分析→報告→推送）
//   - 陷阱指紋即時更新
//   - 雙向 Firestore 同步（offline→online→AI→store）
//   - 批次上傳優化（500ms 去抖）
// ═══════════════════════════════════════════════════════════

var LF = window.LF || {};

LF.EventBus = (function() {
  var _queue = [];
  var _listeners = {};
  var _sessionId = "";
  var _userId = "";
  var _initialized = false;
  var _batchTimer = null;
  var _pendingEvents = [];
  var _apiAvailable = false;

  function _genId(prefix) {
    return prefix + "_" + Date.now().toString(36) + "_" + Math.random().toString(36).substr(2, 6);
  }

  function _loadBuffer() {
    try { return JSON.parse(localStorage.getItem("lf_event_buffer") || "[]"); }
    catch(e) { return []; }
  }

  function _saveBuffer(events) {
    try {
      if (events.length > 500) events = events.slice(-500);
      localStorage.setItem("lf_event_buffer", JSON.stringify(events));
    } catch(e) {}
  }

  // Check if AI API is available
  function _checkAPI() {
    if (typeof LF_API !== "undefined") {
      _apiAvailable = true;
      return;
    }
    // Try loading the API client dynamically
    var script = document.createElement("script");
    script.src = "/docs/data/lf-api-client.js";
    script.onload = function() { _apiAvailable = true; };
    document.head.appendChild(script);
  }

  // ═════════════════════════════════════
  // AI INTEGRATION — 事件觸發 AI 分析
  // ═════════════════════════════════════

  function _triggerAI(event) {
    if (!_apiAvailable || typeof LF_API === "undefined") return;

    switch(event.name) {
      case "diagnostic_complete":
        // 診斷完成 → AI 分析 → 更新陷阱指紋
        _callAI("analyze", {
          student_name: _userId,
          progress_data: [event.data]
        }).then(function(result) {
          if (result && result.analysis) {
            localStorage.setItem("lf_trap_fingerprint", JSON.stringify(result.analysis));
            _notifyListeners("profile_updated", result.analysis);
          }
        });
        break;

      case "question_answered":
        // 連續 3 題錯同一陷阱 → 自動生成提示
        if (!event.data.correct) {
          var trapCount = _getTrapStreak(event.data.trapType);
          if (trapCount >= 3) {
            _callAI("hints", {
              question: event.data.question || "",
              model_answer: event.data.correctAnswer || ""
            }).then(function(result) {
              if (result && result.hints) {
                _notifyListeners("hint_needed", {
                  trapType: event.data.trapType,
                  hints: result.hints
                });
              }
            });
          }
        }
        break;

      case "lesson_complete":
        // 課堂完成 → 自動生成家長報告
        _callAI("report", {
          student_name: event.data.studentName || _userId,
          today_data: event.data
        }).then(function(result) {
          if (result && result.summary) {
            localStorage.setItem("lf_last_report", result.summary);
            _notifyListeners("report_generated", {
              summary: result.summary,
              lessonId: event.data.lessonId
            });
          }
        });

        // 更新學生陷阱指紋
        if (event.data.traps) {
          var fp = _getTrapFingerprint();
          Object.keys(event.data.traps).forEach(function(trap) {
            if (!fp[trap]) fp[trap] = { total: 0, correct: 0 };
            fp[trap].total += event.data.traps[trap].total || 0;
            fp[trap].correct += event.data.traps[trap].correct || 0;
          });
          localStorage.setItem("lf_trap_fingerprint", JSON.stringify(fp));
        }
        break;

      case "churn_risk":
        // 流失風險 → 自動觸發挽回行動
        _notifyListeners("churn_alert", {
          userId: _userId,
          reason: event.data.reason,
          daysInactive: event.data.daysInactive
        });
        break;
    }
  }

  function _callAI(endpoint, data) {
    if (typeof LF_API !== "undefined" && LF_API[endpoint]) {
      return LF_API[endpoint](data.student_name || data.question || "", data);
    }
    return Promise.resolve(null);
  }

  function _getTrapStreak(trapType) {
    try {
      var events = _loadBuffer();
      var recent = events.filter(function(e) {
        return e.name === "question_answered" && e.data.trapType === trapType && !e.data.correct;
      });
      return recent.slice(-10).length;
    } catch(e) { return 0; }
  }

  function _getTrapFingerprint() {
    try { return JSON.parse(localStorage.getItem("lf_trap_fingerprint") || "{}"); }
    catch(e) { return {}; }
  }

  function _notifyListeners(eventName, data) {
    var list = _listeners[eventName] || [];
    list.forEach(function(fn) { try { fn(data); } catch(e) {} });
    ( _listeners["*"] || []).forEach(function(fn) { try { fn({name: eventName, data: data}); } catch(e) {} });
  }

  // ═════════════════════════════════════
  // FIRESTORE BATCH SYNC — 批次同步
  // ═════════════════════════════════════

  function _scheduleBatch() {
    if (_batchTimer) return;
    _batchTimer = setTimeout(function() {
      _batchTimer = null;
      _flushBatch();
    }, 500); // 500ms debounce
  }

  function _flushBatch() {
    if (_pendingEvents.length === 0) return;
    var batch = _pendingEvents.slice();
    _pendingEvents = [];

    // Save to Firestore if available
    if (typeof firebase !== "undefined" && firebase.firestore) {
      var db = firebase.firestore();
      batch.forEach(function(event) {
        db.collection("events").add(event).catch(function() {});
      });
    }

    // Also try API batch endpoint
    if (_apiAvailable && typeof LF_API !== "undefined" && LF_API.batchHints) {
      // For batch processing of answers
      var answers = batch.filter(function(e) { return e.name === "question_answered"; });
      if (answers.length >= 3) {
        LF_API.batchHints(answers.map(function(e) {
          return { question: e.data.question || "", answer: e.data.correctAnswer || "" };
        })).catch(function() {});
      }
    }

    // Track batch
    _notifyListeners("batch_synced", { count: batch.length });
  }

  // ═════════════════════════════════════
  // PUBLIC API
  // ═════════════════════════════════════

  return {
    init: function(options) {
      options = options || {};
      _sessionId = options.sessionId || _genId("sess");
      _userId = options.userId || localStorage.getItem("lf_user_id") || _genId("user");
      if (!localStorage.getItem("lf_user_id")) {
        localStorage.setItem("lf_user_id", _userId);
      }
      _initialized = true;
      _checkAPI();

      // Flush queued events
      while (_queue.length > 0) {
        this.track(_queue.shift().name, _queue.shift().data);
      }

      console.log("[LFv7] EventBus initialized | user:", _userId, "| session:", _sessionId);
      return this;
    },

    track: function(eventName, data) {
      var event = {
        name: eventName,
        data: data || {},
        timestamp: new Date().toISOString(),
        sessionId: _sessionId,
        userId: _userId,
        page: window.location.pathname,
        referrer: document.referrer || ""
      };

      if (!_initialized) {
        _queue.push(event);
        return this;
      }

      // 1. Save to localStorage buffer
      var buffer = _loadBuffer();
      buffer.push(event);
      _saveBuffer(buffer);

      // 2. Schedule batch sync
      _pendingEvents.push(event);
      _scheduleBatch();

      // 3. Trigger AI analysis
      _triggerAI(event);

      // 4. Notify local listeners
      _notifyListeners(eventName, event.data);
      _notifyListeners("*", event);

      // 5. Google Analytics
      if (typeof gtag !== "undefined") {
        gtag("event", eventName, event.data);
      }

      return this;
    },

    on: function(eventName, fn) {
      if (!_listeners[eventName]) _listeners[eventName] = [];
      _listeners[eventName].push(fn);
      return this;
    },

    off: function(eventName, fn) {
      var list = _listeners[eventName];
      if (list) {
        _listeners[eventName] = list.filter(function(f) { return f !== fn; });
      }
      return this;
    },

    getEvents: function(eventName, limit) {
      limit = limit || 50;
      var buffer = _loadBuffer();
      if (eventName) buffer = buffer.filter(function(e) { return e.name === eventName; });
      return buffer.slice(-limit);
    },

    getStats: function() {
      var events = _loadBuffer();
      var stats = { total: events.length, byName: {}, last24h: 0 };
      var now = new Date();
      events.forEach(function(e) {
        stats.byName[e.name] = (stats.byName[e.name] || 0) + 1;
        if (new Date(e.timestamp) > new Date(now - 86400000)) stats.last24h++;
      });
      return stats;
    },

    getTrapFingerprint: function() {
      return _getTrapFingerprint();
    },

    buildProfile: function() {
      var events = _loadBuffer();
      var profile = {
        userId: _userId,
        totalDiagnostics: 0,
        totalQuestions: 0,
        correctRate: 0,
        trapMastery: _getTrapFingerprint(),
        lastActive: null,
        streakDays: 0
      };

      var correct = 0, total = 0;
      var activeDates = {};

      events.forEach(function(e) {
        var d = new Date(e.timestamp).toDateString();
        activeDates[d] = true;

        switch(e.name) {
          case "diagnostic_complete":
            profile.totalDiagnostics++;
            profile.lastActive = e.timestamp;
            if (e.data.score) profile.latestScore = e.data.score;
            break;
          case "question_answered":
            total++;
            profile.totalQuestions++;
            if (e.data.correct) correct++;
            break;
        }
      });

      profile.correctRate = total > 0 ? Math.round(correct / total * 100) : 0;
      profile.streakDays = Object.keys(activeDates).length;
      return profile;
    }
  };
})();

// ═══════════════════════════════════════════════════════════
// AUTO TRACKING — 自動監聽常見事件
// ═══════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", function() {
  LF.EventBus.init();

  // Track page view
  LF.EventBus.track("page_view", {
    title: document.title,
    path: window.location.pathname
  });

  // Auto-track form submissions
  document.addEventListener("submit", function(e) {
    var form = e.target;
    if (form.id === "signupForm" || form.action?.match(/signup|register/)) {
      LF.EventBus.track("form_submitted", { formType: "signup" });
    }
  });

  // Auto-track link clicks
  document.addEventListener("click", function(e) {
    var link = e.target.closest("a");
    if (!link) return;
    var href = link.getAttribute("href") || "";
    if (href.match(/wa\.me|whatsapp/i)) {
      LF.EventBus.track("whatsapp_click", { target: href.substring(0, 50) });
    }
  });
});

// ═══════════════════════════════════════════════════════════
// EVENT HELPERS
// ═══════════════════════════════════════════════════════════

LF.track = {
  diagnosticComplete: function(score, weaknesses, strengths) {
    LF.EventBus.track("diagnostic_complete", { score: score, weaknesses: weaknesses, strengths: strengths });
  },
  questionAnswered: function(questionId, correct, trapType, question, correctAnswer) {
    LF.EventBus.track("question_answered", {
      questionId: questionId, correct: correct, trapType: trapType,
      question: question, correctAnswer: correctAnswer,
      timeSpent: 0
    });
  },
  trialBooked: function(grade, source) {
    LF.EventBus.track("trial_booked", { grade: grade, source: source || "website" });
  },
  lessonComplete: function(lessonId, traps, studentName) {
    LF.EventBus.track("lesson_complete", {
      lessonId: lessonId, traps: traps, studentName: studentName, satisfaction: 0
    });
  },
  enrollmentComplete: function(plan, price) {
    LF.EventBus.track("enrollment_complete", { plan: plan, price: price });
  },
  churnRisk: function(reason, daysInactive) {
    LF.EventBus.track("churn_risk", { reason: reason, daysInactive: daysInactive });
  },
  buttonClick: function(buttonName) {
    LF.EventBus.track("button_click", { button: buttonName });
  }
};

console.log("[LFv7] 🧠 Unified Intelligence Event Bus v7.0 loaded");
