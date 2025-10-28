import { useEffect, useRef, useState } from "react";

type Loaded = {
  kind: "file" | "url";
  name: string;
  type: string;
  size?: number; // bytes
  url: string; // object URL or remote URL
};

function humanSize(b?: number) {
  if (!b && b !== 0) return "";
  const units = ["B", "KB", "MB", "GB"]; let i = 0; let n = b;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(1)} ${units[i]}`;
}

export default function VisualViewer() {
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [desc, setDesc] = useState("");
  const urlInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onOpen = () => urlInputRef.current?.focus();
    const handler = () => onOpen();
    window.addEventListener("open-visual-import", handler as any);
    return () => window.removeEventListener("open-visual-import", handler as any);
  }, []);

  const onFiles = (files: FileList | null) => {
    if (!files || !files[0]) return;
    const f = files[0];
    const url = URL.createObjectURL(f);
    setLoaded({ kind: "file", name: f.name, type: f.type || "", size: f.size, url });
  };

  const onUrl = async (val: string) => {
    const u = val.trim(); if (!u) return;
    let type = ""; let size: number | undefined = undefined;
    try {
      const head = await fetch(u, { method: "HEAD" });
      type = head.headers.get("content-type") || type;
      const cl = head.headers.get("content-length");
      if (cl) size = parseInt(cl, 10);
    } catch {}
    setLoaded({ kind: "url", name: u.split("/").pop() || u, type, size, url: u });
  };

  const isVideo = (t: string) => t.startsWith("video/") || /\.(mp4|webm|mov)$/i.test(loaded?.name || "");
  const isImage = (t: string) => t.startsWith("image/") || /\.(png|jpg|jpeg|gif|webp|svg)$/i.test(loaded?.name || "");

  return (
    <div className="w-full h-full flex flex-col">
      <div className="mb-3 flex items-center gap-2">
        <input
          ref={urlInputRef}
          type="url"
          placeholder="Paste Runway asset URL (or any image/video URL)"
          className="w-full px-3 py-2 rounded-md bg-[#0f1419] border border-cyan-400/20 text-cyan-100 placeholder:text-cyan-400/40"
          onKeyDown={(e) => { if (e.key === "Enter") onUrl((e.target as HTMLInputElement).value); }}
        />
        <label className="px-3 py-2 rounded-md border border-cyan-400/30 hover:border-cyan-400 text-cyan-300 cursor-pointer">
          Import File
          <input type="file" accept="image/*,video/*" className="hidden" onChange={(e) => onFiles(e.target.files)} />
        </label>
      </div>

      <div
        className="flex-1 rounded-xl border border-cyan-400/10 bg-gradient-to-b from-[#0b0f14] to-[#0a0e12] relative overflow-hidden"
      >
        {!loaded ? (
          <div className="absolute inset-0 flex items-center justify-center text-cyan-400/40 select-none">
            Drop or import an image/video to preview • This will be used for backgrounds or build assets
          </div>
        ) : (
          <div className="absolute inset-0 p-2">
            {isVideo(loaded.type) ? (
              <video src={loaded.url} className="w-full h-full object-contain" controls />
            ) : isImage(loaded.type) ? (
              <img src={loaded.url} className="w-full h-full object-contain" alt={loaded.name} />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-cyan-300/60">
                Unsupported type. Try an image or video.
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="rounded-md border border-cyan-400/10 bg-[#0f1419] p-3">
          <div className="text-xs text-cyan-400/60 mb-1">Asset Metadata</div>
          <div className="text-sm text-cyan-200">
            <div>Name: {loaded?.name || "—"}</div>
            <div>Type: {loaded?.type || "—"}</div>
            <div>Size: {loaded?.size ? humanSize(loaded.size) : "—"}</div>
            <div>Source: {loaded?.kind === "url" ? "URL" : loaded ? "Local File" : "—"}</div>
          </div>
        </div>
        <div className="rounded-md border border-cyan-400/10 bg-[#0f1419] p-3">
          <div className="text-xs text-cyan-400/60 mb-1">Describe for Build/Background</div>
          <textarea
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            placeholder="Write a highly detailed description for the assistant to use with this visual (content, style, purpose)."
            className="w-full h-24 rounded-md bg-[#0b1015] border border-cyan-400/20 text-cyan-100 p-2"
          />
        </div>
      </div>
    </div>
  );
}
