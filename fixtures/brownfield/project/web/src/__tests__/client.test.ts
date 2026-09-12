import { fetchQuote } from '../api/client';
// stale: uses an old API path
export const expectation = fetchQuote('B').then((s) => s === 'GET /quotes/B');
