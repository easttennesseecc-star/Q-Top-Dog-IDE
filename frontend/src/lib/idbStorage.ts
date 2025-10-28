import { get as idbGet, set as idbSet, del as idbDel, keys as idbKeys } from 'idb-keyval';

const BLOB_PREFIX = 'topdog:blob:';

export async function saveBlob(blob: Blob) {
  const id = (typeof crypto !== 'undefined' && (crypto as any).randomUUID) ? (crypto as any).randomUUID() : String(Date.now()) + Math.random().toString(36).slice(2);
  const key = BLOB_PREFIX + id;
  await idbSet(key, blob);
  return id;
}

export async function getBlob(id: string): Promise<Blob | undefined> {
  try {
    return await idbGet(BLOB_PREFIX + id) as Blob | undefined;
  } catch (e) {
    console.warn('idbStorage.getBlob failed', e);
    return undefined;
  }
}

export async function deleteBlob(id: string) {
  try {
    await idbDel(BLOB_PREFIX + id);
  } catch (e) {
    console.warn('idbStorage.deleteBlob failed', e);
  }
}

export async function listBlobIds(): Promise<string[]> {
  try {
    const all = await idbKeys();
    return (all as string[]).filter(k => typeof k === 'string' && k.startsWith(BLOB_PREFIX)).map(k => k.slice(BLOB_PREFIX.length));
  } catch (e) {
    console.warn('idbStorage.listBlobIds failed', e);
    return [];
  }
}

export async function getBlobSize(id: string): Promise<number> {
  try {
    const b = await getBlob(id);
    return b ? b.size : 0;
  } catch (e) {
    return 0;
  }
}

const REGISTRY_KEY = 'topdog:blob_registry';

export function registerBlobId(id: string) {
  try {
    const raw = localStorage.getItem(REGISTRY_KEY);
    const arr = raw ? JSON.parse(raw) as string[] : [];
    if (!arr.includes(id)) {
      arr.push(id);
      localStorage.setItem(REGISTRY_KEY, JSON.stringify(arr));
    }
  } catch (e) { console.warn('registerBlobId failed', e); }
}

export function listRegisteredBlobIds(): string[] {
  try {
    const raw = localStorage.getItem(REGISTRY_KEY);
    return raw ? JSON.parse(raw) as string[] : [];
  } catch (e) { return []; }
}

export async function pruneOrphanedBlobs() {
  // Delete blobs that exist in idb but are not in the registry
  const all = await listBlobIds();
  const reg = new Set(listRegisteredBlobIds());
  const orphans = all.filter(id => !reg.has(id));
  for (const id of orphans) {
    try { await deleteBlob(id); } catch (_) {}
  }
  return orphans;
}

let _pruneInterval: number | null = null;

/**
 * Schedule a periodic prune of orphaned blobs.
 * Runs once immediately and then once per day by default.
 * Returns a cancel function.
 */
export function schedulePrune(opts?: { intervalMs?: number }) {
  try {
    const intervalMs = opts?.intervalMs ?? 1000 * 60 * 60 * 24; // 24h
    // run immediately
    pruneOrphanedBlobs().catch(() => {});
    if (_pruneInterval) window.clearInterval(_pruneInterval);
    _pruneInterval = window.setInterval(() => { pruneOrphanedBlobs().catch(() => {}); }, intervalMs);
    return () => { if (_pruneInterval) { window.clearInterval(_pruneInterval); _pruneInterval = null; } };
  } catch (e) {
    console.warn('schedulePrune failed', e);
    return () => {};
  }
}
