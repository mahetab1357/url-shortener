import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "url-shortener:my-links";

// There's no auth/accounts system in this project, so core-service has no
// concept of "my" URLs - it just stores mappings. We track which links
// this browser has created in localStorage instead. A future improvement
// (real user accounts) would move this server-side.
function readLinks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeLinks(links) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(links));
}

export function useMyLinks() {
  const [links, setLinks] = useState(readLinks);

  useEffect(() => {
    writeLinks(links);
  }, [links]);

  const addLink = useCallback((link) => {
    setLinks((prev) => {
      if (prev.some((existing) => existing.shortCode === link.shortCode)) {
        return prev;
      }
      return [link, ...prev];
    });
  }, []);

  const removeLink = useCallback((shortCode) => {
    setLinks((prev) => prev.filter((link) => link.shortCode !== shortCode));
  }, []);

  return { links, addLink, removeLink };
}
