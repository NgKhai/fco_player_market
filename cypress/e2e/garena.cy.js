describe('Garena market integration API', () => {
  it('reports a disconnected state without exposing credentials', () => {
    cy.request('/api/garena/status').then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.deep.include({ status: 'success', connected: false });
      expect(response.body).not.to.have.any.keys('token', 'password');
    });
  });

  it('rejects an empty manual token', () => {
    cy.request({
      method: 'POST',
      url: '/api/garena/token',
      body: { token: '   ' },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(422);
      expect(response.body.status).to.eq('error');
    });
  });

  it('rejects login when username or password is missing', () => {
    cy.request({
      method: 'POST',
      url: '/api/garena/login',
      body: { username: '', password: '' },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(422);
      expect(response.body.status).to.eq('error');
    });
  });

  it('logs out without returning a token', () => {
    cy.request({ method: 'POST', url: '/api/garena/logout' }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.deep.include({ status: 'success', connected: false });
      expect(response.body).not.to.have.any.keys('token', 'password');
    });
  });

  it('shows a validation error when saving an invalid token', () => {
    cy.intercept('GET', '**/api/garena/status', {
      statusCode: 200,
      body: { status: 'success', connected: false },
    });
    cy.intercept('GET', '**/api/players/search*', {
      statusCode: 200,
      body: { status: 'success', total: 0, data: [] },
    });
    cy.intercept('POST', '**/api/garena/token', (request) => {
      expect(request.body.uid).to.eq('123');
      request.reply({
        statusCode: 422,
        body: { status: 'error', message: 'Token Garena không hợp lệ.' },
      });
    }).as('invalidToken');
    cy.visit('/?builder=1');
    cy.contains('button', 'Đăng Nhập Garena VN').click();
    cy.contains('button', 'Dán Token Trực tiếp').click();
    cy.get('input[placeholder^="Dán sso_token"]').type('invalid-token');
    cy.get('input[placeholder^="Nhập UID"]').type('123');
    cy.contains('button', 'Lưu Token').click();
    cy.wait('@invalidToken');
    cy.contains('.fixed.inset-0', 'Token Garena không hợp lệ.').should('be.visible');
  });
});
