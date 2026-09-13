describe('FC Online web critical flows', () => {
  beforeEach(() => {
    cy.visit('/?builder=1');
  });

  it('loads the player database', () => {
    cy.contains('Danh sách cầu thủ mùa').should('be.visible');
    cy.get('.fco-card').should('have.length.greaterThan', 0);
  });

  it('searches players by name', () => {
    cy.get('input[placeholder^="Nhập tên cầu thủ"]').type('Pelé');
    cy.get('form').first().submit();
    cy.contains('Kết quả tìm kiếm cho').should('be.visible');
    cy.contains('.fco-card', 'Pelé').should('be.visible');
  });

  it('filters the database by position', () => {
    cy.contains('span', 'Vị trí:').parent().contains('button', 'GK').click();
    cy.get('.fco-card').should('have.length.greaterThan', 0).each(($card) => {
      cy.wrap($card).should('contain.text', 'GK');
    });
  });

  it('changes sort order', () => {
    cy.get('select').select('name_asc').should('have.value', 'name_asc');
  });

  it('opens and closes player details', () => {
    cy.get('.fco-card').first().click();
    cy.contains('Chi tiết cầu thủ & Bảng giá Live').should('be.visible');
    cy.get('.fixed.inset-0').last().find('button').first().click();
    cy.contains('Chi tiết cầu thủ & Bảng giá Live').should('not.exist');
  });

  it('validates empty Garena login', () => {
    cy.contains('button', 'Đăng Nhập Garena VN').click();
    cy.contains('KẾT NỐI MÁY CHỦ GARENA VIỆT NAM').should('be.visible');
    cy.contains('button', 'Đăng nhập & Tự động kết nối').click();
    cy.contains('Vui lòng nhập tài khoản và mật khẩu Garena!').should('be.visible');
  });

  it('changes formation and keeps the builder slot count', () => {
    cy.contains('button', 'FORMATIONS').click();
    cy.contains('button.formation-option', '4-4-2').click();
    cy.contains('button', 'FORMATIONS 4-4-2').should('be.visible');
    cy.get('button.builder-empty').should('have.length', 11);
  });

  it('assigns and resets a player in the builder', () => {
    cy.get('button.builder-empty').first().click();
    cy.contains('h2', 'CHỌN CẦU THỦ · GK').should('be.visible');
    cy.get('.player-picker button').eq(1).click();
    cy.get('.builder-player-card').should('have.length', 1);
    cy.contains('button', 'Reset').click();
    cy.get('.builder-player-card').should('not.exist');
  });
});
