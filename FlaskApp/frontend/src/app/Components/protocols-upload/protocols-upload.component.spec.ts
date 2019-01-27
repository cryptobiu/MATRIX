import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProtocolsUploadComponent } from './protocols-upload.component';

describe('ProtocolsUploadComponent', () => {
  let component: ProtocolsUploadComponent;
  let fixture: ComponentFixture<ProtocolsUploadComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProtocolsUploadComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProtocolsUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
