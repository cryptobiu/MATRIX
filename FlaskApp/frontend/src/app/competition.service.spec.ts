import { TestBed } from '@angular/core/testing';

import { CompetitionService } from './competition.service';

describe('CompetitionService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CompetitionService = TestBed.get(CompetitionService);
    expect(service).toBeTruthy();
  });
});
