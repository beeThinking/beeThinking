export interface CalendarExportEvent {
  uid: string;
  title: string;
  description?: string | null;
  location?: string | null;
  start: string;
  end?: string | null;
  completed?: boolean;
}

export function createICalendar(events: CalendarExportEvent[], generatedAt = new Date()): string {
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//BeeThinking//Apiary Calendar//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH'
  ];

  for (const event of events) {
    lines.push('BEGIN:VEVENT');
    lines.push(`UID:${escapeText(event.uid)}`);
    lines.push(`DTSTAMP:${utcDateTime(generatedAt)}`);
    if (event.start.includes('T')) {
      lines.push(`DTSTART:${utcDateTime(new Date(event.start))}`);
      if (event.end) lines.push(`DTEND:${utcDateTime(new Date(event.end))}`);
    } else {
      lines.push(`DTSTART;VALUE=DATE:${compactDate(event.start)}`);
      lines.push(`DTEND;VALUE=DATE:${compactDate(nextDay(event.start))}`);
    }
    lines.push(`SUMMARY:${escapeText(event.title)}`);
    if (event.description) lines.push(`DESCRIPTION:${escapeText(event.description)}`);
    if (event.location) lines.push(`LOCATION:${escapeText(event.location)}`);
    lines.push(`STATUS:${event.completed ? 'COMPLETED' : 'CONFIRMED'}`);
    lines.push('END:VEVENT');
  }

  lines.push('END:VCALENDAR');
  return `${lines.flatMap(foldLine).join('\r\n')}\r\n`;
}

function escapeText(value: string): string {
  return value
    .replaceAll('\\', '\\\\')
    .replace(/\r?\n/g, '\\n')
    .replaceAll(',', '\\,')
    .replaceAll(';', '\\;');
}

function utcDateTime(value: Date): string {
  return value.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
}

function compactDate(value: string): string {
  return value.slice(0, 10).replaceAll('-', '');
}

function nextDay(value: string): string {
  const date = new Date(`${value.slice(0, 10)}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + 1);
  return date.toISOString().slice(0, 10);
}

function foldLine(line: string): string[] {
  const folded: string[] = [];
  let rest = line;
  while (rest.length > 73) {
    folded.push(rest.slice(0, 73));
    rest = ` ${rest.slice(73)}`;
  }
  folded.push(rest);
  return folded;
}
