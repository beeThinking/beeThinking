import { describe, expect, it } from 'vitest';
import { createICalendar } from './calendar.utils';

describe('createICalendar', () => {
  const generatedAt = new Date('2026-07-13T12:00:00Z');

  it('exports timed events in UTC', () => {
    const calendar = createICalendar([{
      uid: 'appointment-1@beethinking',
      title: 'Apiary visit',
      start: '2026-07-20T10:00:00+02:00',
      end: '2026-07-20T11:30:00+02:00'
    }], generatedAt);

    expect(calendar).toContain('DTSTART:20260720T080000Z');
    expect(calendar).toContain('DTEND:20260720T093000Z');
    expect(calendar).toContain('DTSTAMP:20260713T120000Z');
  });

  it('escapes calendar text fields', () => {
    const calendar = createICalendar([{
      uid: 'appointment-2@beethinking',
      title: 'Check honey, feed; supers',
      description: 'Line one\nLine two',
      location: 'Garden, north',
      start: '2026-07-20'
    }], generatedAt);

    expect(calendar).toContain('SUMMARY:Check honey\\, feed\\; supers');
    expect(calendar).toContain('DESCRIPTION:Line one\\nLine two');
    expect(calendar).toContain('LOCATION:Garden\\, north');
  });

  it('exports due-date appointments as full-day events', () => {
    const calendar = createICalendar([{
      uid: 'appointment-3@beethinking',
      title: 'Deadline',
      start: '2026-07-20'
    }], generatedAt);

    expect(calendar).toContain('DTSTART;VALUE=DATE:20260720');
    expect(calendar).toContain('DTEND;VALUE=DATE:20260721');
    expect(calendar.endsWith('\r\n')).toBe(true);
  });
});
