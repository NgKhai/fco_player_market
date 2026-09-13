describe('Squad Builder', () => {
  beforeEach(() => {
    cy.visit('/?builder=1');
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
});
