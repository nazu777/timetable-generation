const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function generateTimetable(payload: Record<string, unknown>) {
  const res = await fetch(`${API_URL}/api/v1/timetables/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`generate failed: ${res.status}`);
  return (await res.json()) as { job_id: string; status: string };
}

export async function getJob(jobId: string) {
  const res = await fetch(`${API_URL}/api/v1/timetables/jobs/${jobId}`);
  if (!res.ok) throw new Error(`job fetch failed: ${res.status}`);
  return await res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API_URL}/health`);
  return res.ok;
}
