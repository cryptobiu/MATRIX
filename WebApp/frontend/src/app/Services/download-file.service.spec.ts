import { TestBed } from '@angular/core/testing';

import { DownloadFileService } from './download-file.service';

describe('DownloadFileService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: DownloadFileService = TestBed.get(DownloadFileService);
    expect(service).toBeTruthy();
  });
});
