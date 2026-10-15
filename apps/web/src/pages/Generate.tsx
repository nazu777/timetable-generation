import { useState } from 'react';
import { generateTimetable, getJob } from '../lib/api';

export default function Generate() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');

  async function run() {
    setStatus('queued');
    const job = await generateTimetable({ name: 'demo', time_limit_seconds: 10 });
    setJobId(job.job_id);
    const t = setInterval(async () => {
      const j = await getJob(job.job_id);
      setStatus(j.status);
      if (j.status === 'succeeded' || j.status === 'failed') clearInterval(t);
    }, 2000);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Generate</h1>
      <button onClick={run} className="bg-blue-600 text-white px-4 py-2 rounded">
        Run solver
      </button>
      <p className="mt-2 text-sm">Job: {jobId ?? '—'} · Status: {status}</p>
    </div>
  );
}
