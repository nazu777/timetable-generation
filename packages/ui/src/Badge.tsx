interface BadgeProps {
  label: string;
}

export function Badge({ label }: BadgeProps) {
  return <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">{label}</span>;
}
