import { get } from '../util/http';
export async function fetchQuote(zone: string): Promise<string> { return get(`/quote/${zone}`); }
