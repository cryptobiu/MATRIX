import { TestBed } from '@angular/core/testing';

import { FormSubmissionService } from './formSubmission.service';

describe('EnrollmentService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: FormSubmissionService = TestBed.get(FormSubmissionService);
    expect(service).toBeTruthy();
  });
});
