export function apiBase() {
  return import.meta.env.VITE_API_URL || "http://localhost:8080";
}

export async function fetchScores(postId) {
  const response = await fetch(
    `${apiBase()}/combined/${encodeURIComponent(postId)}`
  );
  const text = await response.text();
  let payload = null;
  try {
    payload = JSON.parse(text);
  } catch {
    payload = null;
  }
  if (!response.ok) {
    const message =
      payload && payload.error ? payload.error : "The API request failed.";
    throw new Error(message);
  }
  if (!Array.isArray(payload)) {
    throw new Error("The API returned an unexpected response.");
  }
  return payload;
}
