// ═══════════════════════════════════════════
// 霖楓學苑 · Real-time Battle Engine
// WebSocket/SignalR-ready with simulation fallback
// ═══════════════════════════════════════════

var LFBattle = {
  mode: 'simulation', // simulation | websocket | signalr
  roomId: null,
  players: [],
  scores: {},
  currentQuestion: null,
  timerSec: 0,
  
  // ── INIT ──
  init: function(config) {
    this.roomId = config?.roomId || ('LF'+Math.random().toString(36).substr(2,6)).toUpperCase();
    this.players = config?.players || [
      {id:'p1',name:'小明',emoji:'🧑',connected:true},
      {id:'p2',name:'小美',emoji:'👧',connected:true},
      {id:'p3',name:'家豪',emoji:'🧒',connected:true}
    ];
    this.players.forEach(function(p){ this.scores[p.id] = 0; }.bind(this));
    
    if(config?.mode === 'websocket'){
      this._connectWebSocket(config.wsUrl);
    } else if(config?.mode === 'signalr'){
      this._connectSignalR(config.signalRUrl);
    } else {
      this.mode = 'simulation';
    }
    
    return this;
  },
  
  // ── WEBSOCKET CONNECTION ──
  _connectWebSocket: function(url) {
    var self = this;
    this.ws = new WebSocket(url);
    this.ws.onopen = function(){ self.mode='websocket'; self._onConnect(); };
    this.ws.onmessage = function(e){ self._onMessage(JSON.parse(e.data)); };
    this.ws.onclose = function(){ self.mode='simulation'; };
  },
  
  // ── SIGNALR CONNECTION ──
  _connectSignalR: function(url) {
    // SignalR connection stub - requires signalr.js
    if(typeof signalR !== 'undefined'){
      var self = this;
      this.connection = new signalR.HubConnectionBuilder()
        .withUrl(url).build();
      this.connection.on('ReceiveAnswer', function(data){ self._onMessage(data); });
      this.connection.on('PlayerJoined', function(data){ self._onPlayerJoin(data); });
      this.connection.start().then(function(){ self.mode='signalr'; });
    }
  },
  
  // ── EVENT HANDLERS ──
  _onConnect: function() {
    this.ws.send(JSON.stringify({type:'join',room:this.roomId}));
  },
  
  _onMessage: function(data) {
    if(data.type === 'answer'){
      this.scores[data.playerId] = data.score;
      if(this.onScoreUpdate) this.onScoreUpdate(data);
    }
  },
  
  _onPlayerJoin: function(data) {
    var exists = this.players.find(function(p){return p.id===data.id;});
    if(!exists) this.players.push(data);
  },
  
  // ── SUBMIT ANSWER ──
  submitAnswer: function(playerId, answerIdx, correct) {
    var points = correct ? 10 + (this._streaks[playerId]||0)*2 : 0;
    this.scores[playerId] = (this.scores[playerId]||0) + points;
    if(correct){ this._streaks[playerId] = (this._streaks[playerId]||0)+1; }
    else { this._streaks[playerId] = 0; }
    
    if(this.mode === 'websocket' && this.ws?.readyState===WebSocket.OPEN){
      this.ws.send(JSON.stringify({
        type:'answer', room:this.roomId, playerId:playerId,
        score:this.scores[playerId], correct:correct
      }));
    }
    
    return {score:this.scores[playerId], streak:this._streaks[playerId]||0};
  },
  
  // ── SIMULATE (for demo/testing) ──
  simulate: function(questionBank) {
    var self = this;
    this.currentQuestion = questionBank[Math.floor(Math.random()*questionBank.length)];
    
    // Simulate players answering at different speeds
    var delays = [800, 1200, 2000]; // P1 fast, P2 medium, P3 slow
    this.players.forEach(function(p,i){
      setTimeout(function(){
        var correct = Math.random()>(0.3+i*0.15); // P1 most accurate
        self.submitAnswer(p.id, correct?self.currentQuestion.ans:((self.currentQuestion.ans+1)%4), correct);
      }, delays[i]);
    });
  },
  
  _streaks: {},
  
  // ── GET LEADERBOARD ──
  getLeaderboard: function() {
    return this.players.slice().sort(function(a,b){
      return (this.scores[b.id]||0) - (this.scores[a.id]||0);
    }.bind(this));
  }
};

if(typeof window !== 'undefined') window.LFBattle = LFBattle;
