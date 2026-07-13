import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { beforeEach, describe, expect, it } from 'vitest';
import { environment } from '../../../environments/environment';
import { ApiaryMember } from '../models/apiary.models';
import { ApiaryService } from './apiary.service';

describe('ApiaryService team management', () => {
  let service: ApiaryService;
  let http: HttpTestingController;

  const member: ApiaryMember = {
    id: 7,
    apiary_id: 3,
    user_id: 12,
    role: 'member',
    invited_by_user_id: 1,
    accepted_at: null,
    created_at: '2026-07-13T10:00:00Z',
    user: { id: 12, username: 'beekeeper', email: 'bee@example.com' },
    apiary: { id: 3, stock_number: 'S-003', name: 'Orchard' }
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(ApiaryService);
    http = TestBed.inject(HttpTestingController);
  });

  it('loads pending invitations', () => {
    service.getInvitations().subscribe(result => expect(result).toEqual([member]));

    const request = http.expectOne(`${environment.apiUrl}/api/apiaries/invitations`);
    expect(request.request.method).toBe('GET');
    request.flush([member]);
    http.verify();
  });

  it('invites a team member with the selected role', () => {
    service.inviteMember(3, 'bee@example.com', 'admin').subscribe(result => expect(result).toEqual(member));

    const request = http.expectOne(`${environment.apiUrl}/api/apiaries/3/members`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ username_or_email: 'bee@example.com', role: 'admin' });
    request.flush(member);
    http.verify();
  });

  it('accepts and declines invitations through their dedicated endpoints', () => {
    service.acceptInvitation(7).subscribe(result => expect(result).toEqual(member));
    const acceptRequest = http.expectOne(`${environment.apiUrl}/api/apiaries/invitations/7/accept`);
    expect(acceptRequest.request.method).toBe('POST');
    acceptRequest.flush(member);

    service.declineInvitation(8).subscribe();
    const declineRequest = http.expectOne(`${environment.apiUrl}/api/apiaries/invitations/8`);
    expect(declineRequest.request.method).toBe('DELETE');
    declineRequest.flush(null);
    http.verify();
  });
});
