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
});
