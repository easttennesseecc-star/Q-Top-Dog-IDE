const { registerBlobId, listRegisteredBlobIds } = require('../idbStorage');

describe('idbRegistry (localStorage-backed)', () => {
  beforeEach(() => { localStorage.clear(); });
  afterEach(() => { localStorage.clear(); });

  test('registers and lists blob ids', () => {
    registerBlobId('abc123');
    registerBlobId('xyz');
    registerBlobId('abc123'); // duplicate shouldn't duplicate
    const all = listRegisteredBlobIds();
    expect(all).toContain('abc123');
    expect(all).toContain('xyz');
    expect(all.length).toBe(2);
  });
});
