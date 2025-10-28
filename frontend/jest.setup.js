require('@testing-library/jest-dom');

// Provide a simple global fetch mock for tests to avoid ReferenceError in jsdom.
// Individual tests can override this mock when they need specific behavior.
if (typeof global.fetch === 'undefined') {
	global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => ({}) }));
}
