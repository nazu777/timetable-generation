// Shared contracts — must mirror apps/api/app/schemas/*.py
export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed';

export interface Assignment {
  batch_id: string;
  subject_id: string;
  teacher_id: string;
  room_id: string;
  timeslot_id: string;
}

export interface GenerateRequest {
  name: string;
  time_limit_seconds: number;
  teacher_ids: string[];
  batch_ids: string[];
  room_ids: string[];
  subject_ids: string[];
  timeslot_ids: string[];
}

export interface JobPollResponse {
  job_id: string;
  status: JobStatus;
  score?: number | null;
  assignments?: Assignment[] | null;
  violations?: string[] | null;
  error?: string | null;
}
