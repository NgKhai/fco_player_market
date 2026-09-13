const { createApp } = Vue;

const FORMATION_LINES = {
  '3-1-2-1-3': [['CB', 'CB', 'CB'], ['CDM'], ['LM', 'RM'], ['CAM'], ['LW', 'ST', 'RW']],
  '3-1-4-2': [['CB', 'CB', 'CB'], ['CDM'], ['LM', 'CM', 'CM', 'RM'], ['ST', 'ST']],
  '3-2-1-2': [['CB', 'CB', 'CB'], ['CDM', 'CDM'], ['LM', 'RM'], ['CAM'], ['ST', 'ST']],
  '3-2-3-2': [['CB', 'CB', 'CB'], ['CDM', 'CDM'], ['LM', 'CAM', 'RM'], ['ST', 'ST']],
  '3-4-1-2': [['CB', 'CB', 'CB'], ['LM', 'CM', 'CM', 'RM'], ['CAM'], ['ST', 'ST']],
  '3-4-3': [['CB', 'CB', 'CB'], ['LM', 'CM', 'CM', 'RM'], ['LW', 'ST', 'RW']],
  '3-4-3F': [['CB', 'CB', 'CB'], ['LM', 'CM', 'CM', 'RM'], ['LW', 'ST', 'RW']],
  '4-1-2-1-2': [['LB', 'CB', 'CB', 'RB'], ['CDM'], ['LM', 'RM'], ['CAM'], ['ST', 'ST']],
  '4-1-2-1-2-C': [['LB', 'CB', 'CB', 'RB'], ['CDM'], ['LM', 'RM'], ['CAM'], ['ST', 'ST']],
  '4-1-2-3': [['LB', 'CB', 'CB', 'RB'], ['CDM'], ['CM', 'CM'], ['LW', 'ST', 'RW']],
  '4-1-2-3-F': [['LB', 'CB', 'CB', 'RB'], ['CDM'], ['CM', 'CM'], ['LW', 'ST', 'RW']],
  '4-1-3-2': [['LB', 'CB', 'CB', 'RB'], ['CDM'], ['LM', 'CM', 'RM'], ['ST', 'ST']],
  '4-1-4-1': [['LB', 'CB', 'CB', 'RB'], ['CDM'], ['LM', 'CM', 'CM', 'RM'], ['ST']],
  '4-2-1-3': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['CAM'], ['LW', 'ST', 'RW']],
  '4-2-1-3-A': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['CAM'], ['LW', 'ST', 'RW']],
  '4-2-1-3-D': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['CAM'], ['LW', 'ST', 'RW']],
  '4-2-2-1-1': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['LM', 'RM'], ['CAM'], ['ST']],
  '4-2-2-2': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['LM', 'RM'], ['ST', 'ST']],
  '4-2-2-2A': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['LM', 'RM'], ['ST', 'ST']],
  '4-2-3-1': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['CAM', 'CAM', 'CAM'], ['ST']],
  '4-2-4': [['LB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['LW', 'ST', 'ST', 'RW']],
  '4-3-1-2': [['LB', 'CB', 'CB', 'RB'], ['CM', 'CM', 'CM'], ['CAM'], ['ST', 'ST']],
  '4-3-2-1': [['LB', 'CB', 'CB', 'RB'], ['CM', 'CM', 'CM'], ['CAM', 'CAM'], ['ST']],
  '4-3-3': [['LB', 'CB', 'CB', 'RB'], ['CM', 'CM', 'CM'], ['LW', 'ST', 'RW']],
  '4-3-3F': [['LB', 'CB', 'CB', 'RB'], ['CM', 'CM', 'CM'], ['LW', 'ST', 'RW']],
  '4-4-1-1': [['LB', 'CB', 'CB', 'RB'], ['LM', 'CM', 'CM', 'RM'], ['CAM'], ['ST']],
  '4-4-2': [['LB', 'CB', 'CB', 'RB'], ['LM', 'CM', 'CM', 'RM'], ['ST', 'ST']],
  '4-4-2F': [['LB', 'CB', 'CB', 'RB'], ['LM', 'CM', 'CM', 'RM'], ['ST', 'ST']],
  '4-5-1': [['LB', 'CB', 'CB', 'RB'], ['LM', 'CM', 'CAM', 'CM', 'RM'], ['ST']],
  '5-1-2-1-1': [['LB', 'CB', 'CB', 'CB', 'RB'], ['CDM'], ['LM', 'RM'], ['CAM'], ['ST']],
  '5-2-1-2': [['LB', 'CB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['CAM'], ['ST', 'ST']],
  '5-2-3': [['LB', 'CB', 'CB', 'CB', 'RB'], ['CDM', 'CDM'], ['LW', 'ST', 'RW']],
  '5-3-2': [['LB', 'CB', 'CB', 'CB', 'RB'], ['CM', 'CM', 'CM'], ['ST', 'ST']],
  '5-4-1': [['LB', 'CB', 'CB', 'CB', 'RB'], ['LM', 'CM', 'CM', 'RM'], ['ST']]
};

const createFormationSlots = (lines) => [
  ['GK', 50, 88],
  ...lines.flatMap((row, line) => row.map((position, index) => {
    const width = row.length === 1 ? 0 : Math.min(76, 18 + (row.length - 1) * 18);
    const x = 50 + (index - (row.length - 1) / 2) * (width / Math.max(1, row.length - 1));
    const y = lines.length === 1 ? 40 : 72 - line * (56 / (lines.length - 1));
    return [position, x, y];
  }))
];

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
      builderSearchRequestId: 0,
      selectedSlotId: null,
      draggedSlotId: null,
      builderFormationId: '4-3-3',
      formationPickerOpen: false,
      playerPickerOpen: false,
      builderAssignments: {},
      savedSquads: [],
      activeSquadId: null,
      squadName: '',
      formationGroups: [
        { title: '3 HẬU VỆ', items: ['3-1-2-1-3', '3-1-4-2', '3-2-1-2', '3-2-3-2', '3-4-1-2', '3-4-3', '3-4-3F'] },
        { title: '4 HẬU VỆ', items: ['4-1-2-1-2', '4-1-2-1-2-C', '4-1-2-3', '4-1-2-3-F', '4-1-3-2', '4-1-4-1', '4-2-1-3', '4-2-1-3-A', '4-2-1-3-D', '4-2-2-1-1', '4-2-2-2', '4-2-2-2A', '4-2-3-1', '4-2-4', '4-3-1-2', '4-3-2-1', '4-3-3', '4-3-3F', '4-4-1-1', '4-4-2', '4-4-2F', '4-5-1'] },
        { title: '5 HẬU VỆ', items: ['5-1-2-1-1', '5-2-1-2', '5-2-3', '5-3-2', '5-4-1'] }
      ],
      formations: Object.fromEntries(Object.entries(FORMATION_LINES).map(([id, lines]) => [id, createFormationSlots(lines)])),
      loading: false,
      playerRequestError: '',
      selectedPlayerDetail: null,
      modalData: {},
      playerDetailError: '',
      showTokenModal: false,
      authTab: 'login',
      loginUsername: '',
      loginPassword: '',
      loginLoading: false,
      authMessage: '',
      authMessageType: '',
      seasonImageErrors: {},
      garenaConnected: false,
      garenaTokenInput: '',
      garenaUidInput: '',
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
        const hasPositionData = list.some(p => this.getPlayerPositions(p).length);
        if (hasPositionData) list = list.filter(p => this.getPlayerPositions(p).includes(this.selectedPosition));
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
        position: slot[0], x: slot[1], y: slot[0] === 'GK' ? 78 : slot[2]
      }));
    },
    builderPlayers() {
      const q = this.builderSearch.trim().toLowerCase();
      const position = this.builderSlots.find(s => s.id === this.selectedSlotId)?.position;
      const candidates = this.builderResults.length ? this.builderResults : this.players;
      const hasPositionData = candidates.some(p => this.getPlayerPositions(p).length);
      return candidates
        .filter(p => !q || (p.name || '').toLowerCase().includes(q) || String(p.spid || p.id || '').includes(q))
        .filter(p => !position || !hasPositionData || this.getPlayerPositions(p).includes(position))
        .filter((p, i, list) => list.findIndex(x => String(x.uid || x.spid || x.id) === String(p.uid || p.spid || p.id)) === i)
        .slice(0, 30);
    },
    builderSquadPlayers() {
      return Object.values(this.builderAssignments).filter(Boolean);
    },
    builderAverageOvr() {
      const list = this.builderSlots.map(slot => ({ slot, player: this.getBuilderPlayer(slot.id) })).filter(x => x.player);
      return list.length ? Math.round(list.reduce((sum, x) => sum + this.getBuilderOvr(x.player, x.slot.position), 0) / list.length) : 0;
    },
    builderTotalSalary() {
      return this.builderSquadPlayers.reduce((sum, p) => sum + Number(p.attrA || p.salary || 0), 0);
    },
    builderSalaryExceeded() {
      return this.builderTotalSalary > 305;
    },
    builderPositionWarnings() {
      return this.builderSlots.filter(s => {
        const p = this.builderAssignments[s.id];
        return p && !this.getPlayerPositions(p).includes(s.position);
      }).length;
    }
  },
  mounted() {
    this.checkGarenaStatus();
    this.loadSavedSquad();
    this.fetchPlayersBySeason('icontm');
  },
  methods: {
    getPlayerPositions(player) {
      return [player?.pos1, player?.pos2, player?.pos]
        .filter(Boolean)
        .map(pos => String(pos).toUpperCase());
    },
    getBuilderOvr(player, position) {
      if (!player) return 0;
      if (String(player.pos1 || player.pos).toUpperCase() === position) return Number(player.pos1val || player.attrB || 0);
      if (String(player.pos2 || '').toUpperCase() === position) return Number(player.pos2val || player.pos1val || player.attrB || 0);
      return Number(player.pos1val || player.attrB || player.ovr || 0);
    },
    formationFor(id) {
      return this.formations[id] || this.formations['4-3-3'];
    },
    async checkGarenaStatus() {
      try {
        const res = await fetch('/api/garena/status');
        const json = await res.json();
        if (json.status === 'success') {
          this.garenaConnected = json.connected;
          this.garenaUidInput = json.uid || '';
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
        this.garenaUidInput = '';
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
            body: JSON.stringify({ token: this.garenaTokenInput.trim(), uid: this.garenaUidInput.trim() })
        });
        const json = await res.json();
        if (json.status === 'success') {
          this.garenaConnected = true;
          this.authMessage = '';
          this.showTokenModal = false;
          alert('✅ Đã lưu token Garena VN thành công!');
        } else {
          this.authMessage = json.message || 'Token Garena không hợp lệ.';
          this.authMessageType = 'error';
        }
      } catch (err) {
        alert('Lỗi kết nối: ' + err.message);
      }
    },
    async fetchPlayersBySeason(seasonCode) {
      this.loading = true;
      this.playerRequestError = '';
      this.selectedSeason = seasonCode;
      this.searchQuery = '';
      try {
        const res = await fetch(`/api/players/search?season=${encodeURIComponent(seasonCode)}`);
        const json = await res.json();
        if (!res.ok || json.status !== 'success') throw new Error(json.message || 'request failed');
        this.players = json.data || [];
        this.builderResults = this.players;
      } catch (err) {
        console.error('Fetch error:', err);
        this.playerRequestError = 'Không thể tải dữ liệu cầu thủ.';
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
    async searchBuilderPlayers() {
      const q = this.builderSearch.trim();
      const requestId = ++this.builderSearchRequestId;
      if (q.length < 2) {
        this.builderResults = this.players;
        return;
      }
      try {
        const res = await fetch(`/api/players/search?q=${encodeURIComponent(q)}`);
        const json = await res.json();
        if (requestId === this.builderSearchRequestId && json.status === 'success') {
          this.builderResults = json.data || [];
        }
      } catch (err) {
        if (requestId === this.builderSearchRequestId) console.error('Builder search error:', err);
      }
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
      const used = new Set();
      this.builderSlots.forEach(slot => {
        const index = old.findIndex((player, i) => !used.has(i) && this.getPlayerPositions(player).includes(slot.position));
        if (index >= 0) {
          this.builderAssignments[slot.id] = old[index];
          used.add(index);
        }
      });
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
      const name = this.squadName.trim() || `Đội hình ${this.savedSquads.length + 1}`;
      const squad = {
        id: this.activeSquadId || `squad-${Date.now()}`,
        name,
        formation: this.builderFormationId,
        assignments: this.builderAssignments
      };
      const index = this.savedSquads.findIndex((saved) => saved.id === squad.id);
      this.savedSquads = index >= 0
        ? this.savedSquads.map((saved, savedIndex) => savedIndex === index ? squad : saved)
        : [...this.savedSquads, squad];
      this.activeSquadId = squad.id;
      this.squadName = squad.name;
      localStorage.setItem('fco-squads', JSON.stringify({ version: 1, activeId: squad.id, squads: this.savedSquads }));
      localStorage.setItem('fco-squad', JSON.stringify({ formation: squad.formation, assignments: squad.assignments }));
    },
    saveNewSquad() {
      this.activeSquadId = null;
      this.persistSquad();
    },
    isValidFormation(id) {
      return Object.prototype.hasOwnProperty.call(this.formations, id);
    },
    restoreSquad(saved) {
      const formation = this.isValidFormation(saved.formation) ? saved.formation : '4-3-3';
      const source = saved.assignments && typeof saved.assignments === 'object' ? saved.assignments : {};
      const restored = {};
      const used = new Set();
      const playerKey = (player) => String(player.uid || player.spid || player.id);

      this.builderFormationId = formation;
      this.builderAssignments = {};
      this.builderSlots.forEach((slot) => {
        const player = source[slot.id];
        if (player) {
          restored[slot.id] = player;
          used.add(playerKey(player));
        }
      });
      this.builderSlots.forEach((slot) => {
        if (restored[slot.id]) return;
        const entry = Object.values(source).find((player) => player && !used.has(playerKey(player)) && this.getPlayerPositions(player).includes(slot.position));
        if (entry) {
          restored[slot.id] = entry;
          used.add(playerKey(entry));
        }
      });
      this.builderAssignments = restored;
    },
    loadSavedSquad() {
      try {
        const collection = JSON.parse(localStorage.getItem('fco-squads') || 'null');
        const squads = Array.isArray(collection) ? collection : collection?.squads;
        if (Array.isArray(squads) && squads.length) {
          this.savedSquads = squads.filter((squad) => squad && squad.id && squad.name);
          const saved = this.savedSquads.find((squad) => squad.id === collection.activeId) || this.savedSquads[0];
          this.activeSquadId = saved.id;
          this.squadName = saved.name;
          this.restoreSquad(saved);
          return;
        }

        const saved = JSON.parse(localStorage.getItem('fco-squad') || 'null');
        if (saved) this.restoreSquad(saved);
      } catch (_) {
        this.savedSquads = [];
        this.activeSquadId = null;
        this.squadName = '';
      }
    },
    selectSavedSquad(id) {
      const saved = this.savedSquads.find((squad) => squad.id === id);
      if (!saved) return;
      this.activeSquadId = saved.id;
      this.squadName = saved.name;
      this.restoreSquad(saved);
      this.persistSquad();
    },
    deleteSavedSquad() {
      const index = this.savedSquads.findIndex((squad) => squad.id === this.activeSquadId);
      if (index < 0) return;
      this.savedSquads.splice(index, 1);
      if (this.savedSquads.length) {
        this.selectSavedSquad(this.savedSquads[Math.min(index, this.savedSquads.length - 1)].id);
      } else {
        this.activeSquadId = null;
        this.squadName = '';
        this.builderFormationId = '4-3-3';
        this.builderAssignments = {};
        localStorage.removeItem('fco-squads');
        localStorage.removeItem('fco-squad');
      }
    },
    clearBuilder() {
      this.builderAssignments = {};
      this.selectedSlotId = null;
      if (this.activeSquadId) this.persistSquad();
      else localStorage.removeItem('fco-squad');
    },
    async handleSearch() {
      const q = this.searchQuery.trim();
      if (!q) {
        this.fetchPlayersBySeason(this.selectedSeason || 'icontm');
        return;
      }
      this.loading = true;
      this.playerRequestError = '';
      this.selectedSeason = '';
      try {
        const res = await fetch(`/api/players/search?q=${encodeURIComponent(q)}`);
        const json = await res.json();
        if (!res.ok || json.status !== 'success') throw new Error(json.message || 'request failed');
        this.players = json.data || [];
      } catch (err) {
        console.error('Search error:', err);
        this.playerRequestError = 'Không thể tải dữ liệu cầu thủ.';
      } finally {
        this.loading = false;
      }
    },
    retryPlayerRequest() {
      return this.searchQuery.trim() ? this.handleSearch() : this.fetchPlayersBySeason(this.selectedSeason || 'icontm');
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
      this.playerDetailError = '';
      this.modalData = { db: player, price: {}, traits: {} };
      
      try {
        const spidParam = player.id || player.spid || '';
        const query = new URLSearchParams({ uid: player.uid || '' });
        if (/^\d+$/.test(String(spidParam))) query.set('spid', String(spidParam));
        const res = await fetch(`/api/players/detail?${query.toString()}`);
        const json = await res.json();
        if (!res.ok || json.status !== 'success' || !json.data) {
          this.playerDetailError = json.message || 'Không tìm thấy cầu thủ.';
          return;
        }
        this.modalData = json.data;
      } catch (err) {
        console.error('Detail fetch error:', err);
        this.playerDetailError = 'Không thể tải thông tin cầu thủ.';
      }
    },
    getMinifaceUrl(player) {
      if (!player) return '';
      const identifier = player.spid || player.id;
      if (identifier && /^\d+$/.test(String(identifier))) {
        return `/minifaces/action/p${identifier}.png`;
      }
      if (player.source_uid || player.uid) {
        return `/minifaces/fifaaddict/${encodeURIComponent(player.source_uid || player.uid)}.png`;
      }
      return '';
    },
    getSeasonImageUrl(player) {
      const seasonId = Number(player && player.season_id);
      const key = String(seasonId);
      return seasonId > 0 && !this.seasonImageErrors[key] ? `/seasons/season_${seasonId}.png` : '';
    },
    markSeasonImageError(player) {
      const seasonId = Number(player && player.season_id);
      if (seasonId > 0) this.seasonImageErrors[String(seasonId)] = true;
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
