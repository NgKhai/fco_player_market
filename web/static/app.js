const { createApp } = Vue;

createApp({
  data() {
    return {
      searchQuery: '',
      selectedSeason: 'icontm',
      selectedPosition: 'ALL',
      sortBy: 'ovr_desc',
      players: [],
      builderResults: [],
      builderSearch: '',
      selectedSlotId: null,
      draggedSlotId: null,
      builderFormationId: '4-3-3',
      formationPickerOpen: false,
      playerPickerOpen: false,
      builderAssignments: {},
      formationGroups: [
        { title: '3 HẬU VỆ', items: ['3-1-2-1-3', '3-1-4-2', '3-2-1-2', '3-2-3-2', '3-4-1-2', '3-4-3', '3-4-3F'] },
        { title: '4 HẬU VỆ', items: ['4-1-2-1-2', '4-1-2-1-2-C', '4-1-2-3', '4-1-2-3-F', '4-1-3-2', '4-1-4-1', '4-2-1-3', '4-2-1-3-A', '4-2-1-3-D', '4-2-2-1-1', '4-2-2-2', '4-2-2-2A', '4-2-3-1', '4-2-4', '4-3-1-2', '4-3-2-1', '4-3-3', '4-3-3F', '4-4-1-1', '4-4-2', '4-4-2F', '4-5-1'] },
        { title: '5 HẬU VỆ', items: ['5-1-2-1-1', '5-2-1-2', '5-2-3', '5-3-2', '5-4-1'] }
      ],
      formations: {
        '4-3-3': [
          ['GK', 50, 88], ['LB', 12, 70], ['CB', 34, 73], ['CB', 66, 73], ['RB', 88, 70],
          ['CM', 25, 48], ['CM', 50, 51], ['CM', 75, 48], ['LW', 25, 24], ['ST', 50, 17], ['RW', 75, 24]
        ],
        '4-2-3-1': [
          ['GK', 50, 88], ['LB', 12, 70], ['CB', 34, 73], ['CB', 66, 73], ['RB', 88, 70],
          ['CDM', 25, 52], ['CDM', 75, 52], ['CAM', 27, 30], ['CAM', 50, 40], ['CAM', 73, 30], ['ST', 50, 17]
        ],
        '4-4-2': [
          ['GK', 50, 88], ['LB', 12, 70], ['CB', 34, 73], ['CB', 66, 73], ['RB', 88, 70],
          ['LM', 15, 45], ['CM', 38, 49], ['CM', 62, 49], ['RM', 85, 45], ['ST', 38, 20], ['ST', 62, 20]
        ],
        '3-5-2': [
          ['GK', 50, 88], ['CB', 25, 72], ['CB', 50, 75], ['CB', 75, 72], ['CDM', 35, 52], ['CDM', 65, 52],
          ['LM', 12, 35], ['CAM', 50, 38], ['RM', 88, 35], ['ST', 38, 17], ['ST', 62, 17]
        ],
        '5-3-2': [
          ['GK', 50, 88], ['LB', 10, 70], ['CB', 30, 73], ['CB', 50, 75], ['CB', 70, 73], ['RB', 90, 70],
          ['CM', 25, 48], ['CM', 50, 51], ['CM', 75, 48], ['ST', 38, 18], ['ST', 62, 18]
        ]
      },
      loading: false,
      selectedPlayerDetail: null,
      modalData: {},
      showTokenModal: false,
      authTab: 'login',
      loginUsername: '',
      loginPassword: '',
      loginLoading: false,
      authMessage: '',
      authMessageType: '',
      garenaConnected: false,
      garenaTokenInput: '',
      popularSeasons: [
        { name: 'ICON The Moment', code: 'icontm' },
        { name: 'Eternal Legends (EL)', code: 'el' },
        { name: '26 TOTS', code: '26ts' },
        { name: 'World Legend (WG)', code: 'wg' },
        { name: '24 TOTY', code: '24toty' },
        { name: 'ICON', code: 'icon' },
        { name: 'Home Grown (HG)', code: 'hg' },
        { name: 'Legendary Numbers (LN)', code: 'ln' },
        { name: 'Back to Back (BTB)', code: 'btb' },
        { name: 'Captain (CAP)', code: 'cap' },
        { name: 'European Best Stars', code: 'ebs' },
        { name: 'Multi-League Champ', code: 'mc' },
        { name: 'Loyal Heroes (LH)', code: 'lh' },
        { name: 'Heroes of the Team', code: 'hot' }
      ],
      positionsList: ['ALL', 'ST', 'CF', 'LW', 'RW', 'CAM', 'CM', 'CDM', 'CB', 'LB', 'RB', 'GK']
    };
  },
  computed: {
    filteredPlayers() {
      let list = [...this.players];

      if (this.selectedPosition !== 'ALL') {
        list = list.filter(p => {
          const pos = (p.pos1 || p.pos || '').toUpperCase();
          const pos2 = (p.pos2 || '').toUpperCase();
          return pos === this.selectedPosition || pos2 === this.selectedPosition;
        });
      }

      list.sort((a, b) => {
        const ovrA = parseInt(a.pos1val || a.attrB || 0);
        const ovrB = parseInt(b.pos1val || b.attrB || 0);
        const salaryA = parseInt(a.attrA || a.salary || 0);
        const salaryB = parseInt(b.attrA || b.salary || 0);
        const nameA = (a.name || '').toLowerCase();
        const nameB = (b.name || '').toLowerCase();

        if (this.sortBy === 'ovr_desc') return ovrB - ovrA;
        if (this.sortBy === 'salary_asc') return salaryA - salaryB;
        if (this.sortBy === 'salary_desc') return salaryB - salaryA;
        if (this.sortBy === 'name_asc') return nameA.localeCompare(nameB);
        return 0;
      });

      return list;
    },
    builderSlots() {
      return this.formationFor(this.builderFormationId).map((slot, index) => ({
        id: `${this.builderFormationId}-${index}`,
        position: slot[0], x: slot[1], y: slot[2]
      }));
    },
    builderPlayers() {
      const q = this.builderSearch.trim().toLowerCase();
      const position = this.builderSlots.find(s => s.id === this.selectedSlotId)?.position;
      return (this.builderResults.length ? this.builderResults : this.players)
        .filter(p => !q || (p.name || '').toLowerCase().includes(q) || String(p.spid || p.id || '').includes(q))
        .filter(p => !position || [p.pos1, p.pos2, p.pos].some(pos => String(pos || '').toUpperCase() === position))
        .filter((p, i, list) => list.findIndex(x => String(x.uid || x.spid || x.id) === String(p.uid || p.spid || p.id)) === i)
        .slice(0, 30);
    },
    builderSquadPlayers() {
      return Object.values(this.builderAssignments).filter(Boolean);
    },
    builderAverageOvr() {
      const list = this.builderSquadPlayers;
      return list.length ? Math.round(list.reduce((sum, p) => sum + Number(p.pos1val || p.attrB || p.ovr || 0), 0) / list.length) : 0;
    },
    builderTotalSalary() {
      return this.builderSquadPlayers.reduce((sum, p) => sum + Number(p.attrA || p.salary || 0), 0);
    },
    builderPositionWarnings() {
      return this.builderSlots.filter(s => {
        const p = this.builderAssignments[s.id];
        return p && s.position !== (p.pos1 || p.pos) && s.position !== p.pos2;
      }).length;
    }
  },
  mounted() {
    this.checkGarenaStatus();
    this.loadSavedSquad();
    this.fetchPlayersBySeason('icontm');
  },
  methods: {
    formationFor(id) {
      if (this.formations[id]) return this.formations[id];
      const parts = id.replace(/[A-Z]+$/, '').replace(/-$/, '').split('-').map(Number);
      if (parts.some(Number.isNaN) || parts.length < 2) return this.formations['4-3-3'];
      const positions = (count, line, last) => {
        if (line === 0) return count === 3 ? ['CB', 'CB', 'CB'] : count === 5 ? ['LB', 'CB', 'CB', 'CB', 'RB'] : ['LB', 'CB', 'CB', 'RB'];
        if (last) return count === 1 ? ['ST'] : count === 2 ? ['ST', 'ST'] : count === 3 ? ['LW', 'ST', 'RW'] : ['LW', 'CF', 'CF', 'RW'];
        if (count === 1) return ['CAM'];
        if (count === 2) return ['CDM', 'CDM'];
        if (count === 3) return ['LM', 'CM', 'RM'];
        return count === 5 ? ['LM', 'CM', 'CAM', 'CM', 'RM'] : ['LM', 'CM', 'CM', 'RM'];
      };
      const slots = [['GK', 50, 88]];
      const rows = parts.slice(0, -1);
      rows.forEach((count, line) => {
        const row = positions(count, line, false);
        const y = 72 - line * (40 / Math.max(1, rows.length - 1));
        const spread = Math.min(80, 20 * (row.length - 1));
        row.forEach((position, index) => slots.push([position, 50 + (index - (row.length - 1) / 2) * (spread / Math.max(1, row.length - 1)), y]));
      });
      const attack = positions(parts[parts.length - 1], parts.length - 1, true);
      attack.forEach((position, index) => slots.push([position, 50 + (index - (attack.length - 1) / 2) * (80 / Math.max(1, attack.length - 1)), 16]));
      return slots;
    },
    async checkGarenaStatus() {
      try {
        const res = await fetch('/api/garena/status');
        const json = await res.json();
        if (json.status === 'success') {
          this.garenaConnected = json.connected;
        }
      } catch (err) {
        console.error('Garena status error:', err);
      }
    },
    async handleAutoLogin() {
      if (!this.loginUsername.trim() || !this.loginPassword.trim()) {
        this.authMessage = 'Vui lòng nhập tài khoản và mật khẩu Garena!';
        this.authMessageType = 'error';
        return;
      }
      this.loginLoading = true;
      this.authMessage = '';
      try {
        const res = await fetch('/api/garena/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.loginUsername.trim(),
            password: this.loginPassword.trim()
          })
        });
        const json = await res.json();
        if (json.status === 'success') {
          this.garenaConnected = true;
          this.authMessage = '✅ ' + json.message;
          this.authMessageType = 'success';
          setTimeout(() => {
            this.showTokenModal = false;
            this.authMessage = '';
          }, 1200);
        } else {
          this.authMessage = '❌ ' + json.message;
          this.authMessageType = 'error';
        }
      } catch (err) {
        this.authMessage = 'Lỗi kết nối: ' + err.message;
        this.authMessageType = 'error';
      } finally {
        this.loginLoading = false;
      }
    },
    async handleLogout() {
      try {
        await fetch('/api/garena/logout', { method: 'POST' });
        this.garenaConnected = false;
        this.loginUsername = '';
        this.loginPassword = '';
        this.authMessage = 'Đã đăng xuất tài khoản Garena.';
        this.authMessageType = 'success';
        setTimeout(() => {
          this.showTokenModal = false;
          this.authMessage = '';
        }, 1000);
      } catch (err) {
        console.error(err);
      }
    },
    async saveGarenaToken() {
      if (!this.garenaTokenInput.trim()) {
        alert('Vui lòng nhập Token Garena!');
        return;
      }
      try {
        const res = await fetch('/api/garena/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: this.garenaTokenInput.trim() })
        });
        const json = await res.json();
        if (json.status === 'success') {
          this.garenaConnected = true;
          this.showTokenModal = false;
          alert('✅ Đã lưu token Garena VN thành công!');
        }
      } catch (err) {
        alert('Lỗi kết nối: ' + err.message);
      }
    },
    async fetchPlayersBySeason(seasonCode) {
      this.loading = true;
      this.selectedSeason = seasonCode;
      this.searchQuery = '';
      try {
        const res = await fetch(`/api/players/search?season=${encodeURIComponent(seasonCode)}`);
        const json = await res.json();
        if (json.status === 'success') {
          this.players = json.data || [];
          this.builderResults = this.players;
        }
      } catch (err) {
        console.error('Fetch error:', err);
      } finally {
        this.loading = false;
      }
    },
    getBuilderPlayer(slotId) {
      return this.builderAssignments[slotId] || null;
    },
    selectBuilderSlot(slot) {
      this.selectedSlotId = slot.id;
      this.builderSearch = '';
      this.playerPickerOpen = true;
    },
    addBuilderPlayer(player) {
      if (!this.selectedSlotId) return;
      const oldSlot = Object.keys(this.builderAssignments).find(id => {
        const p = this.builderAssignments[id];
        return p && String(p.uid || p.spid || p.id) === String(player.uid || player.spid || player.id);
      });
      if (oldSlot && oldSlot !== this.selectedSlotId) delete this.builderAssignments[oldSlot];
      this.builderAssignments[this.selectedSlotId] = player;
      const next = this.builderSlots.find(s => !this.builderAssignments[s.id]);
      this.selectedSlotId = next ? next.id : null;
      this.playerPickerOpen = false;
      this.persistSquad();
    },
    removeBuilderPlayer(slotId) {
      delete this.builderAssignments[slotId];
      this.selectedSlotId = slotId;
      this.playerPickerOpen = false;
      this.persistSquad();
    },
    changeBuilderFormation(id) {
      const old = Object.values(this.builderAssignments).filter(Boolean);
      this.builderFormationId = id;
      this.builderAssignments = {};
      this.builderSlots.forEach((slot, index) => { if (old[index]) this.builderAssignments[slot.id] = old[index]; });
      this.selectedSlotId = null;
      this.persistSquad();
    },
    dragBuilderStart(slotId) { this.draggedSlotId = slotId; },
    dropBuilderSlot(targetId) {
      if (!this.draggedSlotId || this.draggedSlotId === targetId) return;
      const from = this.builderAssignments[this.draggedSlotId];
      const to = this.builderAssignments[targetId];
      if (from) this.builderAssignments[targetId] = from; else delete this.builderAssignments[targetId];
      if (to) this.builderAssignments[this.draggedSlotId] = to; else delete this.builderAssignments[this.draggedSlotId];
      this.draggedSlotId = null;
      this.persistSquad();
    },
    persistSquad() {
      localStorage.setItem('fco-squad', JSON.stringify({
        formation: this.builderFormationId,
        assignments: this.builderAssignments,
      }));
    },
    loadSavedSquad() {
      try {
        const saved = JSON.parse(localStorage.getItem('fco-squad') || 'null');
        if (!saved || !this.formations[saved.formation] || !saved.assignments) return;
        this.builderFormationId = saved.formation;
        this.builderAssignments = saved.assignments;
      } catch (_) {
        localStorage.removeItem('fco-squad');
      }
    },
    clearBuilder() {
      this.builderAssignments = {};
      this.selectedSlotId = null;
      localStorage.removeItem('fco-squad');
    },
    async handleSearch() {
      const q = this.searchQuery.trim();
      if (!q) {
        this.fetchPlayersBySeason(this.selectedSeason || 'icontm');
        return;
      }
      this.loading = true;
      this.selectedSeason = '';
      try {
        const res = await fetch(`/api/players/search?q=${encodeURIComponent(q)}`);
        const json = await res.json();
        if (json.status === 'success') {
          this.players = json.data || [];
        }
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        this.loading = false;
      }
    },
    selectSeason(code) {
      this.fetchPlayersBySeason(code);
    },
    resetToHome() {
      this.searchQuery = '';
      this.selectedPosition = 'ALL';
      this.fetchPlayersBySeason('icontm');
    },
    async openPlayerDetail(player) {
      this.selectedPlayerDetail = player;
      this.modalData = { db: player, price: {}, traits: {} };
      
      try {
        const spidParam = player.id || player.spid || '';
        const res = await fetch(`/api/players/detail?uid=${encodeURIComponent(player.uid)}&spid=${encodeURIComponent(spidParam)}`);
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          this.modalData = json.data;
        }
      } catch (err) {
        console.error('Detail fetch error:', err);
      }
    },
    getMinifaceUrl(player) {
      if (!player) return '';
      if (player.id || player.spid) {
        return `/minifaces/action/p${player.spid || player.id}.png`;
      }
      return '';
    },
    handleImageError(e) {
      e.target.style.visibility = 'hidden';
    },
    getPositionBadgeColor(pos) {
      pos = (pos || '').toUpperCase();
      if (['ST', 'CF', 'LW', 'RW'].includes(pos)) return 'bg-rose-500/20 text-rose-400 border border-rose-500/40';
      if (['CAM', 'CM', 'CDM', 'LM', 'RM'].includes(pos)) return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
      if (['CB', 'LB', 'RB', 'LWB', 'RWB', 'SW'].includes(pos)) return 'bg-sky-500/20 text-sky-400 border border-sky-500/40';
      if (['GK'].includes(pos)) return 'bg-amber-500/20 text-amber-400 border border-amber-500/40';
      return 'bg-slate-700 text-slate-300';
    },
    getGradeColorClass(lvl) {
      if (lvl === 1) return 'bg-[#181d2a] border-slate-700 text-slate-300';
      if (lvl <= 4) return 'bg-[#1e1b18] border-amber-700/60 text-amber-300';
      if (lvl <= 7) return 'bg-[#181e28] border-sky-500/60 text-sky-300 shadow-sm shadow-sky-500/10';
      if (lvl <= 9) return 'bg-[#241a2c] border-purple-500/60 text-purple-300 shadow-md shadow-purple-500/20';
      return 'bg-gradient-to-b from-amber-600/30 to-amber-900/40 border-amber-400 text-amber-300 shadow-lg shadow-amber-500/30';
    },
    getGradeBadgeClass(lvl) {
      if (lvl === 1) return 'bg-slate-700 text-white';
      if (lvl <= 4) return 'bg-amber-700 text-amber-100';
      if (lvl <= 7) return 'bg-sky-600 text-white';
      if (lvl <= 9) return 'bg-purple-600 text-white';
      return 'bg-amber-400 text-black font-black';
    },
    getCoreAttributes(data) {
      const db = data.db || {};
      const attrg = db.attrgroup || {};
      if (attrg.labels && attrg.data && attrg.labels.length === attrg.data.length) {
        const result = {};
        for (let i = 0; i < attrg.labels.length; i++) {
          result[attrg.labels[i]] = parseInt(attrg.data[i]) || 100;
        }
        return result;
      }
      return {
        'Tốc độ': parseInt(db.pos1val || 120) + 5,
        'Sút': parseInt(db.pos1val || 120) + 4,
        'Chuyền': parseInt(db.pos1val || 120) - 2,
        'Rê bóng': parseInt(db.pos1val || 120) + 3,
        'Phòng thủ': 60,
        'Thể lực': parseInt(db.pos1val || 120) - 5
      };
    },
    getStatColorClass(val) {
      if (val >= 130) return 'text-purple-400';
      if (val >= 120) return 'text-rose-400';
      if (val >= 110) return 'text-amber-400';
      if (val >= 90) return 'text-emerald-400';
      return 'text-slate-300';
    },
    getStatBarColor(val) {
      if (val >= 130) return 'bg-purple-500 shadow-sm shadow-purple-500/50';
      if (val >= 120) return 'bg-rose-500 shadow-sm shadow-rose-500/50';
      if (val >= 110) return 'bg-amber-400 shadow-sm shadow-amber-400/50';
      if (val >= 90) return 'bg-emerald-400 shadow-sm shadow-emerald-400/50';
      return 'bg-slate-600';
    }
  }
}).mount('#app');
