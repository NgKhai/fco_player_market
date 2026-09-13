describe('Squad Builder', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/players/search*', (req) => {
      const data = req.query.q ? [
        { id: 1002, spid: 1002, uid: '2', name: 'Striker Test', season_full: 'ICON', pos: 'ST', pos1: 'ST', attrA: 10, attrB: 95, foot_left: 4, foot_right: 5, season_id: 100 },
        { id: 2002, spid: 2002, uid: '20', name: 'Striker Test', season_full: '24 TOTY', pos: 'ST', pos1: 'ST', attrA: 11, attrB: 96, foot_left: 4, foot_right: 5, season_id: 200 }
      ] : [
        { id: 1001, spid: 1001, uid: '1', name: 'Goalkeeper Test', pos: 'GK', pos1: 'GK', attrA: 8, attrB: 90, foot_left: 2, foot_right: 5, season_id: 100 },
        { id: 1002, spid: 1002, uid: '2', name: 'Striker Test', season_full: 'ICON', pos: 'ST', pos1: 'ST', attrA: 10, attrB: 95, foot_left: 4, foot_right: 5, season_id: 100 }
      ];
      req.reply({ statusCode: 200, body: { status: 'success', total: data.length, data } });
    }).as('playerSearch');
    cy.visit('/?builder=1');
    cy.wait('@playerSearch');
  });

  it('opens the formation picker', () => {
    cy.contains('button', 'FORMATIONS').click();
    cy.contains('button', '4-4-2').should('be.visible');
    cy.get('.formation-backdrop').should('have.css', 'background-color', 'rgba(0, 0, 0, 0.72)');
  });

  it('renders the explicit positions for 4-1-2-1-2', () => {
    cy.contains('button', 'FORMATIONS').click();
    cy.contains('button.formation-option', '4-1-2-1-2').click();
    cy.get('.builder-empty span').then(($positions) => {
      expect([...$positions].map((position) => position.textContent.trim())).to.deep.equal([
        'GK', 'LB', 'CB', 'CB', 'RB', 'CDM', 'LM', 'RM', 'CAM', 'ST', 'ST'
      ]);
    });
  });

  it('suggests only goalkeepers for the GK slot', () => {
    cy.get('button.builder-empty').first().click();
    cy.contains('h2', 'CHỌN CẦU THỦ · GK').should('be.visible');
    cy.get('.player-picker button').each(($button, index) => {
      if (index > 0) cy.wrap($button).should('contain.text', 'GK');
    });
  });

  it('shows all card seasons for a player in the picker search', () => {
    cy.get('button.builder-empty').eq(9).click();
    cy.get('.player-picker input').type('Striker Test');
    cy.wait('@playerSearch');
    cy.get('.player-picker').should('contain.text', 'ICON').and('contain.text', '24 TOTY');
  });

  it('persists the selected squad locally', () => {
    cy.get('button.builder-empty').first().click();
    cy.get('.player-picker button').eq(1).click();
    cy.reload();
    cy.get('.builder-player-card').should('have.length', 1);
  });

  it('restores every picker formation after reload', () => {
    cy.contains('button', 'FORMATIONS').click();
    cy.contains('button.formation-option', '4-1-2-1-2').click();
    cy.get('button.builder-empty').first().click();
    cy.get('.player-picker button').eq(1).click();
    cy.reload();
    cy.contains('button', 'FORMATIONS 4-1-2-1-2').should('be.visible');
    cy.get('button.builder-empty').should('have.length', 10);
    cy.get('.builder-player-card').should('have.length', 1);
  });

  it('saves, selects, and deletes named squads locally', () => {
    cy.get('input[aria-label="Tên squad"]').type('GK Squad');
    cy.contains('button', 'Lưu đội hình').click();
    cy.get('input[aria-label="Tên squad"]').clear().type('Second Squad');
    cy.contains('button', 'Lưu squad mới').click();
    cy.get('select[aria-label="Chọn squad"] option').should('have.length', 2);
    cy.get('select[aria-label="Chọn squad"]').select('GK Squad');
    cy.get('input[aria-label="Tên squad"]').should('have.value', 'GK Squad');
    cy.get('button[aria-label="Xóa squad"]').click();
    cy.get('select[aria-label="Chọn squad"] option').should('have.length', 1);
    cy.get('select[aria-label="Chọn squad"]').should('contain', 'Second Squad');
  });

  it('shows the player weak foot from the API and the salary cap', () => {
    cy.contains('.fco-card', 'Goalkeeper Test').should('contain.text', '2-5');
    cy.get('button.builder-empty').first().click();
    cy.get('.player-picker button').eq(1).click();
    cy.contains('Lương').should('contain.text', '/ 305');
  });

  it('uses the local season image when available', () => {
    cy.get('img[src="/seasons/season_100.png"]').should('be.visible');
  });

  it('keeps the goalkeeper slot above the squad summary on mobile', () => {
    cy.viewport(375, 667);
    cy.get('button.builder-empty').first().then(($gk) => {
      cy.get('.builder-summary').then(($summary) => {
        expect($gk[0].getBoundingClientRect().bottom).to.be.lessThan($summary[0].getBoundingClientRect().top);
      });
    });
  });
});
