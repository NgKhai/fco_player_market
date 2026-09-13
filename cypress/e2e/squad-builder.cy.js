describe('Squad Builder', () => {
  beforeEach(() => {
    cy.intercept('GET', '**/api/players/search*', {
      statusCode: 200,
      body: {
        status: 'success',
        total: 2,
        data: [
          { id: 1001, spid: 1001, uid: '1', name: 'Goalkeeper Test', pos: 'GK', pos1: 'GK', attrA: 8, attrB: 90 },
          { id: 1002, spid: 1002, uid: '2', name: 'Striker Test', pos: 'ST', pos1: 'ST', attrA: 10, attrB: 95 }
        ]
      }
    }).as('playerSearch');
    cy.visit('/?builder=1');
    cy.wait('@playerSearch');
  });

  it('opens the formation picker', () => {
    cy.contains('button', 'FORMATIONS').click();
    cy.contains('button', '4-4-2').should('be.visible');
  });

  it('suggests only goalkeepers for the GK slot', () => {
    cy.get('button.builder-empty').first().click();
    cy.contains('h2', 'CHỌN CẦU THỦ · GK').should('be.visible');
    cy.get('.player-picker button').each(($button, index) => {
      if (index > 0) cy.wrap($button).should('contain.text', 'GK');
    });
  });

  it('persists the selected squad locally', () => {
    cy.get('button.builder-empty').first().click();
    cy.get('.player-picker button').eq(1).click();
    cy.reload();
    cy.get('.builder-player-card').should('have.length', 1);
  });
});
