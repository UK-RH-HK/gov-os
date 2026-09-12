import { get } from '../util/http';
export async function fetchRun(name: string): Promise<string> { return get(`/run/${name}`); }
