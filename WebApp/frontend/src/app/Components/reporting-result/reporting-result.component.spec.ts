import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportingResultComponent } from './reporting-result.component';

describe('ReportingResultComponent', () => {
  let component: ReportingResultComponent;
  let fixture: ComponentFixture<ReportingResultComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReportingResultComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReportingResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
